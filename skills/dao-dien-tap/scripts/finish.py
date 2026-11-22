"""Finish an episode: cut the clips, lay a continuous sound bed, add timed effects and
on-screen hook/punchline text, then normalise loudness for TikTok/Reels.

  python3 finish.py shots.tsv --out final.mp4 \
      --bed <music.mp3> [--bed-offset 12] [--bed-rel -3] \
      [--sfx <purr.ogg>@19.5[@-4]] ... \
      [--hook "POV: Hà Nội trở lạnh lần đầu" --hook-end 2.5] \
      [--end-text "xin nghỉ 1 buổi chắc không sao" --end-start 20]

Audio: Flow scene sound is kept in sync with its picture, with a 2-frame fade at
every cut, lifted to a working level, mixed with the bed and effects, then
normalised to --lufs (default -14 LUFS integrated, -1.5 dBTP) in two passes.
Text: rendered with Pillow (Nunito 900, Vietnamese-safe) when available,
otherwise with ffmpeg drawtext. The script never overwrites an existing file.
--remove-veo-mark subtracts Flow's semi-transparent sparkle (assets/veo-mark-alpha.png)
and always adds a small on-screen AI label in its place, top left.
"""

import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cut import FPS, read_cuts, render, stream_field  # noqa: E402

CORE = HERE.parent.parent / "directing-stickman-videos"
FONT = CORE / "assets" / "fonts" / "Nunito.ttf"
LIBRARY = CORE / "assets" / "b-audio-library"
# Alpha of Flow's visible sparkle on 720x1280 exports (measured 2026-11-22 from 9 clips).
VEO_MASK = HERE.parent / "assets" / "veo-mark-alpha.png"
UNBLEND = "if(gt(B,0),clip((A-B)/(1-B/255),0,255),A)"  # out = (in - a*255) / (1 - a)
W, H = 720, 1280
WORK_LUFS = -20.0


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def loudness(path, extra_filter=None, inputs=None):
    """Measure integrated loudness with loudnorm's analysis pass. Returns dict or None if silent."""
    if inputs is None:
        cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path),
               "-af", "loudnorm=print_format=json", "-f", "null", "-"]
    else:
        cmd = ["ffmpeg", "-nostdin", "-hide_banner", *inputs, "-filter_complex",
               extra_filter + ",loudnorm=print_format=json[m]", "-map", "[m]", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    found = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
    if not found:
        raise RuntimeError(f"loudness analysis failed:\n{err[-1500:]}")
    data = json.loads(found[-1])
    value = float(data["input_i"]) if data["input_i"] not in ("-inf", "inf") else -math.inf
    if not math.isfinite(value):
        return None
    return data


def peak_db(path):
    err = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path), "-af",
                          "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    match = re.search(r"max_volume:\s*(-?[\d.]+) dB", err)
    return float(match.group(1)) if match else 0.0


def library_credit(path):
    """Return a credit line if the file comes from the bundled audio library and needs one."""
    try:
        rel = Path(path).resolve().relative_to(LIBRARY.resolve()).as_posix()
    except ValueError:
        return None
    catalog = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
    items = catalog.get("items") if isinstance(catalog, dict) else catalog
    if items is None:
        items = next(v for v in catalog.values() if isinstance(v, list))
    for item in items:
        if item.get("path") == rel:
            licence = item.get("license", {}).get("id", "")
            if licence.startswith("CC0"):
                return None
            return (f"{item.get('title')} — {item.get('author')} "
                    f"({licence}, {item.get('source_url', '')})")
    return f"{rel}: not found in catalog.json, check its licence before publishing"


def text_png(text, out, y_frac, size, left=None):
    """Render outlined text on a transparent 720x1280 canvas (centred, or from x=left)."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(FONT), size)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= W * 0.84 or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    stroke = max(3, size // 9)
    height = sum(font.getbbox(l, stroke_width=stroke)[3] for l in lines) + (len(lines) - 1) * 8
    y = int(H * y_frac - height / 2)
    for l in lines:
        width = draw.textlength(l, font=font)
        x = (W - width) / 2 if left is None else left
        draw.text((x, y), l, font=font, fill=(255, 248, 235, 255),
                  stroke_width=stroke, stroke_fill=(20, 12, 24, 255))
        y += font.getbbox(l, stroke_width=stroke)[3] + 8
    canvas.save(out)


def has_pillow():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def drawtext(text, start, end, y_frac, size, left=None):
    escaped = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")
    x = "(w-text_w)/2" if left is None else str(left)
    return (f"drawtext=fontfile='{FONT}':text='{escaped}':fontsize={size}:fontcolor=0xFFF8EB:"
            f"borderw={max(3, size // 9)}:bordercolor=0x140C18:x={x}:"
            f"y=h*{y_frac}-text_h/2:enable='between(t,{start},{end})'")


def parse_sfx(spec):
    parts = spec.split("@")
    if len(parts) not in (2, 3):
        raise ValueError(f"--sfx {spec!r}: use path@seconds or path@seconds@gain_db")
    path = Path(parts[0]).expanduser()
    if not path.is_file():
        raise ValueError(f"--sfx file not found: {path}")
    return path, float(parts[1]), float(parts[2]) if len(parts) == 3 else 0.0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--target", type=float)
    parser.add_argument("--bed", type=Path, help="music or ambience that runs under the whole film")
    parser.add_argument("--bed-offset", type=float, default=0.0, help="start this many seconds into the bed")
    parser.add_argument("--bed-rel", type=float, default=-3.0,
                        help="bed level relative to the scene sound, dB (default -3)")
    parser.add_argument("--scene-max-gain", type=float, default=14.0,
                        help="cap on how much quiet Flow audio is lifted, dB (default 14)")
    parser.add_argument("--sfx", action="append", default=[], help="path@seconds[@gain_db]")
    parser.add_argument("--hook", help="text on screen from 0s (Vietnamese is fine)")
    parser.add_argument("--hook-end", type=float, default=2.5)
    parser.add_argument("--end-text", help="punchline text near the end")
    parser.add_argument("--end-start", type=float, help="when the end text appears (s)")
    parser.add_argument("--text-y", type=float, default=0.17, help="vertical centre of text, 0..1")
    parser.add_argument("--text-size", type=int, default=54)
    parser.add_argument("--lufs", type=float, default=-14.0)
    parser.add_argument("--remove-veo-mark", action="store_true",
                        help="remove Flow's visible sparkle by reverse alpha blending; "
                             "an on-screen AI label (--ai-label) is then always drawn")
    parser.add_argument("--ai-label", default="Video tạo bằng AI",
                        help="disclosure shown for the whole film when the Veo mark is removed")
    args = parser.parse_args()

    try:
        if args.out.exists():
            raise ValueError(f"Output already exists: {args.out}")
        if args.remove_veo_mark:
            if not args.ai_label.strip():
                raise ValueError("--remove-veo-mark needs a non-empty --ai-label: removing the "
                                 "provider's mark must leave a visible AI disclosure")
            if not VEO_MASK.is_file():
                raise ValueError(f"Mask missing: {VEO_MASK}")
        if (args.hook or args.end_text) and not FONT.is_file():
            raise ValueError(f"Font missing: {FONT}")
        if args.end_text and args.end_start is None:
            raise ValueError("--end-text needs --end-start")
        cuts = read_cuts(args.plan)
        frames = sum(last - first for _, first, last in cuts)
        if args.target is not None and round(args.target * FPS) != frames:
            raise ValueError(f"Planned edit is {frames / FPS:.3f}s; expected {args.target}s")
        duration = frames / FPS
        sfx = [parse_sfx(s) for s in args.sfx]
        args.out.parent.mkdir(parents=True, exist_ok=True)

        with TemporaryDirectory(dir=args.out.parent) as temp:
            temp = Path(temp)
            scene = temp / "scene.mp4"
            render(cuts, scene, frames)

            # 1. Levels: bring each stem to a working level before the mix.
            measured = loudness(scene)
            scene_gain = 0.0 if measured is None else max(
                -10.0, min(args.scene_max_gain, WORK_LUFS - float(measured["input_i"])))
            inputs = ["-i", str(scene)]
            # Flow sound is mostly faint room tone with a few loud taps: lift it, then
            # limit the taps so one transient cannot dominate the final normalisation.
            chains = [f"[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
                      f"volume={scene_gain:.2f}dB,alimiter=limit=0.5:attack=2:release=60:level=false[s0]"]
            labels = ["[s0]"]
            report = {"scene_lufs_raw": None if measured is None else float(measured["input_i"]),
                      "scene_gain_db": round(scene_gain, 2)}
            credits = []
            if args.bed:
                if not args.bed.is_file():
                    raise ValueError(f"--bed file not found: {args.bed}")
                bed_m = loudness(args.bed)
                bed_gain = 0.0 if bed_m is None else (WORK_LUFS + args.bed_rel) - float(bed_m["input_i"])
                inputs += ["-stream_loop", "-1", "-ss", f"{args.bed_offset}", "-i", str(args.bed)]
                fade_out = min(1.2, duration / 4)
                chains.append(
                    f"[1:a]atrim=0:{duration:.4f},asetpts=PTS-STARTPTS,"
                    f"afade=t=in:st=0:d=0.25,afade=t=out:st={duration - fade_out:.4f}:d={fade_out:.4f},"
                    f"volume={bed_gain:.2f}dB,aformat=sample_rates=48000:channel_layouts=stereo[s1]")
                labels.append("[s1]")
                report["bed_gain_db"] = round(bed_gain, 2)
                credit = library_credit(args.bed)
                if credit:
                    credits.append(credit)
            for path, at, gain in sfx:
                index = len(labels)
                inputs += ["-i", str(path)]
                level = -12.0 - peak_db(path) + gain  # effect peaks near -12 dBFS in the -20 LUFS working mix
                delay = max(0, int(round(at * 1000)))
                chains.append(
                    f"[{index}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                    f"adelay={delay}|{delay},volume={level:.2f}dB,apad,atrim=0:{duration:.4f}[s{index}]")
                labels.append(f"[s{index}]")
                credit = library_credit(path)
                if credit:
                    credits.append(credit)
            n = len(labels)
            mix = ";".join(chains)
            if n > 1:
                # amix divides by the input count; multiply back so stems keep their set levels.
                mix += f";{''.join(labels)}amix=inputs={n}:duration=first:dropout_transition=0,volume={n}"
            else:
                mix += ";[s0]anull"

            # 2. Two-pass loudness normalisation on the mix.
            first = loudness(None, extra_filter=mix, inputs=inputs)
            if first is None:
                norm = "anull"
            else:
                norm = (f"loudnorm=I={args.lufs}:TP=-1.5:LRA=11:measured_I={first['input_i']}:"
                        f"measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}:"
                        f"measured_thresh={first['input_thresh']}:offset={first['target_offset']}:"
                        "linear=true,aresample=48000")
            norm += ",aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
            graph = mix + f",{norm}[aout]"

            # 3. Picture: optional watermark removal, then text overlays.
            def next_input():
                return sum(1 for x in inputs if x == "-i")

            chain, last = [], "[0:v]"
            texts = []  # (text, start, end, y_frac, size, left)
            if args.remove_veo_mark:
                mask = next_input()
                inputs += ["-loop", "1", "-t", f"{duration:.4f}", "-i", str(VEO_MASK)]
                chain.append(f"[0:v]format=gbrp[vg];[{mask}:v]format=gray,format=gbrp[mk];"
                             f"[vg][mk]blend=all_expr='{UNBLEND}',format=yuv420p[clean]")
                last = "[clean]"
                texts.append((args.ai_label, 0.0, duration, 0.045, 24, 26))
                report["veo_mark"] = "removed; AI label shown for the whole film"
            if args.hook:
                texts.append((args.hook, 0.0, min(args.hook_end, duration), args.text_y, args.text_size, None))
            if args.end_text:
                texts.append((args.end_text, args.end_start, duration, args.text_y, args.text_size, None))
            if texts and has_pillow():
                for k, (text, start, end, y_frac, size, left) in enumerate(texts):
                    png = temp / f"text{k}.png"
                    text_png(text, png, y_frac, size, left)
                    index = next_input()
                    inputs += ["-loop", "1", "-t", f"{duration:.4f}", "-i", str(png)]
                    chain.append(f"{last}[{index}:v]overlay=0:0:enable='between(t,{start},{end})'[t{k}]")
                    last = f"[t{k}]"
                report["text_renderer"] = "pillow"
            elif texts:
                chain.append(last + ",".join(drawtext(t, s, e, y, z, x) for t, s, e, y, z, x in texts)
                             + "[td]")
                last = "[td]"
                report["text_renderer"] = "drawtext"
            reencode = bool(chain)
            video = ";".join(chain) + f";{last}format=yuv420p[vout]" if reencode else ""

            encoded = temp / "final.mp4"
            vcodec = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-r", str(FPS)] \
                if reencode else ["-c:v", "copy"]
            run(["ffmpeg", "-nostdin", "-v", "error", *inputs, "-filter_complex",
                 graph + (";" + video if reencode else ""), "-map", "[vout]" if reencode else "0:v",
                 "-map", "[aout]",
                 *vcodec, "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                 "-t", f"{duration:.4f}", "-movflags", "+faststart", str(encoded)])
            got = int(stream_field(encoded, "nb_frames"))
            if abs(got - frames) > 1:
                raise ValueError(f"Encoded {got} frames; plan has {frames}")
            final = loudness(encoded)
            report["final_lufs"] = None if final is None else float(final["input_i"])
            report["final_true_peak"] = None if final is None else float(final["input_tp"])
            report["frames"] = got
            report["seconds"] = round(got / FPS, 3)
            encoded.rename(args.out)
        if credits:
            report["credits_required"] = credits
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or ""
        parser.exit(1, f"{error}\n{detail[-1500:]}\n")


if __name__ == "__main__":
    main()
