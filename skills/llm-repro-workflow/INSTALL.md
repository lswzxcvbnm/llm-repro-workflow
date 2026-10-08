# Installation and cross-machine use

This English Agent Skill contains the workflow, five focused references, run-record and runbook templates, and three standard-library Python helpers. It does not include research repositories, models, datasets, Python environments, or machine credentials.

**Full experiments are command-only handoffs.** The agent prepares and performs bounded checks; the user runs full training, full evaluation, ablations, and multi-seed experiments outside the conversation.

## Install the verified bundle

Extract the complete llm-repro-workflow directory and use an existing Python 3.9+ interpreter. No additional Python environment or dependencies are needed just to install this skill.

From the extracted directory:

```text
python scripts/install_skill.py --verify-only
python scripts/install_skill.py
```

Use `py -3` or a conda interpreter path on Windows, or `python3` on Linux/macOS as appropriate. By default, the installer targets `$CODEX_HOME/skills/llm-repro-workflow`, or `~/.codex/skills/llm-repro-workflow` if CODEX_HOME is unset, preserving the original local convention.

For a host using the current documented `.agents/skills` user location, select it explicitly. Install only one copy for the host. See [Codex discovery paths](https://learn.chatgpt.com/docs/build-skills).

PowerShell:

```powershell
python scripts/install_skill.py --skills-dir (Join-Path $HOME '.agents/skills')
```

Bash:

```bash
python3 scripts/install_skill.py --skills-dir "$HOME/.agents/skills"
```

The installer checks SHA-256, sizes, and the exact file set before copying, refuses existing destinations, and verifies copied files. Checksums detect changed bytes, not publisher identity. Keep local customizations before deciding how to replace an older installation.

You can also copy the entire folder into the host's supported discovery directory. Open a new session and restart the host if it is not discovered. Other Agent Skills-compatible tools can consume SKILL.md; agents/openai.yaml is optional Codex metadata.

## Install from the public repository

After the repository is published, use its source URL. With Node.js/npx and the third-party Skills CLI:

```text
npx skills add lswzxcvbnm/llm-repro-workflow --skill llm-repro-workflow --agent codex --global
```

This is an alternative to the Python installer, not an additional required installation. For a reproducible skill version, retrieve a selected repository commit and install its pristine `skills/llm-repro-workflow` directory. Authentication is needed if a repository later becomes private. See [Skills CLI documentation](https://github.com/vercel-labs/skills).

## Example requests

```text
Use $llm-repro-workflow to prepare reproduction of Table 2 in this paper.
Paper: paper URL
Repository: repository URL or local path
Target: the selected model/dataset training or evaluation
Limits: local execution, maximum four hours for the user-operated experiment.
Analyze the code, inspect hardware, prepare the environment and inputs, and run
only bounded smoke tests. Do not start the full experiment. Deliver complete
commands for launch, monitoring, stopping, resuming, evaluation, and aggregation.
```

```text
Use $llm-repro-workflow to assess whether this repository is feasible on my
machine. Produce a code map, environment choice, and resource gaps without
large downloads or complete experiments.
```

```text
Use $llm-repro-workflow to migrate an existing experiment to another Linux GPU
machine. Verify locks and resource hashes, perform only bounded smoke tests,
and deliver full commands adapted to the new machine for me to run separately.
```

The workflow is: freeze target/code -> map implementation -> inspect resources -> choose and validate environment -> configure sources/cache -> pin inputs -> bounded tests -> complete runbook -> user execution -> analyze supplied results and archive.

Values such as ORG/MODEL, FULL_COMMIT_SHA, environment names, and example paths in references illustrate syntax. Replace them from real project evidence before generating the final runbook.

## Package map

| Path | Purpose |
|---|---|
| SKILL.md | Entry point, execution boundary, routing, workflow |
| references/code-and-experiments.md | Code analysis, protocol, runbook, recovery, comparison |
| references/environment.md | Hardware sizing, conda/uv, CUDA and dependency validation |
| references/troubleshooting.md | Package sources, HF mirrors, network/build/OOM/distributed failures |
| references/models-and-data.md | Pinned acquisition, loading, preprocessing, offline checks |
| references/portability.md | Skill and experiment reconstruction on another machine |
| assets/run-record.md | Experiment record template |
| assets/run-instructions.md | Complete user-operated execution template |
| scripts/doctor.py | Read-only local hardware/environment report |
| scripts/artifact_manifest.py | Explicit-file SHA-256 creation and verification |
| scripts/install_skill.py | Verified installation without overwriting existing skills |
| bundle-manifest.json | Pristine distribution checksums |

## Maintenance and limits

Documentation reviewed on 2026-10-08. Recheck the research project's pinned tool versions when executing its commands. Skill portability does not imply binary-environment portability or bitwise-identical results.

After editing the skill, rebuild bundle-manifest.json from an explicit reviewed list excluding the manifest itself, caches, research artifacts, and credentials. Then validate and package it. Do not ignore mismatches to hide accidental corruption. Third-party installers may transform metadata; verify the original bundle separately in that case.

The helpers were exercised on Windows. Linux/macOS branches are implemented but were not tested on those operating systems during initial authoring. Inspect the target machine before relying on them. No research experiment is claimed to have been reproduced by merely installing this skill.
