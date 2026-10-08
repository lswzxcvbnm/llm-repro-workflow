# LLM Research Reproduction Workflow

A portable [Agent Skill](https://agentskills.io/specification) for preparing reproducible large-language-model research experiments from papers and repositories.

**Full experiments are never started inside the agent conversation.** The skill performs preparation and bounded checks, then delivers complete commands for the user to run outside the conversation. This includes full training, full-dataset evaluation, ablations, multiple seeds, and background or scheduled jobs.

## What it covers

- Trace a paper's method through entry points, configurations, data pipelines, model/loss code, and metrics.
- Inspect local CPU, RAM, disks, GPUs, VRAM, drivers, and the actual execution context.
- Choose conda or uv from project evidence, preserve pinned versions, and diagnose dependency/ABI conflicts.
- Configure project-scoped package sources, Hugging Face endpoints, mirrors, and caches.
- Acquire fixed model, tokenizer, adapter, and dataset revisions; check preprocessing and offline loading.
- Perform only bounded smoke tests with sample/step and time limits.
- Deliver launch, logging, monitoring, stopping, checkpoint-resume, evaluation, and result-aggregation commands.
- Compare user-supplied results against the paper and prepare a cross-machine reconstruction record.

The skill instructions, references, templates, and UI metadata are in English. Agents should still communicate in the user's preferred language.

## Install

With Node.js/npx, using the third-party [Skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add lswzxcvbnm/llm-repro-workflow --skill llm-repro-workflow --agent codex --global
```

Inspect before installing:

```sh
npx skills add lswzxcvbnm/llm-repro-workflow --list
```

Alternatively, in a Codex environment with skill-installer available, ask:

```text
Use $skill-installer to install the skill at:
https://github.com/lswzxcvbnm/llm-repro-workflow/tree/main/skills/llm-repro-workflow
```

For a manual, version-controlled transfer:

```sh
git clone https://github.com/lswzxcvbnm/llm-repro-workflow.git
cd llm-repro-workflow
python skills/llm-repro-workflow/scripts/install_skill.py --verify-only
python skills/llm-repro-workflow/scripts/install_skill.py
```

Use an existing Python 3.9+ interpreter (`python3` or `py -3` if appropriate). The included installer uses `$CODEX_HOME/skills`, or `~/.codex/skills`, by default. For a host that discovers user skills under `.agents/skills`, pass `--skills-dir` explicitly. Choose one installation method and avoid duplicate copies. See the [installation guide](skills/llm-repro-workflow/INSTALL.md) for platform-specific commands and caveats.

To pin the skill itself, check out a selected full Git commit before running the included installer. Checksum verification certifies the pristine skill files, not the trustworthiness of the publisher or metadata rewritten by third-party installers.

## Use

```text
Use $llm-repro-workflow to prepare reproduction of the specified paper result.
Paper: <paper URL>
Repository: <repository URL or path>
Target: <table/figure, model, dataset, training or evaluation>
Constraints: <available hardware, storage, download and time budgets>

Analyze the code, inspect hardware, prepare the environment and resources,
and perform only bounded smoke tests. Do not start full experiments.
Deliver complete commands for me to run outside this conversation,
including monitoring, stopping, resuming, evaluation, and aggregation.
```

The handoff is `reproduction/RUN.md` and appropriate shell/job scripts, with an explicit statement that the full experiment has not started. Supply resulting logs and metrics later for analysis.

## Repository layout

```text
skills/llm-repro-workflow/
  SKILL.md
  INSTALL.md
  agents/openai.yaml
  references/
    code-and-experiments.md
    environment.md
    models-and-data.md
    troubleshooting.md
    portability.md
  assets/
    run-record.md
    run-instructions.md
  scripts/
    doctor.py
    artifact_manifest.py
    install_skill.py
  bundle-manifest.json
```

## Validation and compatibility

The package uses required name/description YAML frontmatter, a matching lowercase hyphenated directory name, relative resource links, and focused references. English is a distribution choice, not a requirement of the Agent Skills format. Codex-specific UI metadata is optional for other hosts. See the [specification](https://agentskills.io/specification).

The helpers require only Python's standard library; optional probes inspect already-installed tools and packages. They do not install dependencies or download models. Check the [skill entry point](skills/llm-repro-workflow/SKILL.md) before executing any helper.

Initial validation covered naming/frontmatter, links and UI metadata, 21 helper checks, Python 3.9 syntax, ZIP integrity, and relocated installation. Helper runtime checks were performed on Windows; Linux/macOS behavior was not tested on those systems during authoring. Translation changes were checked for structure, links, and package integrity. A successful skill installation is not a reproduced research result.

This repository contains no models, datasets, experiment output, credentials, or machine-specific hardware reports. Migrate research environments and inputs separately using the [portability workflow](skills/llm-repro-workflow/references/portability.md).

## Community distribution

GitHub hosts the versioned source. [skills.sh](https://www.skills.sh/docs) offers discovery and installation through its CLI. This repository's installation command does not claim that it has already been indexed, reviewed, or endorsed by a directory. The directory controls its own indexing and ranking.

## License

[MIT](LICENSE). The standalone skill also includes a copy of the license.
