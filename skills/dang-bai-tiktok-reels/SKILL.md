---
name: dang-bai-tiktok-reels
description: Write TikTok and Facebook Reels publishing copy for a dao-dien-tap short episode, including cover text, platform captions, up to three hashtags including #xuhuong, a pinned comment and a cover frame.
---

# TikTok and Facebook Reels publishing copy

Input: an episode directory containing `FLOW.md` and, if available, `TRENDS.md`. If the user supplies only an episode description, use that. Output: **POST.md** in the episode directory, in Vietnamese by default (the audience is Vietnamese) or the user-specified output language. Posting is the user's task; do not publish automatically.

## Read before writing

From FLOW.md, identify the main interaction mechanism (share, comment, rewatch or save), the **Source trend** or legacy **Trend gốc** line, ending and best frame before the ending. From TRENDS.md, identify the trend name and hashtags actually used for it.

## POST.md contents

1. **Cover text:** at most eight words, naming a recognizable situation without revealing the ending.
2. **TikTok caption:** one line that can be read without expanding it. Open with the situation, use a conversational tone and slang only when natural. End with one invitation matching the chosen mechanism: for comments, a clear two-sided choice; for sharing, identify the kind of person to tag; for saving, say why the viewer might keep it.
3. **Facebook Reels caption:** the same idea rewritten for viewers unfamiliar with TikTok. Open with enough context, allow a slightly longer sentence, and invite sharing with friends or family. Avoid TikTok-specific slang.
4. **Hashtags:** at most three shared across both platforms. `#xuhuong` always comes first. Add one or two genuine trend tags from TRENDS.md. When there is no source trend, use `#xuhuong` and one specific topic tag. Do not pad with generic tags such as `#fyp`, `#viral` or `#foryou`.
5. **Pinned comment:** invite viewers to share their version of the situation or notice a background detail.
6. **Cover frame:** identify the shot code and source second with the clearest expression or pose before the ending.
7. **Credits:** copy every `credits_required` line printed by `finish.py` (CC BY music or effects) into a `Credits` line ready to paste into the post description.
8. **AI label:** remind the user to switch on the platform's AI-generated content label. If the film was finished with `--remove-veo-mark`, note that its on-screen "Video tạo bằng AI" label must stay in the posted version.

## Completion checks

- Use one to three hashtags, including `#xuhuong`.
- No section reveals the ending.
- Each caption ends with exactly one invitation matching the interaction mechanism in FLOW.md.
- Cover text has at most eight words.
- Every CC BY credit from the finish report appears in POST.md.
