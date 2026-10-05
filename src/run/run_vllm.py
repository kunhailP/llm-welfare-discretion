"""Run every (profile x query) as an independent single-turn chat with vLLM, greedy decoding.

Usage:
  python src/run/run_vllm.py --model qwen3-8b --data data/pilot/profiles.jsonl --queries q1_direct,q2_definition,q3_extraction,q4_need_severity,q5_deservingness --out results/pilot/qwen3-8b.jsonl [--limit 100]
  Several datasets in one model load: repeat --spec "DATA|QUERIES|OUT" instead of --data/--queries/--out.
"""
import argparse
import json
import os
import time

import yaml

ROOT = os.environ.get("WN_ROOT", "/workspace/welfare-need-naacl")
os.environ.setdefault("HF_HOME", "/workspace/hf")
MAX_TOKENS = {"q3_extraction": 300}


def _dtype(llm):
    try:
        return str(llm.llm_engine.model_config.dtype)
    except Exception as e:  # provenance must never break a finished run
        return f"unavailable ({type(e).__name__})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data")
    ap.add_argument("--queries")
    ap.add_argument("--out")
    ap.add_argument("--spec", action="append", default=[])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-model-len", type=int, default=4096)
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    ap.add_argument("--first-token-logprobs", action="store_true",
                    help="1-token generation, keep top-20 first-token logprobs (label probability readout)")
    a = ap.parse_args()

    from vllm import LLM, SamplingParams

    cfg = {m["id"]: m for m in yaml.safe_load(open(f"{ROOT}/configs/models.yaml"))["models"]}[a.model]
    prompts = yaml.safe_load(open(f"{ROOT}/configs/prompts.yaml"))
    specs = [x.split("|") for x in a.spec] or [(a.data, a.queries, a.out)]

    kw = dict(model=cfg["repo"], revision=cfg["revision"], max_model_len=a.max_model_len,
              gpu_memory_utilization=a.gpu_mem, seed=0)
    if cfg["repo"].startswith("mistralai/"):
        kw.update(tokenizer_mode="mistral", config_format="mistral", load_format="mistral")
    llm = LLM(**kw)

    jobs, convs, params = [], [], []
    for data, qs, out in specs:
        for r in [json.loads(l) for l in open(data)][: a.limit]:
            for q in qs.split(","):
                jobs.append((r, q, out))
                convs.append([{"role": "user", "content": prompts[q].format(text=r["text"])}])
                params.append(SamplingParams(temperature=0.0, max_tokens=1, logprobs=20) if a.first_token_logprobs
                              else SamplingParams(temperature=0.0, max_tokens=MAX_TOKENS.get(q, 64)))
    assert len(jobs) == len(convs) == len(params)
    chat_kw = {"chat_template_kwargs": {"enable_thinking": False}} if "qwen" in a.model else {}

    t0 = time.time()
    outs = llm.chat(convs, params, use_tqdm=True, **chat_kw)
    dt = time.time() - t0

    files = {}
    for _, _, out in specs:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        files[out] = open(out, "w")
    for (r, q, out), o in zip(jobs, outs):
        c = o.outputs[0]
        top = ([[lp.decoded_token, lp.logprob] for lp in c.logprobs[0].values()] if a.first_token_logprobs else None)
        files[out].write(json.dumps(dict(model=a.model, revision=cfg["revision"], query=q, profile_id=r["profile_id"],
                                    raw=c.text, finish_reason=c.finish_reason, top_logprobs=top,
                                    n_prompt_tokens=len(o.prompt_token_ids), n_output_tokens=len(c.token_ids))) + "\n")
    for f in files.values():
        f.close()
    import platform
    import torch
    import transformers
    import vllm
    meta = dict(model=a.model, repo=cfg["repo"], revision=cfg["revision"], dtype=_dtype(llm),
                vllm=vllm.__version__, transformers=transformers.__version__, torch=torch.__version__,
                python=platform.python_version(), sampling="greedy, temperature 0",
                first_token_logprobs=a.first_token_logprobs, chat_kwargs=chat_kw,
                example_rendered_messages=convs[0] if convs else None,
                n_calls=len(jobs), seconds=round(dt, 1), calls_per_sec=round(len(jobs) / dt, 2), specs=specs)
    print(json.dumps(meta))
    for out in files:
        with open(out + ".meta.json", "w") as f:
            json.dump(meta, f)


if __name__ == "__main__":
    main()
