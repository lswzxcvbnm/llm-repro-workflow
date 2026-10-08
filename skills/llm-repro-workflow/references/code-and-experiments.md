# Code analysis and experiment design

## Freeze the baseline

Inspect `git status --short`, `git rev-parse HEAD`, and `git submodule status`, then the README, paper appendix, releases, example configurations, and dependency files. For LFS repositories, inspect `git lfs ls-files` and real file sizes: pointer text is not a model weight file. Do not refactor a research project merely to reproduce it.

Use `rg --files` and targeted `rg -n` searches rather than loading the entire repository. Useful anchors:

```text
Entry points: __main__ / argparse / hydra.main / click / main()
Assembly: from_pretrained / load_dataset / DataLoader / collator
Execution: Trainer / Accelerator / backward / optimizer.step / generate
Distributed: torchrun / deepspeed / init_process_group / FSDP
Evaluation: compute_metrics / evaluate / lm_eval / scorer
State: save_pretrained / save_checkpoint / resume / load_state_dict
```

Trace forward from the paper's launch command and backward from the final metric. Produce a mapping with exact symbols and current file/line references:

| Paper step | Entry point/symbol | Config and precedence | Inputs and shapes | Output | Check |
|---|---|---|---|---|---|
| Data construction | Actual function | CLI/YAML/default precedence | Fields, split, count | Tokens/labels/masks | Inspect fixed samples |
| Model/loss | Actual class/forward | Precision, adapter, loss weights | Batch, sequence, hidden | Logits/loss | Forward and gradients |
| Evaluation | Actual scorer | Few-shot, template, decoding | Prompts, references | Predictions/score | Manually score one sample |

Check working-directory assumptions, relative paths, environment defaults, implicit downloads, data leakage, repeated sampler examples, the checkpoint actually loaded, and adapter-only versus full-model saves. If paper, README, and implementation disagree, retain the evidence and state which setting this reproduction follows.

## Define the protocol

Specify the target table/row/column, metric unit and direction, split, checkpoint selection, and acceptable deviation before seeing results. Explain any self-defined tolerance; do not invent a universal percentage. Use validation data for selection, not test data for score chasing.

- Training: initial weights, trainable parameters, loss reduction, optimizer/eps/betas, schedule/warmup, learning rate, weight decay, epochs/steps, effective batch, sequence length, packing/truncation, gradient clipping, precision, and checkpointing.
- Generation: tokenizer revision, chat template, BOS/EOS/PAD, padding side, sampling, temperature, top-p/top-k, max_new_tokens, stopping, parallelism, and KV cache.
- Evaluation: prompts, few-shot samples/order, extraction/normalization, token or example weighting, pass@k sampling count, harness commit, perplexity windows/loss masks, and choice-score length normalization.
- API or LLM-as-judge: judge model/version identifiers, prompts, sampling, and raw responses. Remote services may drift; do not claim the same reproducibility as pinned local weights.

For simple data parallelism, effective batch equals per-device microbatch times gradient accumulation times data-parallel replicas. Total GPUs in tensor/pipeline parallelism are not the replica count. Check partial batches, token-based batching, and loss normalization too.

## Stage verification and assign execution

This is an experiment sequence, not permission for the agent to run every stage. Full experiments are delivered as instructions for the user outside the conversation, including background and scheduler execution.

| Stage | Action | Executor | Evidence before expansion |
|---|---|---|---|
| Static | Parse config; inspect code, paths, dependencies | Agent | Parameters match the target; inputs available |
| Smoke test | A few batches; updates or generation/scoring | Agent only with sample/step and time limits | Correct shapes, finite outputs, actual gradients/updates |
| Save/restore | Save and reload checkpoint | Agent only when bounded; otherwise user | Step, optimizer/scheduler, and required RNG restored |
| Small baseline | Fixed subset | Agent only for bounded short checks; otherwise user | Throughput, memory, cost estimate, output format |
| Full baseline | Original configuration and target split | User outside the conversation | Complete logs, successful exit, recomputable metrics |
| Method/ablations | Explainable changes and required seeds | User outside the conversation | Same-protocol comparison and appropriate statistics |

A tiny supervised overfit test can diagnose data and optimization, but still needs step/time limits. Decreasing loss alone does not prove correctness. If startup, loading, compilation, or workload cannot be bounded, deliver the test command rather than executing it.

## Complete runbook requirements

Generate `reproduction/RUN.md` from the [runbook template](../assets/run-instructions.md), and suitable `run_full.sh`, `run_full.ps1`, or job files when useful. Target the user's actual platform and repository; do not assume an entry point named train.py.

Include:

1. Fresh-terminal working directory, conda/uv or exact interpreter, environment variables, and resource paths. Do not rely on state set only inside the conversation.
2. Separate commands for unfinished preparation, pinned resources, access requirements, and cache setup. Never embed credentials.
3. Exact dependencies and order for applicable baseline, training/fine-tuning, inference, evaluation, ablations, and seeds. Include actual configs, devices/parallelism, batch/accumulation, precision, outputs, and checkpoint selection.
4. Separate output directories, stdout/stderr capture, and the experiment's real exit status. A logging pipeline must not report tee success as experiment success. Preserve pipefail/process status in Bash; explicitly propagate native exit codes in PowerShell.
5. Foreground launch instructions, then persistent-session/scheduler instructions if needed. Label them user-operated and not started. Do not run them to validate the commands.
6. Log viewing, device utilization, progress, success/failure signals, scoped stopping, and resume commands. Explain how to obtain PID/job IDs; never invent IDs, measured runtimes, or nonexistent checkpoints.
7. Exact prediction, scoring, rescoring, and seed aggregation commands, expected files, metric definitions, and tolerances.

Statically verify entry points, argument parsers, config keys, resource paths, and shell syntax. Even `--help`, imports, or config parsing may trigger loading or execution; inspect code before using them. Do not invent `--dry-run`. List unresolved values and make generated scripts fail clearly on missing configuration rather than falsely claiming immediate readiness.

Finish preparation by stating which short checks actually ran, where the complete commands are, that the full experiment was not started, and any required user configuration. When later logs arrive, diagnose and revise commands without automatically restarting long experiments.

## Randomness, logging, and recovery

Record Python, NumPy, PyTorch, device, sampler, and DataLoader worker seeds. Explicit NumPy Generator objects need their own seeding. Record shuffling, sample order, and distributed `set_epoch`; set PYTHONHASHSEED before Python starts.

Match deterministic algorithms, cuDNN benchmark, TF32, precision, and attention backends to the paper and supported operations. Do not silently enable numerically different acceleration. A fixed seed does not guarantee bitwise identity across hardware or PyTorch releases. See [PyTorch reproducibility](https://docs.pytorch.org/docs/main/notes/randomness.html).

Have the generated scripts record argument arrays, shell/cwd, start/end, exit code, logs, counts, learning curves, throughput, peak VRAM/RAM, and independent run directories. Prefer the project's job runner. Persistent sessions, scheduler jobs, and redirected hidden Windows processes are instructions for the user, not actions for the agent to launch.

After an interruption, inspect the user's logs and last complete checkpoint before producing a resume command. Identify how step, optimizer, scheduler, scaler, RNG, and sampler/data position are restored. Loading weights alone is a warm start, not exact continuation. Do not execute long resumed training in the conversation.

## Diagnose metric differences

Compare in order: code/weight revisions -> splits/preprocessing/counts -> prompts/templates/tokenizer -> metric/scorer -> hyperparameters/token budget -> checkpoint selection -> seeds/precision/kernels -> hardware/library versions.

Retain before/after commands and outcomes, and change one explainable factor at a time. For speed metrics, record warmup, synchronization, batch, input/output lengths, compilation-time accounting, and contention. Different hardware timings alone do not establish an algorithmic reproduction failure.
