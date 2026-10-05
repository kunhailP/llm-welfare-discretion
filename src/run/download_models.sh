#!/usr/bin/env bash
# Downloads pinned model revisions to the persistent volume, in priority order.
set -u
export HF_HOME=/workspace/hf HF_HUB_ENABLE_HF_TRANSFER=1
PY=/workspace/venv/bin/python
while read -r repo rev; do
  echo "[$(date -Is)] start $repo@$rev"
  $PY -c "from huggingface_hub import snapshot_download as s; print(s('$repo', revision='$rev', allow_patterns=['*.json','*.safetensors','*.txt','*.model','*.jinja','tekken*','*.py']))" && echo "[$(date -Is)] done $repo" || echo "[$(date -Is)] FAILED $repo"
done <<LIST
Qwen/Qwen3-8B b968826d9c46dd6066d109eabc6255188de91218
mistralai/Ministral-3-8B-Instruct-2512-BF16 f6fae9795746f63c9be8344932f01275f3c63734
Qwen/Qwen3-14B 40c069824f4251a91eefaf281ebe4c544efd3e18
Qwen/Qwen3-32B-AWQ 0499c3ac83fdef8810b907a23894ba91e95eddd8
LIST
