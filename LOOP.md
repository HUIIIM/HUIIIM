# Loop state — HUIIIM

Updated: 2026-11-01 (loop bootstrap). Facts here are the standing state;
when one changes, the PR that changes it updates this file.

## Direction channel

- Tasks: GitHub Issues labeled `jarvis-task` in this repo.
- Merge owner: Jarvis. External Claude opens PRs from `claude/*` branches.

## Decisions in force

- Display name: Jiahui Miao. Location: New York. Site: vertciti.com.
- The Claude GitHub App selection covers this repo (verified 2026-11-01).

## Acceptance rules

- Profile changes are read back on the rendered profile after merge.
- `README check` CI (`.github/workflows/readme-check.yml`) stays green: the profile
  README must render as written (no literal Markdown), every image has alt text,
  and outbound links are probed nightly. Run `python3 scripts/check_readme.py`
  before pushing a README change.
