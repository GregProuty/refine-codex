# Refine for Codex

A Codex skill that hardens a spec, plan, or implementation through independent Codex CLI review rounds. The active Codex agent controls the loop and checks each finding; a fresh `codex exec` session produces each review. The original workflow, ledger, scripts, and stopping rules come from [Greg Prouty's refine-skill](https://github.com/GregProuty/refine-skill).

## Requirements

- Codex CLI, installed and authenticated, with a trusted project
- Python 3, Git, and Bash (Git Bash on Windows)
- A repository with a clean index and a committed subject

## Install

Run `python install.py` from this repository. This copies the skill to `$CODEX_HOME/skills/refine`, or `~/.codex/skills/refine` when `CODEX_HOME` is unset. The installer refuses to overwrite an existing installation; use `python install.py --update` to refresh it. Restart Codex if the skill does not appear immediately.

## Use

Ask Codex to use `$refine` on a committed spec, plan, or `<base>...HEAD` implementation range. For example: `Use $refine on docs/specs/my-feature.md --rounds 6`. The controller records each round in `docs/superpowers/reviews/<date>-<topic>/` and makes path-limited commits. See [SKILL.md](SKILL.md) for the full workflow.

On Windows, use `C:/Program Files/Git/bin/bash.exe` for the shell scripts. Run `python -m unittest discover -s tests -t .` to test the helper scripts. `probe.sh` checks Codex CLI JSON and schema support against a trusted worktree.

## Credits and license

Adapted from [refine-skill](https://github.com/GregProuty/refine-skill) by Greg Prouty. MIT license; see [LICENSE](LICENSE).
