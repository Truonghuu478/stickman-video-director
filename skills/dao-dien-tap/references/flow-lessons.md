# Start frames, Flow settings and prompt templates (A6)

Tested lessons from real episodes ("the-one-comment", "chan-am", "chiec-thuyen-giay-bia"). Read once in Phase 2. Style rules come from [amber-noir](../../directing-stickman-videos/references/amber-noir.md) and [a6-reference-prompts](../../directing-stickman-videos/references/a6-reference-prompts.md): start-frame prompts fully expanded (style, cast, world, composition, constraints, no placeholders); motion prompts short.

## Start frames

**Generated** (new shot, new angle): `scripts/gen-frame.sh` calls 9Router image generation, always attaching the bundled A6 style image (`assets/a6/apartment-style-example.png`) as a style-only reference, then crops to 720×1280.

```bash
gen=<repo>/skills/dao-dien-tap/scripts/gen-frame.sh
bash "$gen" "<anchor prompt>" "$ep/flow-input/S05.png"                       # anchor first
bash "$gen" --ref "$ep/flow-input/S05.png" "<prompt>" "$ep/flow-input/S01.png" # others, parallel is fine
```

- The **anchor** is the shot that shows every recurring character clearly, full body. Redo it until the cast is right; it becomes the cast reference for the rest.
- References leak lighting and prop state (the anchor's lit lamp appeared in a shot that needed it off). State every prop state that differs from the anchor ("the lamp is switched OFF").
- Needs an `edit`+`multiImage` model; default `cx/gpt-image-2`; set `NINEROUTER_IMAGE_MODEL` to switch. Use the [9router-image skill](/Users/truongle/.9router/.agents/skills/9router-image/SKILL.md) to list models. If the provider is down or the model missing, report it; do not switch providers silently.
- The generator frames tight: say "wide full-body shot, character in lower third" when the room matters.

**Extracted** (continuation in the same space): take the real frame from the previous clip. Exact continuity, no cost.

```bash
ffmpeg -ss 4.25 -i "$ep/clips/S05.mp4" -frames:v 1 "$ep/flow-input/S05b.png"
```

**Look before Flow**: `ffprobe` each PNG (720×1280), build `qc/contact-sheet.jpg` (`ffmpeg ... hstack`), open it, check faces, mitten hands, clothing, props, eyelines, pre-action pose. Regenerate failures. Preserve frames that already pass.

### Start-frame prompt template

```
Flat 2D vector illustration in the style of the reference image, angular shapes, restrained cel shading, warm amber light and deep plum shadows. <CAST, verbatim>. Head is one solid matte-black circle with NO hair and NO skin, exactly two small cream-white oval eyes and one short cream line mouth, nothing else on the face. Hands are simple solid black mitten shapes, NOT realistic hands, no fingers. Slim solid black neck and limbs. <Wardrobe>. <World>. <Composition + the instant BEFORE the action>. <Prop states that differ from the anchor>. Vertical 9:16, key action in the upper two-thirds and away from the right edge. No text, no watermark, no captions, no readable text on screens or paper, no photorealism, no sketchy linework.
```

- One frame, one instant: the moment before the action. Never paste the whole story.
- Phones, notes, screens: "abstract shapes, no readable text".
- If the action needs a hand, the mitten must already be visible on or near the prop in the start frame.

## Google Flow settings

Veo 3.1 Fast if the live model list offers it (record the model actually used otherwise), portrait 9:16, 1 output, audio on, the shot PNG in **Start frame**, End frame empty, **duration from `flow_s` in shots.tsv**. The user generates clips and saves them as `clips/<shot>.mp4`.

## Motion prompt template

Two to four sentences of action, then the fixed anatomy lock and sound tail:

```
<Locked | slow push-in that stops> <shot size> of <place>, matching the first frame exactly; <one-sentence recap of the visible character and setting>. <ONE action>, <ONE reaction>; <simple end state, stated early>. <Any state that must not change: "the lamp stays off">. Keep the drawing exactly as the first frame: the face is only two cream oval eyes and one short line mouth, with no eyebrows, eyelids, nose or teeth; hands stay solid black mitten shapes with no fingers or thumbs; feet stay plain black shapes with no toes. <Room tone + one or two effects tied to visible sources>. The mouth stays a small closed line. No dialogue, narration, music, text or captions.
```

## Lessons (each cost a regeneration)

- One action per clip. Vague changes ("the shadow grows") and big camera tilts failed; the character slid out of frame.
- End state simple and early. Buried in a long sentence, "the lamp switches off" was ignored.
- Any state only shown in the start frame can drift: repeat it in the motion prompt ("the lamp stays off").
- Veo adds eyebrows, eyelids, fingers and toes when a character emotes or reaches. Keep the anatomy lock in every prompt; judge at phone size before failing a clip.
- Asking for a hand action whose mitten is not in the start frame makes Veo invent a realistic hand. Show the change through the body or the prop, or start with the mitten on the prop.
- Re-rolling the same prompt repeats the defect. Find the cause in the prompt and rewrite it first.
- Flow returns clips with a semi-transparent ✦ watermark in the lower right. `finish.py --remove-veo-mark` removes it and adds an AI label ([finishing](finishing.md)); keep key action away from that corner anyway.
- Flow audio is quiet room tone plus a few loud taps (one tile tap peaked at −0.2 dB). It is kept for sync, then lifted and limited in finishing; it is never the whole soundtrack.

## Clip QC

- `python3 scripts/check_plan.py shots.tsv --clips`.
- Strip per clip: `ffmpeg -i clips/S01.mp4 -vf "fps=4,scale=135:-1,tile=8x4" -frames:v 1 qc/strip-S01.jpg`; open it. Zoom on face, hands and feet at the reaction.
- Check the turn happens inside the kept range, adjust `in_s`/`out_s` to real frames, rerun check_plan.
- Audio: Claude cannot listen. Use `volumedetect` only to flag problems; mark listening as not checked.
- [video-clip-qc](../../video-clip-qc/SKILL.md) writes a separate correction report when the user wants one.
