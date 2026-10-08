"""Frontier-model replicate of the thinking subsample through APIs (Paper 1, 2026-10-08).

Same 1,554 items, same prompt and answer-order assignment as src/run/run_rules_think.py (its subsample() and
build_prompt() are imported), same parser, same output row format, so src/eval/score_rules_think.py scores the file
unchanged. Providers: Anthropic (anthropic SDK; adaptive thinking, summarized display, effort high) and OpenAI
(openai SDK; reasoning effort medium). Resumable: rows already in --out are skipped. No model fallback is used: a
refusal is recorded as verdict REFUSAL so every row comes from the named model.

Usage: python src/run/run_rules_api.py --model claude-opus-5-5 --out results/rules_think/claude-opus-5-5.jsonl
       python src/run/run_rules_api.py --model gpt-5 --out results/rules_think/gpt-5.jsonl
Credentials: ANTHROPIC_API_KEY / OPENAI_API_KEY in the environment.
"""
import argparse, json, os, pathlib, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.environ.get("WN_ROOT", str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, f"{ROOT}/src/run")
from run_rules_think import subsample, build_prompt, parse  # noqa: E402

PROVIDER = {"claude": "anthropic", "gpt": "openai", "o1": "openai", "o3": "openai", "o4": "openai"}


def call_anthropic(client, model, prompt, max_tokens):
    r = client.messages.create(model=model, max_tokens=max_tokens,
                               thinking={"type": "adaptive", "display": "summarized"},
                               output_config={"effort": "high"},
                               messages=[{"role": "user", "content": prompt}])
    think = "\n".join(b.thinking for b in r.content if b.type == "thinking" and getattr(b, "thinking", ""))
    text = "\n".join(b.text for b in r.content if b.type == "text")
    finish = r.stop_reason
    return text, think, finish, r.usage.output_tokens


def call_openai(client, model, prompt, max_tokens):
    r = client.responses.create(model=model, input=prompt, reasoning={"effort": "medium"},
                                max_output_tokens=max_tokens)
    text = r.output_text
    finish = getattr(r, "status", "completed")
    if getattr(r, "incomplete_details", None):
        finish = "length"
    usage = getattr(r, "usage", None)
    n = getattr(usage, "output_tokens", 0) if usage else 0
    return text, "", finish, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", default="data/rules_pilot/pilot.jsonl")
    ap.add_argument("--packet", default="configs/rule_packet_fy2026.md")
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    provider = next((p for k, p in PROVIDER.items() if a.model.startswith(k)), None)
    assert provider, "model must start with claude / gpt / o1 / o3 / o4"
    packet = open(f"{ROOT}/{a.packet}").read().strip()
    rows = [json.loads(l) for l in open(f"{ROOT}/{a.data}")]
    jobs = subsample(rows)[: a.limit]
    out = pathlib.Path(a.out if os.path.isabs(a.out) else f"{ROOT}/{a.out}")
    done = set()
    if out.exists():
        done = {json.loads(l)["item_id"] for l in open(out)}
    pending = [(r, o) for r, o in jobs if r["item_id"] not in done]
    print(json.dumps(dict(model=a.model, provider=provider, n_items=len(jobs), done=len(done), pending=len(pending))))
    if a.dry_run:
        print(build_prompt(packet, *pending[0]))
        return
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(max_retries=5)
        call = call_anthropic
    else:
        import openai
        client = openai.OpenAI(max_retries=5)
        call = call_openai
    out.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    t0 = time.time()

    def one(r, order):
        prompt = build_prompt(packet, r, order)
        try:
            text, think, finish, n = call(client, a.model, prompt, a.max_tokens)
        except Exception as e:   # recorded, not retried beyond the SDK's own retries
            return dict(model=a.model, item_id=r["item_id"], order=order, verdict="ERROR", n_tokens=0,
                        finish=f"error: {type(e).__name__}: {str(e)[:200]}", think="", answer="")
        verdict, _, _ = parse(text, thinking=False)
        if finish == "refusal":
            verdict = "REFUSAL"
        elif finish in ("max_tokens", "length"):
            verdict = "TRUNCATED"
        return dict(model=a.model, item_id=r["item_id"], order=order, verdict=verdict, n_tokens=n,
                    finish=finish, think=think, answer=text)

    n_written = 0
    with open(out, "a") as f, ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(one, r, o) for r, o in pending]
        for fut in as_completed(futs):
            row = fut.result()
            with lock:
                f.write(json.dumps(row) + "\n"); f.flush()
                n_written += 1
                if n_written % 50 == 0:
                    print(json.dumps(dict(written=n_written, pending=len(pending), seconds=round(time.time() - t0))), flush=True)
    rows_out = [json.loads(l) for l in open(out)]
    states = {}
    for r in rows_out:
        states[r["verdict"]] = states.get(r["verdict"], 0) + 1
    meta = dict(model=a.model, provider=provider, packet=a.packet, data=a.data, max_tokens=a.max_tokens,
                thinking="adaptive/high" if provider == "anthropic" else "reasoning effort medium",
                n=len(rows_out), states=states, seconds=round(time.time() - t0, 1), date=time.strftime("%Y-%m-%d"),
                example_prompt=build_prompt(packet, *jobs[0]))
    json.dump(meta, open(str(out) + ".meta.json", "w"))
    print(json.dumps({k: v for k, v in meta.items() if k != "example_prompt"}))


if __name__ == "__main__":
    main()
