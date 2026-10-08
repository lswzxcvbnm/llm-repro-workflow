---
name: llm-repro-workflow
license: MIT
description: Prepare reproducible LLM research experiments from papers and repositories. Use for code walkthroughs, hardware feasibility, conda or uv setup, dependency and mirror troubleshooting, pinned model and dataset acquisition, bounded smoke tests, experiment runbooks, and analysis of user-supplied results. Deliver full experiment commands for the user to run outside the conversation; do not launch long experiments.
---

# LLM Research Reproduction Workflow

Turn a specific research claim into a traceable experiment plan, a verified setup, and complete execution instructions. Respond in the user's language. The instructions are in English, but the user's reports and explanations need not be.

## Execution boundary

**Do not start or wait for complete experiments in the conversation.** Deliver full training, full-dataset evaluation, multi-seed runs, ablations, and other long experiments as commands for the user to execute outside the conversation. Starting a background process, tmux/nohup session, scheduler job, automation, or delegated run also starts the experiment and does not bypass this boundary. Available hardware or budget does not change it.

Inside the conversation, perform preparation, code analysis, static checks, and small tests with explicit sample/step limits **and a wall-clock limit**. If model loading, compilation, a small baseline, or checkpoint save/restore cannot be reliably bounded, provide its command instead. Delivering the complete runbook finishes the preparation task; do not keep polling or require the user to run it immediately.

## Working rules

- Read user constraints, project instructions, the paper's experiment settings, and repository documentation. Infer supported details and label assumptions; ask only for missing information that changes the target or prevents progress.
- Distinguish feasibility analysis, environment validation, a successful smoke test, and reproduction of the target metric. Smaller models, quantization, fewer samples, or algorithm changes are deviations, not equivalent reproduction.
- Default to conda. Check reusable environments before creating a named environment in conda's configured global environment directories. Use uv when the project explicitly requires it, provides uv.lock, or the user chooses it. Do not create repository-local environments without a project or user requirement; do not install research dependencies into base or system Python.
- Keep mirrors, proxies, caches, and credentials scoped to the process or project. Preserve existing global settings and unrelated GPU jobs. Do not disable TLS or delete shared caches as a generic repair.
- Preserve author-pinned versions first. Consult documentation for those versions; do not fix old research code by upgrading everything. Record each compatibility patch and its validation.
- Respect download, storage, and runtime budgets. Do not upload artifacts or provision paid cloud compute without authorization.

## Workflow

Use the project's artifact layout, or `reproduction/` with independent `runs/<run-id>/` directories. Copy the [run record](assets/run-record.md) and [runbook template](assets/run-instructions.md) into the project. Do not write research artifacts into the installed skill directory.

### 1. Define the target and freeze the code

Identify the paper/version, repository, table or figure, model size, task, training versus evaluation scope, dataset range, hardware, and time budget. If the target is missing, inventory the repository without inventing reference metrics.

Record the repository URL, full commit, submodule/LFS state, and uncommitted changes. Preserve user edits; use an isolated checkout when a version change is needed. Inspect installation scripts before executing them.

Follow [code and experiment analysis](references/code-and-experiments.md) to produce `code-map.md` and `plan.md`: paper step -> config -> implementation symbol/file/line -> input/output -> validation. Define metrics and tolerances before results are observed.

### 2. Establish hardware feasibility

Read [hardware and environments](references/environment.md) before large downloads. Run `scripts/doctor.py` in the actual execution context to inspect the OS, CPU, available memory, relevant disks, GPUs/VRAM, driver, interpreter, and tools. A host report is not proof of resources available inside WSL, a container, or a scheduled allocation.

Estimate weights, precision, sequence length, optimizer state, activations, KV cache, batch size, and parallelism. Refine estimates with bounded measurements where feasible. Report: original configuration feasible, documented adjustments required, or insufficient resources. Continue useful preparation even when the full setup is infeasible.

### 3. Build and validate the environment

Choose conda, uv, or the author's required container from repository evidence. Check Python/PyTorch/CUDA or ROCm/native-extension compatibility before installation. Use [network and dependency troubleshooting](references/troubleshooting.md) when needed.

Verify the interpreter, dependency metadata, key imports, tiny device operations, and a bounded project entry point. Passing `pip check` or `uv pip check` does not establish ABI or algorithm correctness. Save locks, actual versions, installation commands, and package sources.

### 4. Acquire and validate models and data

Read [models and datasets](references/models-and-data.md). Record repository IDs/types, full revisions, access/license requirements, file lists, estimated storage, and local paths. Test connectivity with small metadata/files before large downloads.

Track the relationship between model, tokenizer, adapter, data, and preprocessing versions. Verify shards, schemas, splits, counts, chat templates, label masks, and leakage. Test offline loading with local resources; setting an offline variable alone is not evidence that all resources are present.

### 5. Perform bounded checks and deliver full commands

Prepare these stages with explicit ownership:

1. Agent: static inspection, imports, and configuration parsing.
2. Agent, only when bounded: a few samples or batches with step/sample and time limits; check forward/backward/update for training or prompts/generation/scoring for evaluation. Save/restore only when equally bounded.
3. Small baseline: provide throughput, peak-memory, stability, and cost-estimation commands. Execute only genuinely short, bounded parts in the conversation.
4. User, outside the conversation: full baseline, method, full evaluation, ablations, and multiple seeds.

Resolve unexplained NaNs, wrong data, absent updates, faulty scoring, or configuration drift before recommending expansion. Document changes to effective batch size, context length, precision, quantization, or dataset size.

Deliver `reproduction/RUN.md` and appropriate shell/job scripts. Include the working directory, environment/interpreter, variables, resolved resource/config paths, devices and parallelism, seeds, execution order, logs, real exit codes, checkpoints, scoring, and aggregation. Verify arguments against the actual repository. Ellipses, invented flags, or unexplained placeholders do not constitute complete commands.

Provide user-operated start, monitor, completion-check, stop, and resume instructions, expected outputs, resource estimates, and unverified assumptions. Generate persistent-session or scheduler scripts if appropriate, but do not execute or submit them. Report: **Preparation complete; full experiment not started.**

### 6. Compare supplied results and package the handoff

Initially provide the comparison protocol and aggregation commands; mark unrun metrics as pending user execution. After the user supplies logs/artifacts, compare reference and observed metrics, absolute/relative differences, seed variation, time, and resources under the same protocol. Diagnose discrepancies from evidence; do not tune against the test set or automatically launch another long run.

Follow [portability and archiving](references/portability.md) to save environment reconstruction instructions, code/patches, model/data inventories, checksums, runbooks, results, and limitations. State what actually ran and what remains unexecuted.

## Included tools

The tools themselves need Python 3.9+ and the standard library. Optional probes use already-installed packages/tools; nothing is installed or downloaded. Use the target environment's interpreter. Replace `SKILL_DIR` with this skill's location.

```text
python SKILL_DIR/scripts/doctor.py --project . --disk-path /path/to/cache --output reproduction/preflight.json
python SKILL_DIR/scripts/doctor.py --project . --probe-torch --check-deps auto --output reproduction/environment-check.json
python SKILL_DIR/scripts/artifact_manifest.py create --root reproduction --file plan.md --file environment-check.json --output reproduction/manifest.json
python SKILL_DIR/scripts/artifact_manifest.py verify --root reproduction --manifest reproduction/manifest.json
```

`doctor.py` distinguishes not requested, unavailable, failed, and successful probes. Exit 0 normally means the report was written. With `--strict`, an explicitly requested Torch/dependency check that fails or cannot finish returns 1. CPU success does not prove GPU readiness; this does not validate full models, native extensions, or collectives. Dependency checking supports `auto`, `pip`, and `uv`. Review paths and other sensitive details before sharing reports.

The manifest tool hashes explicitly listed files, rejects paths outside its root and links, and streams large files. It does not collect credentials or recursively package caches. Hashing large weights requires disk-read time.
