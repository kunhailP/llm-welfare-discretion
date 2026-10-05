"""v2 wording probe (2026-10-05): why do 8B models answer "cannot pay" on v2 SUFFICIENT items at +40% surplus
when v1 yes/no was ~100% at L0? Two differences between v1 and v2 are crossed:
  question: v1 person wording ("can {first} pay their essential bills") vs v2 subject-neutral passive wording
  filler:   v2 text with the four context sentences vs money_text only
Items: v2 dev, contexts none + unemp_status, gaps -0.20/-0.05/+0.05/+0.20/+0.40, all 20 bases (person task).
YES/NO first-token log-probs, both answer orders, thinking off.

Usage: python src/run/run_v2_wording_probe.py --model qwen3-8b --out results/v2/wording_probe/qwen3-8b.jsonl
"""
import argparse, json, os, time

import yaml

ROOT = os.environ.get("WN_ROOT", "/workspace/welfare-need-naacl")
os.environ.setdefault("HF_HOME", "/workspace/hf")

Q = {
    "v1_person": "Question: Using only the money {first} can access before the bills are due, can {first} pay "
                 "{poss} essential bills in full by the deadline?",
    "v2_passive": "Question: Using only the money that can be accessed before the bills are due, can the essential "
                  "bills described in the case be paid in full by the deadline?",
}
ORDERS = {"yesfirst": "Answer with exactly one word: YES, NO, or UNKNOWN.",
          "nofirst": "Answer with exactly one word: NO, YES, or UNKNOWN."}
GAPS = {-0.2, -0.05, 0.05, 0.2, 0.4}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", default="data/controlled_v2/dev.jsonl")
    a = ap.parse_args()
    from vllm import LLM, SamplingParams

    cfg = {m["id"]: m for m in yaml.safe_load(open(f"{ROOT}/configs/models.yaml"))["models"]}[a.model]
    kw = dict(model=cfg["repo"], revision=cfg["revision"], max_model_len=2048, gpu_memory_utilization=0.85, seed=0)
    if cfg["repo"].startswith("mistralai/"):
        kw.update(tokenizer_mode="mistral", config_format="mistral", load_format="mistral")
    llm = LLM(**kw)
    tok = llm.get_tokenizer()
    ids = {lab: list(tok.encode(lab, add_special_tokens=False)) for lab in ("YES", "NO", "UNKNOWN")}
    assert all(len(ids[l]) == 1 for l in ("YES", "NO")), f"labels not single tokens: {ids}"
    chat_kw = dict(add_generation_prompt=True)
    if "qwen" in a.model:
        chat_kw["chat_template_kwargs"] = {"enable_thinking": False}

    rows = [json.loads(l) for l in open(f"{ROOT}/{a.data}")]
    rows = [r for r in rows if r["task"] == "person" and r["context"] in ("none", "unemp_status")
            and round(r["gap_frac"], 2) in GAPS]
    jobs, convs = [], []
    for r in rows:
        first = r["subject"].split()[0]
        for filler, text in (("filler", r["text"]), ("nofiller", r["money_text"])):
            for qk, qt in Q.items():
                for order, ot in ORDERS.items():
                    q = qt.format(first=first, poss="their")
                    jobs.append(dict(profile_id=r["profile_id"], context=r["context"], gap_frac=r["gap_frac"],
                                     gold=r["gold"], filler=filler, question=qk, order=order))
                    convs.append([{"role": "user", "content": f"Read the case below.\n\n{text}\n\n{q}\n{ot}"}])
    sp = SamplingParams(temperature=0.0, max_tokens=1, logprobs=20)
    t0 = time.time()
    outs = llm.chat(convs, sp, use_tqdm=True, **chat_kw)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        for j, o in zip(jobs, outs):
            top = o.outputs[0].logprobs[0]
            j.update(model=a.model, greedy=o.outputs[0].text,
                     **{f"lp_{l.lower()}": (top[i[0]].logprob if i[0] in top else None) for l, i in ids.items()})
            f.write(json.dumps(j) + "\n")
    json.dump(dict(model=a.model, revision=cfg["revision"], n=len(jobs), seconds=round(time.time() - t0, 1),
                   label_ids=ids, chat_kwargs=chat_kw, example_prompt=convs[0][0]["content"]),
              open(a.out + ".meta.json", "w"))


if __name__ == "__main__":
    main()
