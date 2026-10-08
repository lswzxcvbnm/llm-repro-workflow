# Networks, mirrors, and troubleshooting

## Diagnose before changing settings

Save the failing command, exit code, first relevant traceback, and versions. Separate connectivity, authentication, missing files, resolution, ABI, and memory issues. Use bounded retries, such as two attempts; then change one justified factor or report an external blocker rather than retrying unchanged forever.

Test DNS, proxy, TLS, endpoint, and disk access with metadata/small files before large weights. If only a mirror is reachable, state that source and verification limitation. Do not print the full environment; redact tokens, proxy passwords, and authenticated URLs.

## Conda channels

Inspect `conda config --show-sources` and `conda config --show channels channel_priority` locally, then the actual host, channel, and subdir requested. Do not hard-code `linux-64` into a channel root on Windows. Old channels, mixed ecosystems, CONDA_SUBDIR, certificates, proxies, and solver constraints can all cause failures.

Prefer command-scoped `--override-channels -c URL --strict-channel-priority` over rewriting the user's .condarc. After confirming that the chosen channel supplies the required packages, adapt this example:

```text
conda create -n repro-demo python=3.10 pip --override-channels -c https://conda.anaconda.org/conda-forge --strict-channel-priority
```

For an accepted mirror, replace the channel root, for example with `https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge`. Check platform coverage and version synchronization first. Defaults and conda-forge are different ecosystems; changing a mirror does not make all packages interchangeable. See the [Tsinghua mirror operator's instructions](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/).

Inspect channels embedded in environment.yml and change only a reviewed project copy. If complex mappings require a temporary CONDARC, verify the effective merged configuration and resolved URLs, then restore prior variables. Setting CONDARC does not justify assuming all other configuration sources disappear.

For UnsatisfiableError, inspect Python/platform/GPU pins before rebuilding an isolated environment. Avoid repeatedly upgrading a shared environment. Remove only demonstrably corrupt cache entries; do not default to `conda clean --all`.

## pip and uv indexes

Scope pip `--index-url` to a command where practical. A mirror must contain the pinned versions. GPU wheels may require the official PyTorch index for the selected release; a CUDA-specific index is not necessarily a general PyPI replacement.

Make multi-index package provenance explicit instead of guessing from index order. Use the project's uv index/source declarations and inspect the lock after any change. Do not hide TLS failures with `--trusted-host` or disabled certificate validation; configure a trusted organizational CA when applicable. See [uv indexes](https://docs.astral.sh/uv/concepts/indexes/).

## Hugging Face endpoint and caches

Prefer `https://huggingface.co`. Use a user-accepted third-party mirror such as HF-Mirror when network conditions justify it. Mirror revision synchronization, gated access, and large-file transport may differ from upstream. See [HF-Mirror's own documentation](https://hf-mirror.com/).

Set variables before importing huggingface_hub, transformers, or datasets. PowerShell example:

```powershell
$env:HF_HOME = 'D:/research-cache/huggingface'  # Choose a suitable local volume.
$env:HF_ENDPOINT = 'https://hf-mirror.com'     # Only when this mirror is selected.
$env:HF_HUB_DISABLE_IMPLICIT_TOKEN = '1'      # Do not implicitly send stored tokens.
```

Bash:

```bash
export HF_HOME="/path/to/research-cache/huggingface"
export HF_ENDPOINT="https://hf-mirror.com"
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1
```

Restore previous variable values afterward; if HF_ENDPOINT was absent, remove it, then restart Python. Preserve organizational settings. HF_INFERENCE_ENDPOINT configures inference APIs, not Hub downloads. HF_HOME may contain credentials as well as cache files; migrate only necessary assets. See [Hub variables](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables).

Check the installed client's `huggingface_hub.constants.ENDPOINT`. Hard-coded project URLs and external dataset hosts may ignore HF_ENDPOINT. Use explicit `token=False` for public resources. Prefer the official endpoint and secure login/secret injection for private or gated resources. Never put tokens in scripts, command lines, run records, or archives. A mirror does not bypass access authorization.

For slow/failed large downloads, inspect redirect and Xet/CAS connectivity, disk/quota, rate limits, and concurrency. Reduce workers where appropriate and retry the fixed revision/location. Consider HF_HUB_DISABLE_XET=1 only when evidence points to Xet and the installed version supports it. Adjust documented timeouts rather than increasing them indefinitely.

## Failure triage

| Symptom | Evidence to inspect | Repair and verify |
|---|---|---|
| 401/403 or gated access | Repo permission, license acceptance, token endpoint | Complete official authorization; test a small file |
| 404 or missing revision | ID, repo_type, full SHA, mirror synchronization | Check upstream; do not silently switch to main |
| TLS/DNS/timeout | Clock, CA chain, proxy, host | Repair CA/proxy or use an accepted temporary source; keep TLS |
| CUDA unavailable | Interpreter, torch build, driver, devices/allocation | Match wheel and device visibility; rerun a tiny operation |
| Undefined symbol, DLL, ABI failure | Torch/CUDA/compiler/NumPy/extension build | Match or rebuild the extension; pip check alone is insufficient |
| flash-attn build failure | Python, GPU architecture, OS, toolkit, torch | Check that version's support matrix; disclose backend substitutions |
| OOM | Loading versus forward/backward/KV, peak VRAM | Release this task's unused objects; adjust microbatch/accumulation first; disclose semantic changes |
| NaN or no updates | Labels/masks, loss, gradients, LR, scaler | Isolate one bounded batch instead of waiting through a long run |
| Distributed hang | Ranks, port, collectives, networking/backend | Bounded single-device then minimal multi-device check; affect only this task |
| Windows path/process error | Length, spaces, links, spawn/main guard | Correct paths/quoting or assess the project's WSL support |
| Offline code still connects | External loaders/metrics, tokenizer, shards | Complete local inputs and actually retest offline |
| Completed run gives wrong score | Split, templates, decoding, scorer, checkpoint | Compare the protocol before treating it as an environment problem |

If the original dependencies are no longer installable, retain the evidence and prefer the author's container/archived wheels or minimal compatibility changes. Identify the setup as a substitute rather than the original environment and validate affected behavior. Deliver full retry or resume commands for the user; troubleshooting does not authorize starting long experiments.
