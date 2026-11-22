---
name: stickman-flow-pipeline
description: Superseded by dao-dien-tap. Use dao-dien-tap for any stickman short film made with start frames and Google Flow clips.
---

# Superseded

This workflow was merged into [dao-dien-tap](../dao-dien-tap/SKILL.md) on 2026-11-22, because the two skills disagreed (30 s vs 20–30 s, approval gate vs none, mute Flow audio vs keep it, ChatGPT vs Remotion editing) and an agent following one was told to read the other.

Everything that was here now lives in dao-dien-tap:

- image generation, Flow settings, prompt templates and tested lessons: [flow-lessons](../dao-dien-tap/references/flow-lessons.md)
- sound effects, music bed, loudness and text: [finishing](../dao-dien-tap/references/finishing.md)
- `gen-frame.sh` moved to `../dao-dien-tap/scripts/gen-frame.sh`; the copy in this folder only forwards to it.

Invoke `dao-dien-tap` instead.
