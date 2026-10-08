# Hardware, environment selection, and dependency validation

## Resource inventory

Start with `doctor.py`; supplement with `nvidia-smi`, `nvcc --version`, ROCm/AMD tools, macOS MPS, scheduler allocation details, and container/WSL device visibility as relevant. Inspect CPU cores, total/available RAM, GPU model and free/total VRAM per device, and free space on project, download, cache, build, and checkpoint volumes. Missing `nvidia-smi` does not imply that all accelerators are absent.

The CUDA version shown by `nvidia-smi` describes driver capability, not the environment's installed toolkit. `torch.version.cuda` describes the PyTorch build; `nvcc` describes the local compilation toolchain. Prebuilt wheels and source-built extensions have different requirements. Match the GPU architecture, driver, OS, and chosen packages. Consult [version-specific PyTorch installation combinations](https://pytorch.org/get-started/previous-versions/).

Estimate components separately:

- Weight storage is roughly parameters times bytes per parameter: 7 billion parameters at two bytes each is about 14 GB, or 13 GiB. This is not total inference or training memory.
- Inference also needs KV cache, activations/workspaces, and loading peaks. A conventional decoder KV estimate is `2 * layers * batch * cached_sequence_length * kv_heads * head_dim * bytes_per_element`; adapt it for MLA, sliding windows, quantization, and implementation details.
- Training adds gradients, optimizer state, possible FP32 master weights, activations, communication, and sharding peaks. There is no universal bytes-per-parameter value for every training stack.
- LoRA still needs the base model and activations. Quantized weights have scales, metadata, and unquantized modules. Multiple GPUs do not automatically combine their VRAM without a suitable partitioning strategy.
- Allow for temporary downloads, duplicate weight formats, processed data, checkpoints, optimizer state, and swap. Use bounded measurements to refine estimates; deliver long-run commands instead of starting the experiment.

## Choose the environment manager

| Repository evidence | Choice | Constraints |
|---|---|---|
| environment.yml, native/CUDA libraries, author specifies conda | conda | Named environment in configured global envs_dirs; inspect channels |
| uv.lock and pyproject.toml, explicit project or user preference | uv | Preserve the lock; use `sync --locked` and an isolated project environment |
| requirements.txt only, no special requirement | conda plus environment-local pip | Choose compatible Python before resolving dependencies |
| Required Docker image or Linux stack | Author's approach when available and authorized | Record image digest, driver, mounts, and arguments |
| Required kernels unavailable on Windows/macOS | Report the feasibility gap | Consider Linux/WSL; record changes rather than claiming identical reproduction |

Choose a Python version from the intersection of `requires-python`, lockfiles, CI, author environment, and available extension wheels. Do not impose the newest Python release.

## Conda procedure

The name `repro-demo` and Python `3.10` below are syntax examples. Derive real values from the project. Inspect existing environments before creating one; verify compatibility and ownership rather than modifying another project's environment because its name looks suitable.

```text
conda env list
conda config --show envs_dirs
conda run -n EXISTING_ENV python -c "import sys; print(sys.executable); print(sys.version)"
conda create -n repro-demo python=3.10 pip
conda run -n repro-demo python -m pip install -r requirements.txt
conda run -n repro-demo python -m pip check
```

When the author provides environment.yml, inspect its prefix, channels, platform packages, and pip section, then use `conda env create -n repro-demo -f environment.yml` instead of creating the same environment twice. Reuse an appropriate existing environment without unconditional upgrades. Prefer `conda run` to fragile shell activation. If the conda launcher fails while its own Python works, `BASE_PYTHON -m conda` can help diagnose the launcher.

Install conda-managed native libraries before pip packages. Re-solving conda after pip installation can overwrite dependencies; use a new named environment for substantial changes. PyTorch distribution channels depend on its version: use the appropriate official installation command rather than assuming every release has an official conda package.

Keep portable intent (`conda env export -n repro-demo --from-history`) as well as the complete export and platform-specific record (`conda list -n repro-demo --explicit`). Remove machine prefixes from portable files and retain pip constraints separately. History exports do not replace a complete pip lock; explicit URLs/builds usually bind to an OS/architecture. See [conda environment exports](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html).

## uv procedure

Do not accidentally layer an unrelated virtual environment over conda. Deactivate first or explicitly verify the target interpreter. Set an absolute, repository-external `UV_PROJECT_ENVIRONMENT` unique to this project and Python version. Never point it at base/system Python or share it among projects. Honor and explain an explicit repository requirement for local `.venv`.

PowerShell example, after selecting the project's Python version:

```powershell
$env:UV_PROJECT_ENVIRONMENT = Join-Path $env:LOCALAPPDATA 'llm-repro/envs/repro-demo-py310'
uv sync --locked --python 3.10
uv run --locked python -c "import sys; print(sys.executable)"
uv pip check --python "$env:UV_PROJECT_ENVIRONMENT/Scripts/python.exe"
```

Bash:

```bash
export UV_PROJECT_ENVIRONMENT="${XDG_DATA_HOME:-$HOME/.local/share}/llm-repro/envs/repro-demo-py310"
uv sync --locked --python 3.10
uv run --locked python -c 'import sys; print(sys.executable)'
uv pip check --python "$UV_PROJECT_ENVIRONMENT/bin/python"
```

Run from the project root and select the required extras/groups; optional dependencies are not all selected by default. `--locked` fails if the lock and project disagree. `--frozen` skips freshness checks and is not a conflict repair. `uv sync` can remove extraneous packages, so its environment must be isolated. Generate a new lock only when needed, and identify it as newly resolved. See [locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) and [environment paths](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path).

For an explicitly selected requirements-based uv workflow, use `uv venv EXTERNAL_ENV --python VERSION`, then `uv pip sync --python ENV_PYTHON requirements.lock`. Compile an unlocked requirements file first with `uv pip compile`. Execute with `ENV_PYTHON`; do not accidentally use `uv run` to create another project environment. Do not fall back to `python -m venv` without a user/project requirement or unavailable conda.

## Four validation layers

1. Interpreter: verify `sys.executable`, `sys.prefix`, and Python version against the intended environment.
2. Metadata: `python -m pip check` for pip environments, or `uv pip check --python ENV_PYTHON` when uv does not install pip. Save missing/conflicting dependencies and exit codes.
3. Binary/device: import torch, transformers, datasets, and required native extensions; test tiny device operations and required precision. When necessary and bounded, test collectives. Working torch alone does not prove flash-attn, bitsandbytes, or deepspeed works.
4. Project: parse the real config and perform a bounded single-sample path. Deliver commands for any unbounded check.

An available `python -m pip install --dry-run -r requirements.txt` can inspect resolution but may access the network or build metadata; it does not replace post-install validation. Trace conflicts through Python markers, extras, NumPy ABI, and torch/CUDA builds. Establish compatible constraints instead of blindly using `--no-deps`, unpinning everything, or disabling build isolation. See [pip check](https://pip.pypa.io/en/stable/cli/pip_check/) and [uv validation](https://docs.astral.sh/uv/pip/compatibility/#dependency-validation).
