# Portability and archiving

## Skill migration versus experiment migration

**Skill migration:** copy the complete `llm-repro-workflow/` directory and preserve relative paths among SKILL.md, agents, references, scripts, and assets. No original username, drive, GPU, or MCP service is required. Included helpers need Python 3.9+. Other Agent Skills-compatible tools can use the workflow; agents/openai.yaml is optional Codex UI metadata and may be ignored elsewhere.

The included installer defaults to `$CODEX_HOME/skills`, or `~/.codex/skills` when unset, matching the environment in which it was created. For hosts using `.agents/skills`, explicitly pass that parent directory with `--skills-dir`. Current Codex documentation lists user `~/.agents/skills` and project `.agents/skills`; check the actual host and install only one copy to avoid duplicate names. See [official discovery paths](https://learn.chatgpt.com/docs/build-skills).

**Experiment migration:** binaries, GPU support, weights, and datasets are not transported by installing this skill. Reinspect the target machine and reconstruct the experiment. Archiving a conda/uv environment directory does not establish cross-OS or cross-architecture portability.

## Experiment handoff layout

```text
reproduction/
  code-map.md
  plan.md
  RUN.md             # Complete user-operated launch/monitor/stop/resume/evaluate commands
  run_full.sh        # Or .ps1 / scheduler script for the actual platform; never auto-started
  environment/       # Author locks, resolved versions, interpreter/build details
  configs/           # Final configuration without secrets
  artifacts.json     # IDs, revisions, relative paths, external sources/access requirements
  manifest.json      # Explicit files and SHA-256 checksums
  runs/<run-id>/     # Commands, logs, exit codes, predictions, metrics, recovery information
  report.md          # Reference comparison, deviations, limitations
```

Large weights, data, and checkpoints can remain in external storage, referenced through path variables, versions, retrieval instructions, and checksums. Do not put them into the skill ZIP. When redistribution is unavailable, document authorized acquisition instead.

Retain both human-readable dependency intent and machine-rebuildable locks/provenance. For conda, save portable YAML without a machine prefix, pip constraints, and the original platform's explicit record. For uv, save pyproject.toml, uv.lock, Python version, groups/extras, and indexes. Include native-extension/system-library requirements; identify editable installs and nonportable absolute local file URLs.

Preserve the actual executed code as a commit plus uncommitted patch, or a clearly identified source snapshot. A commit without the changes used in the run is not an exact code record.

## Rebuild on another machine

1. Verify the pristine skill bundle's checksums. They detect content changes, not publisher identity.
2. Install once into the host's supported directory. Check discovery in a new session; restart the host if needed.
3. Rerun hardware/doctor in the actual execution context, checking OS/architecture, GPU/driver, and free storage.
4. Retrieve the fixed code and patch, then rebuild a global named conda environment or isolated uv environment. Re-resolve platform packages when necessary while preserving top-level intent and recording differences.
5. Map HF_HOME, input, output, and checkpoint paths to the new machine. Verify resource hashes. Do not transfer tokens, proxy passwords, or .env secrets.
6. Perform only bounded dependency/device/loading/smoke checks in the conversation. Provide other validation and full experiment commands for the user outside the conversation.
7. Deliver the original protocol, tolerances, and aggregation commands. Record target-machine outcomes only after user-supplied results arrive. Throughput and floating-point values may vary across hardware.

## Explicit-file manifests

List only intended artifacts, relative to `--root`:

```text
python SKILL_DIR/scripts/artifact_manifest.py create --root reproduction --file plan.md --file environment/requirements.lock --output reproduction/manifest.json
python SKILL_DIR/scripts/artifact_manifest.py verify --root reproduction --manifest reproduction/manifest.json
```

The tool rejects outside-root paths, links, and non-regular files and hashes incrementally. Verification checks listed files, not extra files. Do not include the manifest itself. The bundle installer separately checks the exact distribution file set. If a third-party installer rewrites metadata, verify the pristine source bundle; its checksum cannot certify transformed files without a newly reviewed manifest.

## Completion criteria

Preparation is complete when RUN.md/scripts and validation evidence are delivered. Say **Full experiment not started; the user runs the supplied commands.** Do not wait in the conversation for the long job.

Report the highest stage actually completed, deviations, estimates versus measurements, commands, and remaining blockers. Populate observed metrics only from real results. After a successful reduced check, state both that the smoke test passed and that the full experiment remains unexecuted.
