---
name: dao-dien-tap
description: Direct one 15–30 second silent stickman short (A6 Amber Noir by default) for Vietnamese TikTok/Reels viewers aged 16–28, from pitch to finished MP4. Pitches three stories and waits for the user's pick, then plans shots with explicit Flow durations, makes start frames, prepares Google Flow prompts, checks clips, and finishes with music, hook text and loudness. Also use to continue or re-cut an existing episode.
---

# Direct one episode

One invocation = one standalone episode, 9:16, usually 15–30 s. The audience is Vietnamese, 16–28, scrolling. Episodes live in `../stickman-video-projects/doi-thuong/<YYYY-MM-DD>-<slug>/` relative to the repository root (new dated folder per episode; reopen the named one to continue).

**Languages.** Talk with the user in their language. Think, pitch and write the story in **Vietnamese**: the jokes and details live in Vietnamese. Only image and motion prompts are English.

**Why this skill is shaped this way.** The first episodes looked good and were still unwatchable: the film was near silent (−33 and −46 LUFS), every choice the character made happened between two clips, every shot was requested at 8 s and played slow, and the endings were the first idea. Each phase below exists to stop one of those failures. Read [gold-episodes](references/gold-episodes.md) once to see the difference.

## Phase 1 · Pitch, then stop

Read [story-craft](references/story-craft.md) and [gold-episodes](references/gold-episodes.md). Do **not** read the A6, Flow or prompt references yet: production limits are not allowed to shape the first ideas. Use the user's topic if given; otherwise pick everyday moments from their life (see story-craft) and optionally check [trends](references/trends.md) for timing. Before choosing, read the **Episode signature** line of every `*/FLOW.md` in `doi-thuong/` and do not repeat a conflict + ending pair.

Write **three pitches** in Vietnamese, each on a different engine (e.g. escalation comedy, reversal, small sacrifice). For each pitch:

- **Tên** and **logline** in one sentence that contains a choice and a turn.
- **Beats**: 5–8 numbered lines of visible action. Mark the beat where the character chooses as **[LỰA CHỌN]** and the last beat as **[CÚ LẬT]**.
- **Giây đầu**: the first image and the optional hook text (≤ 8 words).
- **Câu chốt** on screen at the end, if the turn needs one (≤ 10 words).
- **Gửi cho ai**: who a viewer would send it to, and why.
- **Tự chấm**: run the five tests in story-craft and say honestly which one is weakest.

Recommend one, then **stop and wait** for the user to choose or edit. This is the cheapest place to throw a story away. Continue without waiting only when the user said to decide yourself ("tự chọn", "auto") or the session is unattended; then state which pitch you took and why at the top of FLOW.md.

## Phase 2 · Shot plan

Now read [shot-plan](references/shot-plan.md), [flow-lessons](references/flow-lessons.md), and the A6 style files [amber-noir](../directing-stickman-videos/references/amber-noir.md) and [a6-reference-prompts](../directing-stickman-videos/references/a6-reference-prompts.md) (A6 is the default; use another style only when the user names it, through [directing-stickman-videos](../directing-stickman-videos/SKILL.md)).

**What to take from A6, and what this skill overrides.** Take A6's drawing grammar, reference handling and fully expanded start-frame prompts. Ignore A6's finishing and production flow: no Gemini Puck narration, no uppercase captions, no persistent upper-left title, no `a6_finish.py`, and no separate trial/credit-budget gate (the user generates clips in Flow; Phase 1 is the approval). Sound and text come only from Phase 5 `finish.py`.

1. Write `shots.tsv` (format in shot-plan). Every row has a **Flow duration chosen from the durations the live Flow UI offers** (ask or check; 4/6/8/10 s when unknown), sized to the action, never 8 s by habit.
2. Every **[LỰA CHỌN]** beat is a row with `turn=yes` and at least 1 s on screen. A choice that happens between two clips is invisible.
3. Run `python3 scripts/check_plan.py <episode>/shots.tsv --markdown`. Fix every ERROR. Fix WARNs or write one line in FLOW.md on why you keep them.
4. Write `FLOW.md`: title, **Episode signature** (*setting | want | obstacle | ending*), source trend or "none", the chosen pitch's beats, the shot table printed by check_plan (it carries the durations), appearance/world/prop locks, then per shot: start-frame source, one Start-frame prompt and one Motion prompt in separate code blocks (templates in flow-lessons). End with the finish command from [finishing](references/finishing.md).

## Phase 3 · Start frames

Default: one 720×1280 PNG per new shot in `flow-input/`, made with `scripts/gen-frame.sh` (anchor shot first, then the others with `--ref`; details in flow-lessons). When a shot continues the previous one in the same space, use the **real last frame of the previous clip** instead (`ffmpeg -ss <t> -i clips/SXX.mp4 -frames:v 1 flow-input/SYY.png`): it matches exactly and costs nothing. Build `qc/contact-sheet.jpg`, look at it, regenerate failures. Report the folder when every frame passes.

## Phase 4 · Clips

The user makes clips in Google Flow (settings in flow-lessons) and puts them in `clips/` as `<shot>.mp4`. Then:

- `python3 scripts/check_plan.py shots.tsv --clips` (real durations, files present).
- Look at real frames: a 4 fps strip per clip, and zooms on face, hands and feet at the reaction. Move `in_s`/`out_s` to where the action really happens; the turn must stay inside the kept range.
- A failed clip: find the prompt cause, rewrite, regenerate. Re-rolling the same prompt repeats the defect.

## Phase 5 · Finish and publish

Render with `scripts/finish.py` ([finishing](references/finishing.md)): cuts, a continuous music or ambience bed, timed effects, hook and punchline text, −14 LUFS. Never deliver an episode with only Flow room tone. Check the printed report (frames, LUFS, credits), make a 1–2 fps contact sheet of the result and look at it, then write `POST.md` with [dang-bai-tiktok-reels](../dang-bai-tiktok-reels/SKILL.md), including any required music credit. Claude cannot listen: ask the user to watch once with sound before posting, and report what was not checked.

## Rules that are not negotiable

- Characters are silent by default (Flow did not keep mouths stable). If the user wants dialogue, warn about mouth sync and voice drift, then follow [voice-continuity](../directing-stickman-videos/references/voice-continuity.md).
- No readable text generated inside images or clips; on-screen words are added only in finishing.
- The Flow/Veo ✦ mark may be removed only with `finish.py --remove-veo-mark`, which always puts a visible "Video tạo bằng AI" label on screen instead (Vietnam's AI Law requires AI-generated video to be recognisably labelled). Also switch on the platform's AI-generated label.
- Music and effects come from the bundled licensed library or files the user owns; keep CC BY credits.
- Do not claim audience reactions or "viral" potential; say what you checked and what you did not.
