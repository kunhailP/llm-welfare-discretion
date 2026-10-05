"""Sequence-level label scoring: log P(full label string | prompt) for every candidate label.

Fixes the first-token readout, where SHORTFALL/SUFFICIENT can share a first token ("S").
For each (item, query, label) the conversation is rendered with the label as the start of the
assistant turn (continue_final_message=True) and vLLM returns prompt log-probabilities; the label's
score is the summed log-prob of its tokens. Label token count = len(with label) - len(empty assistant turn).

Usage:
  python src/run/score_labels_vllm.py --model qwen3-8b \
    --spec "data/diagnostic/oracle_ladder.jsonl|q1_yesno,q1_direct,q1_direct_rev|results/diagnostic_seq/qwen3-8b.jsonl"
"""
import argparse
import json
import os
import time

import yaml

ROOT = "/workspace/welfare-need-naacl"
os.environ.setdefault("HF_HOME", "/workspace/hf")
CANDIDATES = {
    "q1_yesno": ["YES", "NO", "UNKNOWN"],
    "q1_direct": ["SHORTFALL", "SUFFICIENT", "UNKNOWN"],
    "q1_direct_rev": ["SHORTFALL", "SUFFICIENT", "UNKNOWN"],
    "q2_definition": ["SHORTFALL", "SUFFICIENT", "UNKNOWN"],
    "q1_yesno_rev": ["YES", "NO", "UNKNOWN"],
    "q1_ab": ["A", "B", "C"],
    "q1_ab_rev": ["A", "B", "C"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--spec", action="append", required=True)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    from vllm import LLM, SamplingParams

    cfg = {m["id"]: m for m in yaml.safe_load(open(f"{ROOT}/configs/models.yaml"))["models"]}[a.model]
    prompts = yaml.safe_load(open(f"{ROOT}/configs/prompts.yaml"))
    kw = dict(model=cfg["repo"], revision=cfg["revision"], max_model_len=4096, gpu_memory_utilization=0.85, seed=0)
    if cfg["repo"].startswith("mistralai/"):
        kw.update(tokenizer_mode="mistral", config_format="mistral", load_format="mistral")
    llm = LLM(**kw)
    chat_kw = dict(add_generation_prompt=False, continue_final_message=True)
    if "qwen" in a.model:
        chat_kw["chat_template_kwargs"] = {"enable_thinking": False}
    sp = SamplingParams(temperature=0.0, max_tokens=1, prompt_logprobs=0)

    # Mistral's tokenizer rejects an empty assistant prefix -> use direct label encoding instead.
    use_ref = not cfg["repo"].startswith("mistralai/")
    tok = llm.get_tokenizer()
    lab_ids = {}
    if not use_ref:
        for labs in CANDIDATES.values():
            for lab in labs:
                lab_ids[lab] = list(tok.encode(lab, add_special_tokens=False))
    specs = [x.split("|") for x in a.spec]
    jobs, convs = [], []
    for data, qs, out in specs:
        for r in [json.loads(l) for l in open(data)][: a.limit]:
            for q in qs.split(","):
                user = {"role": "user", "content": prompts[q].format(text=r["text"])}
                for lab in ([""] if use_ref else []) + CANDIDATES[q]:  # "" = prefix length reference
                    jobs.append((r["profile_id"], q, lab, out))
                    convs.append([user, {"role": "assistant", "content": lab}])

    t0 = time.time()
    outs = llm.chat(convs, sp, use_tqdm=True, **chat_kw)
    dt = time.time() - t0

    # group: (pid, q, out) -> {label: (n_prompt_tokens, logprob list)}
    groups = {}
    for (pid, q, lab, out), o in zip(jobs, outs):
        lps = [0.0 if d is None else next(iter(d.values())).logprob for d in o.prompt_logprobs]
        groups.setdefault((pid, q, out), {})[lab] = (len(o.prompt_token_ids), lps, o.prompt_token_ids)
    files = {out: open(out, "w") for _, _, out in specs if not os.makedirs(os.path.dirname(out), exist_ok=True)}
    bad = 0
    for (pid, q, out), d in groups.items():
        scores = {}
        for lab in CANDIDATES[q]:
            n, lps, ids = d[lab]
            if use_ref:
                n0, _, ids0 = d[""]
                ok = n - n0 > 0 and ids[:n0] == ids0
            else:
                li = lab_ids[lab]
                n0 = n - len(li)
                ok = len(li) > 0 and list(ids[n0:]) == li
            if not ok:
                bad += 1  # template does not keep the prefix stable; flag, do not guess
                scores[lab] = None
            else:
                scores[lab] = sum(lps[n0:])
        files[out].write(json.dumps(dict(model=a.model, revision=cfg["revision"], query=q, profile_id=pid,
                                         label_logprob=scores)) + "\n")
    for f in files.values():
        f.close()
    meta = dict(model=a.model, n_sequences=len(jobs), seconds=round(dt, 1), prefix_mismatch=bad, specs=specs)
    print(json.dumps(meta))
    for _, _, out in specs:
        json.dump(meta, open(out + ".meta.json", "w"))


if __name__ == "__main__":
    main()
