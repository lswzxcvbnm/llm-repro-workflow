# Full experiment runbook

Use this template to generate the project's `reproduction/RUN.md`. Fill commands, configurations, and paths from the actual repository. The template itself and commands containing ellipses are not complete execution instructions. The user runs full experiments outside the conversation; the agent does not launch background processes or submit jobs.

## Preparation status

- Completed code/environment/resource preparation and bounded checks:
- Full experiment status: not started.
- Missing resources, configuration, or access and how to obtain them:
- OS, shell, source commit, environment lock version:
- Estimated runtime/resources, distinguished from measurements:

## 1. Set up a fresh terminal

Supply complete copyable commands for the working directory, conda/uv environment or interpreter, devices, caches, endpoint, data, and output paths. Use actual locations or clearly documented configuration variables. Do not depend on shell state from the conversation.

List prerequisite files and verification commands. Separate unfinished downloads, preprocessing, and other preparation. Use secure login/secret injection, never credentials in scripts.

## 2. Bounded smoke test, if user execution is needed

Provide the real entry point, config, sample/step limit, wall-clock limit, and expected outputs. State which checks already ran to avoid repeating expensive validation.

## 3. Full baseline and target experiments

Provide every complete command or executable script plus its invocation, in dependency order: baseline, training/fine-tuning, inference, evaluation, seeds, and ablations as applicable. Include configs, inputs, device count/parallelism, hyperparameters, seed, independent run ID, outputs, and checkpoint paths. Do not replace required arguments with ellipses.

Label the commands: **User execution required; the agent has not run them.** Give foreground instructions first. Add platform-appropriate persistent-session/background/queue instructions if needed.

## 4. Logs, progress, completion, and stopping

Specify stdout/stderr and real exit-code capture, live log viewing, progress/resource checks, success/failure criteria, how to obtain the PID/job ID, and how to stop only this task. Do not invent a live PID or job ID before execution.

## 5. Resume after interruption

Explain complete checkpoint selection and provide the repository's real resume options. Identify whether weights, optimizer, scheduler, RNG, and data position are restored. Explain any warm-start limitation. The user executes resumed training too.

## 6. Evaluation and aggregation

Supply prediction, scoring, rescoring, and multi-seed aggregation commands, expected files, metric definitions, and comparison tolerances. If steps are chained, proceed only after the preceding step succeeds. Mark unrun metrics as pending user execution.

## Command validation record

- Inspected entry points, arguments, config keys, paths, and shell syntax:
- Short checks actually executed and their outcomes:
- Full commands checked statically but not executed:
- Logs, configs, metrics, and checkpoint metadata the user can provide for follow-up analysis:
