---
name: stickman-flow-pipeline
description: Make a TikTok stickman short film (topic, story beats, scene images, Google Flow clips and sound-effect plan) using 9Router images with the A6 style reference, Google Flow Veo 3.1 Fast and this repo's bundled SFX library. Use when the user wants a short stickman or Amber Noir film scene by scene with images fed into Google Flow. Ends at QC'd clips plus an SFX pack; the user edits the final video in ChatGPT, never CapCut.
---

# Stickman → Flow pipeline (TikTok short film)

Runs inside this repo. Style rules live in the sibling skill `skills/directing-stickman-videos` (default style **A6 Amber Noir**; read `references/amber-noir.md` and `references/a6-reference-prompts.md` once per session). Do not edit the repo for a project.

Project folder (outside the repo): `/Users/truongle/Documents/me/AI-tools/stickman-video-projects/<slug>/` with `flow-input/`, `clips/`, `qc/`, `audio/`, `FLOW.md`, `sfx-plan.md`.

## Fixed choices (do not re-ask)
- Format: **TikTok short film**, 9:16, default 30s, 5 shots. Write the production package and prompts in English by default; honor a user-specified output language. Reply in the conversation language.
- Images: use the installed [9router-image skill](/Users/truongle/.9router/.agents/skills/9router-image/SKILL.md) to discover image models and their capabilities. Default to `cx/gpt-image-2` via `skills/stickman-flow-pipeline/gen-frame.sh`; use another configured model when the user chooses it. A listed model is not proof that its provider is connected. If the skill or selected model is unavailable, report the blocker instead of silently changing providers.
- Video: user generates clips in **Google Flow, Veo 3.1 Fast (the model behind the accepted A6 sample), 9:16, 1 output, clips up to 8s, image in the Start frame only (End empty)**. Verify the live model list and durations in the Flow UI; if only Omni Flash is available, say so and note that A6 quality is unverified on it.
- Characters are **silent** (closed small mouth line). Flow supplies ambience and effects only; no dialogue, narration or music in the Flow prompt.
- Audio scope now: **sound effects only**. Narration (voice) and captions are deferred to a later session because no resource is set up (no `GEMINI_API_KEY`, no 9Router TTS model, Pillow missing for `a6_finish.py` when last checked). Do not write narration, do not promise captions, do not claim they work without checking.
- Final video: user edits in ChatGPT. No CapCut prompts, no assembly unless asked.

## Steps
1. **Collect once** (AskUserQuestion, skip what is given): topic (or propose 3 youth-relatable ones), duration (default 30s). Style A6.
2. **Proposal** (no cost): premise, one cast card, 5 shots with one-line story beat each (the story must read visually, since there is no voice yet), planned SFX per shot. Get approval.
   - TikTok: hook visible in shot 1 (first 1–2s), one clear emotional turn, an ending that rewards a rewatch. Keep the subject in the upper two-thirds and away from the right edge, where TikTok's UI covers the frame (approximate; not verified against the current app).
3. **Cast anchor**: one full character description pasted verbatim into every image prompt, plus the reference-image chain in step 4.
4. **Images** (reference-guided; text-only prompts drift away from the A6 look). `gen-frame.sh` always attaches `assets/a6/apartment-style-example.png` as a style-only reference (drawing method, light; not its character or room).
   - Anchor first: the shot that shows the whole cast clearly and full body (not necessarily shot 1). `gen-frame.sh "<prompt>" <project>/flow-input/shotK.png`. Redo until the cast is right; this approved frame becomes the cast reference.
   - Other shots (parallel is fine): `gen-frame.sh --ref <project>/flow-input/shotK.png "<prompt>" <project>/flow-input/shotN.png` (repeat `--ref` for more refs). The reference holds identity but also leaks lighting and prop states, so state every prop state that differs from the anchor ("the lamp is switched OFF").
   - Needs an `edit`+`multiImage` model (`cx/gpt-image-2` verified). Output is cropped to 720x1280; check framing. Preserve passing images if another request fails.
5. **Look before handing over**: ffmpeg `hstack=N` contact sheet, Read it. Regenerate shots with drift (hands, face, outfit, readable text).
6. **Write `FLOW.md`** in the selected output language: Flow setup, per-shot upload + English motion prompt in code blocks, QC checklist, `open <folder>` command.
7. **User generates clips** into `clips/` (names may be `shortN.mp4`; accept either). Probe with ffprobe, build a frame-strip contact sheet (`fps=1/1.6,tile=5x1`, vstack), run `volumedetect` (flag `max_volume` above about -1 dB). Zoom into face, hands and feet at the reaction moment: added eyebrows, eyelids, fingers and toes are the main failure. Before regenerating, rewrite the prompt cause; re-rolling the same prompt reproduced the same defect. Report per-clip verdicts honestly, including weak clips.
8. **SFX pack** (after clips are QC'd), from the repo's bundled library, run from `skills/directing-stickman-videos/`:
   - Per shot, pick the sounds the visible action causes: `node scripts/audio-library.mjs recommend --style B6 --beat <beat> --limit 3`. Beats that exist: `action, ambience, animal, applause, comic-cut, door, ending, horse, indoor-appliance, money, paper-handoff, prop-handoff, reaction, tension, warm, water`, plus `phone` and `rain` (they resolve via the `*` profile). `tension` and `warm` returned no SFX when tested.
   - `search <word>` prints tab-separated rows (`id kind category title`), not JSON, and misses many words (`lamp` returned nothing). Fall back to `list --category <cat> --limit N`.
   - Export the chosen IDs: `node scripts/audio-library.mjs export --ids id1,id2 --out <project>/audio`. This also writes `audio-selection.json` and `CREDITS.md`. CC-BY items need their credit kept; CC0 do not.
   - Write `sfx-plan.md`: table of shot, time in the final cut (shot start + offset), sound ID, level note (SFX under any later voice), and one line on what is deliberately silent.
   - Flow clips carry their own generated audio: tell the user to mute it in the final edit and use the SFX pack instead.
   - Say plainly that Claude cannot listen: IDs are chosen from metadata, so the user must audition them.
9. Stop. Narration and captions come in a later session; offer fixes only for failed shots.

## Image prompt template (worked)
`Flat 2D vector illustration in the style of the reference image, angular shapes, restrained cel shading, warm amber light and deep plum shadows. <ANCHOR>. Head is one solid matte-black circle with NO hair and NO skin, exactly two small cream-white oval eyes and one short cream line mouth, nothing else on the face. Hands are simple solid black mitten shapes, NOT realistic hands, no fingers. Slim solid black neck and limbs. <Wardrobe>. <Scene + action + camera framing>. No text, no watermark, no brick texture, no photorealism, no sketchy linework. No readable text on screens or paper.`

- A loose prompt gave realistic hands and a spotted face; keep the strict head/hands lines.
- Provider output ratios vary; inspect the crop produced by `gen-frame.sh`.
- Do not paste the whole story or a character-sheet into one prompt: one frame, one instant, the instant before the action.
- It frames tight: say "wide full-body shot, character in lower third" when the environment matters.

## Motion prompt template
`9:16 vertical, 2D illustrated animation in a warm amber and deep plum noir style, matching the first frame exactly. <character recap>. <ONE action and reaction>. <camera move>. The character does not speak; mouth stays a small closed line. Keep the drawing exactly as the first frame: the face is only two cream oval eyes and one short line mouth, with no eyebrows, eyelids, nose or teeth; hands stay solid black mitten shapes with no fingers or thumbs; feet stay plain black shapes with no toes. Quiet ambience and effects timed to the visible action; no dialogue, narration or music. No text, no captions, no speech bubbles, no style change.`

Keep it short (2-4 sentences): one action, one reaction, one camera move. A6's reference rules say not to paste a long screenplay into the motion field (`a6-reference-prompts.md`); the accepted sample used a short motion prompt over a shot-specific first frame. The first run's clip failures (see below) were also multi-action or vague-end-state prompts.

Lessons from the first run ("the-one-comment"):
- One action per clip. A vague "shadow grows larger" and a big camera tilt failed: the shadow stayed the same size and the character slid out of frame. Use a steady or slow-push camera when the character must stay visible.
- State the end state simply and early (the lamp was never switched off when buried in a long sentence).
- Flow outputs 8s clips with audio.
- On phones and notes always write "abstract scribbles, no readable text".

Lessons from "chan-am" (Veo 3.1 Fast, 2026-11-22):
- Style and cast held across all six clips, but the clip where the character reacted to a phone gained eyebrows, eyelids and a fingered hand reaching out. Keep the anatomy lock in every motion prompt, and do not ask for a hand action whose mitten is not already visible in the start frame.
- Repeat in the motion prompt any state that must hold during the clip ("the lamp stays off"); a lamp that was off only in the start frame came on.
