# Project IRONLOOP - Git Safety Cleanup Playbook
Last updated: 2026-03-07
Scope: Safe, non-destructive repo cleanup and commit workflow.

## Core Rules (Always)
- Do not run destructive cleanup commands (`git reset --hard`, `git clean -fd`) unless explicitly approved.
- Never touch the `engine-sim` submodule state unless that is the active task.
- Stage by explicit file paths only.
- Commit in small scoped chunks (single concern per commit).

## 1) Snapshot Current State
Run:
```powershell
git status --short
git diff --name-only
git ls-files --others --exclude-standard
```

Goal:
- See tracked modifications
- See untracked files
- Decide exact commit scope before staging

## 2) Pick a Safe Commit Scope
Choose one scope only:
- `docs-only`
- `bridge-only`
- `pinout-only`
- `roadmap-only`

Do not mix unrelated changes in one commit.

## 3) Stage Only Intended Files
Example:
```powershell
git add -- docs/roadmap/roadmap-progression-log.md
git add -- docs/guides/me7-bench-order-guide.html
```

## 4) Verify Staged Content Before Commit
Run:
```powershell
git status --short
git diff --cached --stat
git diff --cached
```

Confirm:
- only intended files are staged
- no unrelated changes slipped in

## 5) Commit with a Precise Message
Example:
```powershell
git commit -m "Update ME7 bench order guide with AK pin-confidence workflow"
```

## 6) Update Progress Log Immediately
After every commit, add a short entry in:
- `docs/roadmap/roadmap-progression-log.md`

Use this format:
```text
- Commit <hash>: <short description> (scope: docs|bridge|pinout|roadmap)
```

## 7) Push Only When Scope Is Confirmed
Run:
```powershell
git push origin main
```

If push fails due to environment/sandbox constraints, re-run with approved escalation path.

## 8) Weekly Hygiene (Non-Destructive)
- Review recurring junk/unwanted files and add targeted ignore rules.
- Keep ignore entries narrow (avoid broad patterns that hide real project files).
- Re-check that `docs/` remains canonical for website content.

## Quick Safety Checklist
- [ ] I reviewed `git status --short` first.
- [ ] I staged explicit paths only.
- [ ] I checked `git diff --cached` before commit.
- [ ] I left unrelated local changes untouched.
- [ ] I logged the commit in roadmap progression notes.
