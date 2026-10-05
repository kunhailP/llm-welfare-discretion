"""Design-B pilot runner: rule packet + case file + question -> P(YES), P(NO) from the first answer token.

YES and NO are single tokens for the models used here (checked at startup; the run aborts otherwise),
so the first-token log-probability IS the full-label sequence log-probability. Generation mode keeps
vLLM prefix caching on, so the shared rule packet is computed once.

Two answer orders per item (YES listed first / NO listed first). Thinking is off (Qwen3).

Usage:
  python src/run/run_rules_pilot.py --model qwen3-8b --data data/rules_pilot/pilot.jsonl \
      --out results/rules_pilot/qwen3-8b.jsonl
"""
import argparse, json, os, time

import yaml

ROOT = os.environ.get("WN_ROOT", "/workspace/welfare-need-naacl")
os.environ.setdefault("HF_HOME", "/workspace/hf")

QUESTIONS = {
    "gross": "Does this household pass the gross income test (Step 2)?",
    "elig": "Is this household income-eligible for SNAP under these rules (Step 8)?",
    "abawd": "Under the ABAWD time limit, can {name} receive SNAP benefits in the determination month named in the case file?",
}
ORDERS = {"yesfirst": "Answer with exactly one word: YES or NO.",
          "nofirst": "Answer with exactly one word: NO or YES."}


def build_prompt(packet, r, order):
    name = r["text"].split("applicant: ")[1].split("\n")[0] if "applicant: " in r["text"] \
        else r["text"].split("note on ")[1].split("'s application")[0]
    q = QUESTIONS[r["task"]].format(name=name)
    return f"{packet}\n\n=== CASE FILE ===\n{r['text']}\n\n=== QUESTION ===\n{q}\n{ORDERS[order]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--packet", default="configs/rule_packet_fy2026.md")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    from vllm import LLM, SamplingParams

    cfg = {m["id"]: m for m in yaml.safe_load(open(f"{ROOT}/configs/models.yaml"))["models"]}[a.model]
    kw = dict(model=cfg["repo"], revision=cfg["revision"], max_model_len=4096, gpu_memory_utilization=0.85,
              seed=0, enable_prefix_caching=True)
    if cfg["repo"].startswith("mistralai/"):
        kw.update(tokenizer_mode="mistral", config_format="mistral", load_format="mistral")
    llm = LLM(**kw)
    tok = llm.get_tokenizer()
    ids = {lab: list(tok.encode(lab, add_special_tokens=False)) for lab in ("YES", "NO")}
    assert all(len(v) == 1 for v in ids.values()), f"labels not single tokens: {ids}"
    yes_id, no_id = ids["YES"][0], ids["NO"][0]

    chat_kw = dict(add_generation_prompt=True)
    if "qwen" in a.model:
        chat_kw["chat_template_kwargs"] = {"enable_thinking": False}
    packet = open(f"{ROOT}/{a.packet}").read().strip()
    rows = [json.loads(l) for l in open(a.data)][: a.limit]
    jobs, convs = [], []
    for r in rows:
        for order in ORDERS:
            jobs.append((r["item_id"], order))
            convs.append([{"role": "user", "content": build_prompt(packet, r, order)}])
    sp = SamplingParams(temperature=0.0, max_tokens=1, logprobs=20)
    t0 = time.time()
    outs = llm.chat(convs, sp, use_tqdm=True, **chat_kw)
    dt = time.time() - t0
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        for (iid, order), o in zip(jobs, outs):
            top = o.outputs[0].logprobs[0]
            lp = lambda t: top[t].logprob if t in top else None
            f.write(json.dumps(dict(model=a.model, item_id=iid, order=order, lp_yes=lp(yes_id), lp_no=lp(no_id),
                                    greedy=o.outputs[0].text)) + "\n")
    import platform, torch, transformers, vllm
    meta = dict(model=a.model, repo=cfg["repo"], revision=cfg["revision"], vllm=vllm.__version__,
                transformers=transformers.__version__, torch=torch.__version__, python=platform.python_version(),
                packet=a.packet, label_token_ids=ids, chat_kwargs=chat_kw, n=len(jobs), seconds=round(dt, 1),
                example_prompt=convs[0][0]["content"], data=a.data)
    json.dump(meta, open(a.out + ".meta.json", "w"))
    print(json.dumps({k: v for k, v in meta.items() if k != "example_prompt"}))


if __name__ == "__main__":
    main()
