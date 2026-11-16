# Refine: Claude Code by default

Harden a spec, plan, or implementation through independent review rounds. Claude Code Opus is the default reviewer; Codex or Claude Code can act as the controller. The legacy Codex CLI reviewer remains available as a compatibility option.

## Requirements

- Claude Code CLI (default reviewer) or Codex CLI (legacy reviewer)
- Either Codex or Claude Code as the controller
- Python 3, Git, and Bash (Git Bash on Windows)
- A repository with a clean index and committed subject

## Install

Run `python install.py --update` to install into Claude Code (`~/.claude/skills/refine`) and Codex (`$CODEX_HOME/skills/refine`, or `~/.codex/skills/refine`).

## Use

Invoke `$refine` from either Claude Code or Codex on a committed spec, plan, or `<base>...HEAD` implementation range. Claude Code Opus runs each review round by default. See [SKILL.md](SKILL.md) for the workflow and [bin/run-round-claude.py](bin/run-round-claude.py) for the Claude runner.

Adapted from [Greg Prouty's refine-skill](https://github.com/GregProuty/refine-skill). MIT license; see [LICENSE](LICENSE).
