# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A distributable agent Skill, `skills/directing-stickman-videos/`, plus the READMEs/assets that advertise it. A second, workflow-only skill, `skills/stickman-flow-pipeline/` (topic → Antigravity images → Google Flow clips → SFX pack), reuses the first skill's style rules and audio library and has no tests. It is mostly instruction documents (`SKILL.md` + `references/`) with a local Node/Python runtime for the Autopilot (B) styles. Video work done *with* the skill belongs outside this repo, not inside it.

## Commands

Skill runtime (run from `skills/directing-stickman-videos/`; Node 20+, FFmpeg/FFprobe required):

```bash
npm ci
node scripts/autopilot.mjs doctor              # dependency check; add --style B6 for B6
npm test                                       # node --test tests/*.test.mjs
node --test tests/runtime.test.mjs             # single Node test file
node --test tests/b5-art-kit.test.cjs          # .cjs file is NOT matched by the npm test glob
python3 tests/b6_puppet_test.py                # Python tests are standalone *_test.py scripts; need Pillow
python3 -m unittest discover -s tests -p 'test_a6_references.py'
python3 scripts/a6_reference_check.py          # A6 asset integrity (offline, no quality verdict)
```

Repo-level README/contract checks (run from repo root):

```bash
bash tests/verify-readmes.sh                   # runs the verify-*.py README/onboarding checks
python3 tests/verify-localized-readmes.py README.ja.md   # one localized README
python3 tests/verify-ab-preservation.py        # sha256 baseline of A1–A5 reference files
bash scripts/optimize-readme-previews.sh       # regenerate README preview GIFs (needs ffmpeg)
```

There is no lint or build step.

## Architecture

- `skills/directing-stickman-videos/SKILL.md` is a deliberately compact router. Detail lives in `references/`; `references/mode-execution-boundaries.md` holds the routing rules the router omits. Read the router, then only the references for the selected style.
- **Two modes that must not leak into each other.**
  - **A · Director** (A1–A5, plus A6 Amber Noir): produces approved storyboards and standalone video-generation prompts (Omni Flash contract in `omni-flash-prompt-contract.md`). A6 has its own rules (`amber-noir.md`, `a6-reference-prompts.md`, `a6-finishing.md`, `scripts/a6_finish.py`) and bypasses the A1–A5 contract.
  - **B · Autopilot** (B1–B6): produces a finished narrated MP4 locally via `scripts/autopilot*.mjs` and `b-style-*.mjs`. B5 uses its own renderer (`character-explainer.mjs`, `b5-*`), B6 its own runtime (`b6-dynamic-meme.mjs`, `b6_*.py`); neither is a manifest-v1 style, so never alias them to B1–B4.
  - A rules do not apply to B and vice versa; each style owns its captions, voice, pacing and SFX.
- `assets/` holds per-style reference images, audio library (`b-audio-library/` with license evidence) and fonts. `examples/` holds runnable B1/B5 projects. Autopilot output goes to a project-local `output/` or `autopilot-work/` (gitignored).
- `docs/superpowers/` contains historical plans/specs, not live requirements.

## Things that break tests

- `tests/verify-ab-preservation.py` pins sha256 hashes of `style-catalog.md`, `voice-continuity.md`, `omni-flash-prompt-contract.md`, `examples.md`, etc. Editing those A1–A5 references fails it unless the change is a recorded owner-directed baseline revision in that script.
- The 10 localized READMEs (`README*.md`, `CHANGELOG.zh-CN.md`) are validated for structure: HTML comment markers such as `<!-- b3:hero:start -->`, the `road-to-10000-stars--creator-ecosystem` anchor, link counts and demo asset presence. Change all language editions consistently and rerun `tests/verify-readmes.sh`.
- B-style approvals bind to the runtime version: changing the runtime invalidates prior preview approvals by design.
