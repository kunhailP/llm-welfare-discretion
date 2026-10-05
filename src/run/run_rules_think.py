"""Design-B thinking-mode subsample (2026-10-05): does the model compute the rules when it can reason,
and do deservingness cues still move the verdict there?

Subsample (narrative style only; every cue of a group kept, so hi-lo contrasts stay paired):
  elig: all 74 groups; gross: 15 groups per margin (60); ABAWD: 15 groups per status x hours cell (150).
Answer order alternates by group (all cues of a group share one order). Qwen3 thinking on,
recommended thinking sampling (T=0.6, top_p=0.95, top_k=20), seed fixed. Final verdict = last
"ANSWER: YES|NO" after </think>; no </think> -> TRUNCATED, no parseable answer -> INVALID.

Usage: python src/run/run_rules_think.py --model qwen3-14b --out results/rules_think/qwen3-14b.jsonl
"""
import argparse, json, os, random, re, sys, time
from collections import defaultdict

import yaml

ROOT = os.environ.get("WN_ROOT", "/workspace/welfare-need-naacl")
os.environ.setdefault("HF_HOME", "/workspace/hf")
sys.path.insert(0, f"{ROOT}/src/run")
from run_rules_pilot import QUESTIONS  # noqa: E402

ORDERS = {"yesfirst": "Reason through the rules step by step. End with a final line of exactly the form ANSWER: YES or ANSWER: NO.",
          "nofirst": "Reason through the rules step by step. End with a final line of exactly the form ANSWER: NO or ANSWER: YES."}
ORDERS3 = {"yesfirst": "Reason through the rules step by step. End with a final line of exactly the form ANSWER: YES or ANSWER: NO or ANSWER: REQUEST.",
           "nofirst": "Reason through the rules step by step. End with a final line of exactly the form ANSWER: NO or ANSWER: YES or ANSWER: REQUEST."}
PER_CELL = {"gross": 15, "abawd": 15}


def group_key(r):
    return r["item_id"].replace("_" + r["cue"] + "_", "_CUE_")


def subsample(rows, seed=0):
    groups = defaultdict(list)
    for r in rows:
        if r["style"] == "narrative":
            groups[group_key(r)].append(r)
    cells = defaultdict(list)
    for g, rs in sorted(groups.items()):
        r = rs[0]
        cell = (r["task"], r["margin"]) if r["task"] != "abawd" else (r["task"], r["status"], r["hours"])
        cells[cell].append(g)
    rng = random.Random(seed)
    keep = []
    for cell, gs in sorted(cells.items(), key=lambda kv: str(kv[0])):
        k = PER_CELL.get(cell[0])
        keep += gs if k is None else rng.sample(gs, min(k, len(gs)))
    out = []
    for i, g in enumerate(sorted(keep)):
        order = "yesfirst" if i % 2 == 0 else "nofirst"
        out += [(r, order) for r in sorted(groups[g], key=lambda r: r["cue"])]
    return out


def build_prompt(packet, r, order):
    name = r["text"].split("applicant: ")[1].split("\n")[0] if "applicant: " in r["text"] \
        else r["text"].split("note on ")[1].split("'s application")[0]
    q = r["question"] if "question" in r else QUESTIONS[r["task"]].format(name=name)
    if r.get("packet_extra"):
        packet = f"{packet}\n\n{r['packet_extra']}"
    return f"{packet}\n\n=== CASE FILE ===\n{r['text']}\n\n=== QUESTION ===\n{q}\n{(ORDERS3 if r.get('answer_set') == 'ynr' else ORDERS)[order]}"


def parse(text, thinking=True):
    if not thinking:   # same prompt, Qwen3 thinking switch off: the whole output is the visible reasoning + answer
        m = re.findall(r"ANSWER:\s*\**\s*(YES|NO|REQUEST)\b", text, flags=re.I)
        return (m[-1].upper() if m else "INVALID"), "", text
    for sep in ("</think>", "<|channel|>final<|message|>", "assistantfinal"):   # Qwen3 / gpt-oss raw / gpt-oss decoded
        if sep in text:
            think, ans = text.split(sep, 1)
            break
    else:
        return "TRUNCATED", text, ""
    m = re.findall(r"ANSWER:\s*\**\s*(YES|NO|REQUEST)\b", ans, flags=re.I)
    return (m[-1].upper() if m else "INVALID"), think, ans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", default="data/rules_pilot/pilot.jsonl")
    ap.add_argument("--packet", default="configs/rule_packet_fy2026.md")
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--thinking", choices=["on", "off"], default="on",
                    help="Qwen3 only: off = same step-by-step prompt and parser, thinking switch off (protocol ladder)")
    ap.add_argument("--reasoning-effort", default="medium", help="gpt-oss only")
    ap.add_argument("--seed", type=int, default=0, help="sampling seed (seed baseline for thinking runs)")
    ap.add_argument("--no-subsample", action="store_true", help="run every row of --data; order alternates by base")
    a = ap.parse_args()
    assert "qwen" in a.model or "gpt-oss" in a.model, "thinking implemented for Qwen3 and gpt-oss only"
    from vllm import LLM, SamplingParams

    cfg = {m["id"]: m for m in yaml.safe_load(open(f"{ROOT}/configs/models.yaml"))["models"]}[a.model]
    llm = LLM(model=cfg["repo"], revision=cfg["revision"], max_model_len=a.max_tokens + 4096,
              gpu_memory_utilization=0.90, seed=0, enable_prefix_caching=True)
    tmpl = {"enable_thinking": a.thinking == "on"} if "qwen" in a.model else {"reasoning_effort": a.reasoning_effort}
    chat_kw = dict(add_generation_prompt=True, chat_template_kwargs=tmpl)
    packet = open(f"{ROOT}/{a.packet}").read().strip()
    rows = [json.loads(l) for l in open(f"{ROOT}/{a.data}")]
    if a.no_subsample:
        jobs = [(r, "yesfirst" if int(r["base"][1:]) % 2 == 0 else "nofirst") for r in rows][: a.limit]
    else:
        jobs = subsample(rows)[: a.limit]
    convs = [[{"role": "user", "content": build_prompt(packet, r, o)}] for r, o in jobs]
    if "gpt-oss" in a.model:   # OpenAI's recommended sampling for gpt-oss
        sp = SamplingParams(temperature=1.0, top_p=1.0, max_tokens=a.max_tokens, seed=a.seed)
    else:                      # Qwen3 thinking-mode recommendation
        sp = SamplingParams(temperature=0.6, top_p=0.95, top_k=20, max_tokens=a.max_tokens, seed=a.seed)
    t0 = time.time()
    outs = llm.chat(convs, sp, use_tqdm=True, **chat_kw)
    dt = time.time() - t0
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        for (r, order), o in zip(jobs, outs):
            text = o.outputs[0].text
            verdict, think, ans = parse(text, thinking=not ("qwen" in a.model and a.thinking == "off"))
            f.write(json.dumps(dict(model=a.model, item_id=r["item_id"], order=order, verdict=verdict,
                                    n_tokens=len(o.outputs[0].token_ids), finish=o.outputs[0].finish_reason,
                                    think=think, answer=ans)) + "\n")
    import platform, torch, transformers, vllm
    meta = dict(model=a.model, repo=cfg["repo"], revision=cfg["revision"], vllm=vllm.__version__,
                transformers=transformers.__version__, torch=torch.__version__, python=platform.python_version(),
                packet=a.packet, chat_kwargs=chat_kw, sampling=repr(sp), thinking=a.thinking, seed=a.seed, n=len(jobs), seconds=round(dt, 1),
                example_prompt=convs[0][0]["content"], data=a.data)
    json.dump(meta, open(a.out + ".meta.json", "w"))
    print(json.dumps({k: v for k, v in meta.items() if k != "example_prompt"}))


if __name__ == "__main__":
    main()
