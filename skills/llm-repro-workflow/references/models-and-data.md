# Models, datasets, loading, and offline verification

## Inventory before acquisition

For models, tokenizers, adapters, datasets, and evaluation assets, record the repository ID/type, full commit SHA, selected files, source, size, and license/access conditions. Resolve author-specified tags through the Hub API or repository page, record the SHA, then download. Compare mirror content with upstream checksums where possible; a matching revision label alone does not prove identical bytes.

Prefer author-released checkpoints. Check whether base/instruct variants, quantization, precision, and merged adapters match the paper. A newer revision can change weights or tokenization. Before filtering downloads, inspect config and shard-index references so tokenizer files, chat templates, generation config, or custom code are not omitted.

## Download fixed snapshots

These API examples require project-specific values; they are not ready-made experiment scripts. Check the installed API and avoid obsolete parameters such as removed `resume_download` options. See [snapshot_download](https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download).

```python
from huggingface_hub import snapshot_download

model_dir = snapshot_download(
    repo_id="ORG/MODEL",
    repo_type="model",
    revision="FULL_COMMIT_SHA",
    local_dir="artifacts/model",
    token=False,  # Public resources; use secure authentication for private repos.
)
data_dir = snapshot_download(
    repo_id="ORG/DATASET",
    repo_type="dataset",
    revision="FULL_DATA_COMMIT_SHA",
    local_dir="artifacts/dataset",
    token=False,
)
```

`local_dir` reproduces the repository layout and has its own download metadata; it is not the same location as the shared cache. Resume an interrupted acquisition using the same fixed revision and location, then verify its files. Do not infer complete shard coverage from filename extensions alone. See the [Hub download guide](https://huggingface.co/docs/huggingface_hub/en/guides/download).

## Load models

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained(
    "artifacts/model", local_files_only=True, trust_remote_code=False
)
model = AutoModelForCausalLM.from_pretrained(
    "artifacts/model", local_files_only=True, trust_remote_code=False
)
```

This only illustrates local loading. Add verified precision, device/partitioning, and memory options for the actual project; **do not directly use the default load for a large model or treat it as a training configuration**. Check `dtype` versus `torch_dtype` for the installed transformers version. Inference `device_map="auto"` is not a general DDP training setup. If loading cannot fit the bounded validation window, provide its command rather than executing it.

Check architecture/tokenizer compatibility, all shards, index integrity, and actual file sizes. For LoRA/PEFT, pin the base revision and adapter, verify trainable parameters, and record merge strategy. Record quantization backends and precision separately.

If `trust_remote_code=True` is required, inspect the relevant code, pin its revision, explain why the standard implementation is insufficient, and stay within authorization. Do not enable it merely to silence an error. Treat untrusted pickle/checkpoint inputs as potentially executable, not necessarily plain data.

## Load and preprocess datasets

Fixed online revision:

```python
from datasets import load_dataset

dataset = load_dataset(
    "ORG/DATASET", name="CONFIG_NAME",
    revision="FULL_DATA_COMMIT_SHA", split="test"
)
```

Local Parquet:

```python
dataset = load_dataset(
    "parquet", data_files={"test": "artifacts/dataset/test-*.parquet"},
    split="test"
)
```

Use `load_from_disk` for `save_to_disk` output; a raw Hub snapshot is not inherently that format. Streaming uses an IterableDataset and does not mean the full data was downloaded. Do not assume length, random access, or offline availability. If a dataset references external URLs, record those files' versions/checksums as well as the Hub revision. See [Datasets loading](https://huggingface.co/docs/datasets/en/loading).

Inspect fixed sample IDs for config/split, fields, language/filtering, deduplication, label encoding, corruption, counts, chat formatting, truncation, padding, loss masks, packing, order, and worker randomness. Keep train/validation/test distinct. Ensure preprocessing changes invalidate the appropriate cache instead of silently reusing stale results.

Keep only shareable diagnostic samples, or hashes/statistics when data is sensitive. Record preprocessing code/parameters, raw and processed counts, and output hashes. Pin separately sourced tokenizers/templates too. Long preprocessing jobs are part of the user-operated runbook.

Old dataset loading scripts may be incompatible with newer datasets versions. Reconstruct the author's environment or document conversion into static files; do not automatically downgrade the whole stack to execute unknown scripts.

## Offline acceptance

After acquiring dependencies and resources, start a fresh Python process with `HF_HUB_OFFLINE=1`, local resource paths, and model `local_files_only=True`. Actually test the bounded target sample without network access. The variable controls the Hub client, not arbitrary project code or remote metric services. See [Hub environment variables](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables).

Include weights, indices, config, tokenizer, templates, adapters, required custom code, data, evaluation code, and metric assets in the inventory. Copying Hub caches requires preserving blobs/refs/snapshots relationships; a verified ordinary-file directory avoids dangling symlinks. Do not copy token or stored_tokens files from HF_HOME.
