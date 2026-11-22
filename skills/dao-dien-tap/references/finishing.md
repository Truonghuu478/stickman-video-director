# Finishing: sound bed, text, loudness, delivery

`scripts/finish.py` turns `shots.tsv` and the clips into the deliverable. Run it from the episode folder:

```bash
S=<repo>/skills
L=$S/directing-stickman-videos/assets/b-audio-library/audio
python3 $S/dao-dien-tap/scripts/finish.py shots.tsv --out final.mp4 \
  --bed $L/music/bgm-easy-lemon.mp3 --bed-rel -2 \
  --sfx "$L/kerzoven-cat/cat_purrsleepy_loop.wav@22.0@-3" \
  --hook "POV: Hà Nội trở lạnh lần đầu" \
  --end-text "Thôi, nghỉ 1 bữa chắc không sao đâu" --end-start 22.6
```

What it does, in order:

1. Cuts every segment at 24 fps with its own Flow audio, adding a 2-frame audio fade at each cut (no clicks, no ambience jumps).
2. Lifts the Flow scene sound towards a −20 LUFS working level (at most +14 dB) and limits its loud taps.
3. Lays the bed from `--bed-offset`, looped if short, faded in and out, `--bed-rel` dB relative to the scene sound.
4. Places each `--sfx path@seconds[@gain_db]`.
5. Normalises the mix to −14 LUFS integrated, −1.5 dBTP (two passes).
6. Draws the hook (0 → `--hook-end`, default 2.5 s) and the punchline (`--end-start` → end) in Nunito 900, which covers Vietnamese.
7. Verifies frame count and prints a JSON report: scene and final loudness, true peak, and **credits_required** for any CC BY file.

It refuses to overwrite an existing output; render v2, v3… side by side.

## Choosing sound

- A silent-actor film needs a bed: music for comedy and warmth, ambience (rain, street, birds) for quiet drama. Room tone alone sounds broken on a phone.
- Music lives in `assets/b-audio-library/audio/music/` (Kevin MacLeod, CC BY 4.0, evidence in `evidence/`). Pick by mood tags in `catalog.json`:
  - warm or cozy: `bgm-easy-lemon`, `bgm-morning`, `bgm-bossabossa`
  - comedy: `bgm-quirky-dog`, `bgm-fluffing-a-duck`, `bgm-sneaky-snitch`, `bgm-monkeys-spinning-monkeys`
  - awkward or ironic: `bgm-local-forecast-elevator`, `bgm-merry-go`
  - sad or tender: `bgm-heartbreaking`
  - tension: `bgm-decisions`, `bgm-investigations`
- Effects: `node scripts/audio-library.mjs list --category <cat>` from `skills/directing-stickman-videos/` (categories include `animal-cat`, `cloth-foley`, `ambience`, `weather-rain`, `musical-stinger`). Place them on the visible cause, in film time (the shot table gives each shot's film start).
- `--bed-rel`: about −2 when music carries a silent film; −6 to −8 when scene effects should lead.
- Claude cannot listen. Pick from tags, say so, and offer two alternatives for the user to audition.

## Text

- Hook ≤ 8 words, punchline ≤ 10 words, Vietnamese, no emoji. Keep them in the top fifth of the frame (default `--text-y 0.17`), away from TikTok's right-side buttons and bottom caption.
- Text is added only here, never generated inside images or clips.

## Checks before delivery

- The JSON report: frames match the plan, final ≈ −14 LUFS, true peak ≤ −1 dBTP.
- Contact sheet of the result (`fps=1.5,scale=160:-1,tile=9x3`): open it; check every cut and that the text is readable and not over a face.
- Watermark: Flow/Veo output carries a semi-transparent ✦ at about x 576–623, y 1136–1183 (720×1280). `--remove-veo-mark` subtracts it exactly using `assets/veo-mark-alpha.png` (measured from 9 real clips; residue is invisible at phone size) and always draws a small "Video tạo bằng AI" label top left for the whole film (`--ai-label` changes the wording; it cannot be empty).
  - Why the label is mandatory: Google keeps the visible mark on in Vietnam (the Flow toggle that turns it off is not offered there), and Vietnam's AI Law (from 1 March 2026) requires AI-generated images and video to be labelled recognisably. The label replaces the mark's job. The invisible SynthID mark stays in the pixels either way.
  - Clean source alternative: Flow accounts where the "Visible watermarking" toggle or the Ultra plan applies export without the mark; then skip the flag but keep the platform's AI label on.
  - If Flow changes the mark's size or position, zoom on the corner of the result and re-measure the mask before using it.
  - Also switch on TikTok's / Facebook's AI-generated content label when posting.
- Credits: copy every `credits_required` line into POST.md and the post description.
- Report what was checked (frames, loudness, text) and what was not (listening, music fit, comedy timing).

## Remotion (optional)

`python3 scripts/cut.py shots.tsv --remotion > timeline.json` plus `assets/episode.jsx` reproduces the picture cut in Remotion for manual editing. It has no bed, effects or text; finish.py is the default deliverable.
