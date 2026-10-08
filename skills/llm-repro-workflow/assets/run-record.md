# Research reproduction record

Copy this template into the project. Use actual values; label unknowns and non-applicable fields. Example settings are not executed results.

## Target and status

- Paper/version/URL, repository, target table/figure/row:
- Task scope (training/fine-tuning/inference/evaluation), metric direction and units:
- Acceptance tolerance and rationale; time/VRAM/storage/download budgets:
- Highest completed stage; completed, pending, and blocked work:
- Runbook location and validation; executor (user); full experiment status (not started / user running / supplied results received):

## Code and execution map

- Repository URL, full commit, branch, submodules/LFS:
- Uncommitted changes and patch location:
- Entry -> configuration -> data -> model/loss -> optimizer/generation -> scoring -> outputs:
- Key files/symbols/lines and paper-to-code discrepancies:

## Hardware and environment

- OS/architecture; host, WSL, container, or scheduler context:
- CPU, available/total RAM, free storage on relevant volumes:
- GPUs, free/total VRAM per device, driver/toolchain:
- Python path/version, conda/uv version, choice and reuse rationale:
- Torch/CUDA or ROCm, transformers, datasets, and native-extension versions:
- Lockfiles, channels/indexes/endpoints without secrets, installation commands:
- Dependency, device, and project-import checks with outcomes/exit codes:

## Inputs and protocol

| Resource | Repository ID/type or source | Full revision/hash | Relative local path | Size/checksum | License/access |
|---|---|---|---|---|---|
| Model | | | | | |
| Tokenizer/template | | | | | |
| Adapter, if any | | | | | |
| Dataset/external files | | | | | |

- Dataset config/splits/fields; raw and processed sample counts:
- Preprocessing version, filters, deduplication, seeds, sequence length, packing/masks:
- Training settings, trainable parameters, effective batch calculation, total training tokens:
- Decoding, prompts/few-shot/templates, scorer version and arguments:
- Checkpoint selection; determinism and attention backend:
- Reference conditions, changes, reasons, and effects on comparability:

## Per-run record (copy for each run ID)

The user runs complete experiments outside the conversation. Before execution, retain planned settings and mark actual timestamps, exit codes, and metrics as pending. Do not report estimates as measurements.

- Run ID, UTC timestamp/timezone, cwd, shell, argument array or fully quoted command:
- Config and hash, seed, data scope, checkpoint input/output:
- Start/end, exit code, job ID, logs, and resume command:
- Update/numerical/save-and-restore checks:
- Elapsed time, throughput measurement protocol, peak VRAM/RAM, storage growth:
- Predictions, raw metrics, rescoring command, and artifact manifest:

| Metric | Reference | Observed/per-seed values | Mean/std, when applicable | Absolute difference | Relative difference | Tolerance/outcome |
|---|---|---|---|---|---|---|
| | | | | | | |

Use not applicable for a relative difference with a zero denominator. Identify the standard-deviation estimator; one seed does not establish seed variability.

## Diagnosis, conclusions, and migration

- Failure evidence -> root-cause hypothesis -> minimal change -> verification:
- Supported conclusions, limitations, and unexecuted work:
- Target-machine rebuild commands, path mapping, and offline checks:
- Environment locks, source patches, manifest, report, and external large-file locations:
- Removed credentials/private data and authorized acquisition for non-redistributable resources:
