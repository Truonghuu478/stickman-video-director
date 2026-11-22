# Shot plan: shots.tsv, durations, cuts

## shots.tsv

One tab-separated file per episode is the single source of truth for shots, durations and cuts. `check_plan.py`, `cut.py` and `finish.py` all read it.

```
shot	clip	flow_s	in_s	out_s	beat	turn
S01	clips/S01.mp4	4	0.5	2.5	Clock jumps to 23:50; he snaps upright from the desk	
S05	clips/S05.mp4	6	0.5	4.0	He drags the whole desk to the outlet	yes
```

- `flow_s`: the duration you will **request** in Flow for that clip. It must be one the live Flow model offers (check the UI; pass `--durations` to check_plan if it differs from 4,6,8,10).
- `in_s` / `out_s`: planned kept range inside the clip. Estimates until the clip exists; then set them from real frames.
- `beat`: what the viewer sees, one line, English (it is copied into prompts and QC).
- `turn`: `yes` on the segment(s) where the character makes the story's choice.
- A clip may appear in two rows when one clip is cut around an insert.

Run `python3 scripts/check_plan.py shots.tsv --markdown` and paste the printed table into FLOW.md. That table is how the durations reach the user; do not retype it.

## Choosing the Flow duration

Video models spread the requested action over the whole clip: an action that takes 2 s, requested at 8 s, comes back slow, floaty, or padded with idle motion. So:

1. Estimate how long the action takes at natural speed (time it with your own body).
2. Add about 0.5 s before (the clip needs to settle from the start frame) and 0.5–1 s after (room to cut).
3. Take the **smallest offered duration** that fits. Most single actions are 4 s; an action with a reaction is 6 s; 8–10 s only for a genuinely continuous longer action.
4. Plan to keep at least half of each clip. check_plan warns when you keep less.

If the user's Flow only offers one duration, write that in FLOW.md and plan tighter in/out points instead.

## Cutting rules

- **The choice is a clip, not a cut.** The segment with `turn=yes` shows the character deciding: the hesitation, the look, the act. ≥ 1 s on screen.
- **Hook by 2 s.** The first kept segment is ≤ 3 s and starts on movement or a readable face, not a dark static wide.
- **No dead time.** A kept segment over ~4.5 s needs a reason (a held reaction, the final image).
- **Continuous action across a cut**: use the previous clip's real last frame as the next clip's start frame (`ffmpeg -ss <t> -i clips/SXX.mp4 -frames:v 1 flow-input/SYY.png`). Lighting, props and positions then match exactly.
- **New angle**: decide what the viewer must see first. Wide shows where things are, medium shows a decision in hands, shoulders or feet, close shows the evidence or the reaction. Keep the camera axis and screen direction inside one space.
- **Time or place jumps** must be visually obvious (new light, new clothes, new room).
- Plan in/out points as estimates, then move them to the real frames once clips exist. If the decisive action lands outside the planned range, move the range; if it is missing, regenerate with a rewritten prompt.

## FLOW.md layout

1. Title, **Episode signature** (*setting | want | obstacle | ending*), **Source trend** (name, link, expiry) or "none".
2. The chosen pitch: logline and numbered beats in Vietnamese, with [LỰA CHỌN] and [CÚ LẬT] marked. If you chose without the user, say which pitch and why.
3. Shot table from `check_plan.py --markdown`, plus one line for any WARN you kept.
4. Locks: cast description (verbatim English, reused in every prompt), world, screen directions, a prop-state table across shots.
5. Per shot: start-frame source (generated or extracted frame and timestamp), Start-frame prompt, Motion prompt (templates in [flow-lessons](flow-lessons.md)).
6. QC notes per shot: what must be true in the kept range.
7. Finish: the exact `finish.py` command with music, effects, hook and punchline ([finishing](finishing.md)).
