---
name: stickman-flow-pipeline
description: Make a TikTok stickman short film (topic -> story beats -> scene images -> Google Flow clips -> sound-effect plan) using 9Router Antigravity images, Flow Omni Flash 1.2 and this repo's bundled SFX library. Use when the user wants a short stickman or Amber Noir film scene by scene with images fed into Google Flow. Ends at QC'd clips plus an SFX pack; the user edits the final video in ChatGPT, never CapCut.
---

# Stickman → Flow pipeline (TikTok short film)

Runs inside this repo. Style rules live in the sibling skill `skills/directing-stickman-videos` (default style **A6 Amber Noir**; read `references/amber-noir.md` and `references/a6-reference-prompts.md` once per session). Do not edit the repo for a project.

Project folder (outside the repo): `/Users/truongle/Documents/me/AI-tools/stickman-video-projects/<slug>/` with `flow-input/`, `clips/`, `qc/`, `audio/`, `FLOW.md`, `sfx-plan.md`.

## Fixed choices (do not re-ask)
- Format: **TikTok short film**, 9:16, default 30s, 5 shots. Reply in Vietnamese; image and Flow prompts in English.
- Images: **only** `ag/gemini-3.1-flash-image` via `skills/stickman-flow-pipeline/gen-frame.sh`. Never `cx/gpt-image-*`.
- Video: user generates clips in **Google Flow, Omni Flash 1.2, 9:16, 1 output, image in the Start frame only (End empty)**.
- Audio scope now: **sound effects only**. Narration (voice) and captions are deferred to a later session because no resource is set up (no `GEMINI_API_KEY`, no 9Router TTS model, Pillow missing for `a6_finish.py` when last checked). Do not write narration, do not promise captions, do not claim they work without checking.
- Final video: user edits in ChatGPT. No CapCut prompts, no assembly unless asked.

## Steps
1. **Collect once** (AskUserQuestion, skip what is given): topic (or propose 3 youth-relatable ones), duration (default 30s). Style A6.
2. **Proposal** (no cost): premise, one cast card, 5 shots with one-line story beat each (the story must read visually, since there is no voice yet), planned SFX per shot. Get approval.
   - TikTok: hook visible in shot 1 (first 1–2s), one clear emotional turn, an ending that rewards a rewatch. Keep the subject in the upper two-thirds and away from the right edge, where TikTok's UI covers the frame (approximate; not verified against the current app).
3. **Cast anchor**: one full character description pasted verbatim into every image prompt. Antigravity takes no reference image, so repetition is the only consistency tool.
4. **Images**: per shot run `skills/stickman-flow-pipeline/gen-frame.sh "<prompt>" <project>/flow-input/shotN.png` (generates, center-crops to 9:16, scales 720x1280). Shots in parallel with `&` + `wait`.
5. **Look before handing over**: ffmpeg `hstack=5` contact sheet, Read it. Regenerate shots with drift (hands, face, outfit, readable text).
6. **Write `FLOW.md`** in Vietnamese: Flow setup, per-shot upload + English motion prompt in code blocks, QC checklist, `open <folder>` command.
7. **User generates clips** into `clips/` (names may be `shortN.mp4`; accept either). Probe with ffprobe, build a frame-strip contact sheet (`fps=1/1.6,tile=5x1`, vstack), run `volumedetect`. Report per-clip verdicts honestly, including weak clips.
8. **SFX pack** (after clips are QC'd), from the repo's bundled library, run from `skills/directing-stickman-videos/`:
   - Per shot, pick the sounds the visible action causes: `node scripts/audio-library.mjs recommend --style B6 --beat <beat> --limit 3`. Beats that exist: `action, ambience, animal, applause, comic-cut, door, ending, horse, indoor-appliance, money, paper-handoff, prop-handoff, reaction, tension, warm, water`, plus `phone` and `rain` (they resolve via the `*` profile). `tension` and `warm` returned no SFX when tested.
   - `search <word>` prints tab-separated rows (`id kind category title`), not JSON, and misses many words (`lamp` returned nothing). Fall back to `list --category <cat> --limit N`.
   - Export the chosen IDs: `node scripts/audio-library.mjs export --ids id1,id2 --out <project>/audio`. This also writes `audio-selection.json` and `CREDITS.md`. CC-BY items need their credit kept; CC0 do not.
   - Write `sfx-plan.md`: table of shot, time in the final cut (shot start + offset), sound ID, level note (SFX under any later voice), and one line on what is deliberately silent.
   - Flow clips carry their own generated audio: tell the user to mute it in the final edit and use the SFX pack instead.
   - Say plainly that Claude cannot listen: IDs are chosen from metadata, so the user must audition them.
9. Stop. Narration and captions come in a later session; offer fixes only for failed shots.

## Image prompt template (worked)
`Flat 2D vector illustration, angular shapes, restrained cel shading, warm amber light and deep plum shadows. <ANCHOR>. Head is one solid matte-black circle with NO hair and NO skin, exactly two small cream-white oval eyes and one short cream line mouth, nothing else on the face. Hands are simple solid black mitten shapes, NOT realistic hands, no fingers. Slim solid black neck and limbs. <Wardrobe>. <Scene + action + camera framing>. No text, no watermark, no brick texture, no photorealism, no sketchy linework. No readable text on screens or paper.`

- A loose prompt gave realistic hands and a spotted face; keep the strict head/hands lines.
- Antigravity ignores `size`; ratio varies, hence the crop in `gen-frame.sh`.
- It frames tight: say "wide full-body shot, character in lower third" when the environment matters.

## Motion prompt template
`9:16 vertical, 2D illustrated animation in a warm amber and deep plum noir style, matching the first frame exactly. <character recap>. <ONE action and reaction>. <camera move>. The character does not speak; mouth stays a small closed line. No text, no captions, no speech bubbles, no style change.`

Lessons from the first run ("the-one-comment"):
- One action per clip. A vague "shadow grows larger" and a big camera tilt failed: the shadow stayed the same size and the character slid out of frame. Use a steady or slow-push camera when the character must stay visible.
- State the end state simply and early (the lamp was never switched off when buried in a long sentence).
- Flow outputs 8s clips with audio.
- On phones and notes always write "abstract scribbles, no readable text".
