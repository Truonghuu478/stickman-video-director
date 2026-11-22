"""Cut a Flow edit: check the plan, export Remotion props, or render picture + scene audio.

The plan is a tab-separated file with at least the columns clip, flow_s, in_s, out_s.
Extra columns (shot, beat, turn, ...) are allowed, so the same shots.tsv drives
check_plan.py, this script and finish.py.
"""

import argparse
import csv
import json
import math
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


FPS = 24
REQUIRED = ("clip", "flow_s", "in_s", "out_s")
FADE_FRAMES = 2  # short audio fade at every cut: removes clicks and ambience jumps


def read_rows(plan):
    """Return (header, rows) where rows are dicts with their source line number."""
    with plan.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        header = [name.strip() for name in (reader.fieldnames or [])]
        missing = [name for name in REQUIRED if name not in header]
        if missing:
            raise ValueError(f"{plan}: missing TSV columns {', '.join(missing)} "
                             f"(need {', '.join(REQUIRED)}; extra columns are allowed)")
        rows = []
        for line, row in enumerate(reader, 2):
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            if not any(row.values()):
                continue
            row["_line"] = line
            rows.append(row)
    if not rows:
        raise ValueError(f"{plan}: shot list is empty")
    return header, rows


def read_cuts(plan):
    cuts = []
    root = plan.resolve().parent
    for row in read_rows(plan)[1]:
        line = row["_line"]
        try:
            clip = row["clip"]
            length, start, end = (float(row[k]) for k in ("flow_s", "in_s", "out_s"))
            if not (4 <= length <= 10 and 0 <= start < end <= length):
                raise ValueError("expected 4..10 source seconds and 0 <= in < out <= flow_s")
            path = (root / clip).resolve()
            if not clip or Path(clip).is_absolute() or not path.is_relative_to(root):
                raise ValueError("clip must be a relative path in the episode folder")
            first, last = round(start * FPS), round(end * FPS)
            if first == last:
                raise ValueError("cut is shorter than one frame")
            cuts.append((path, first, last))
        except ValueError as error:
            raise ValueError(f"{plan}:{line}: {error}") from error
    return cuts


def stream_field(path, field, stream="v:0"):
    return subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", stream,
        "-show_entries", f"stream={field}", "-of", "csv=p=0", str(path),
    ], text=True).strip()


def render(cuts, destination, total_frames, fade_frames=FADE_FRAMES):
    if destination.exists():
        raise ValueError(f"Output already exists: {destination}")
    inputs, filters, labels = [], [], []
    fade = fade_frames / FPS
    for index, (path, first, last) in enumerate(cuts):
        if not path.is_file():
            raise ValueError(f"Missing clip: {path}")
        duration = float(stream_field(path, "duration"))
        if not math.isfinite(duration) or round(duration * FPS) < last:
            raise ValueError(f"{path}: actual picture ends before the planned cut")
        if not stream_field(path, "index", "a:0"):
            raise ValueError(f"{path}: add synchronized scene sound before rendering")
        video_start = float(stream_field(path, "start_time"))
        inputs.extend(["-i", str(path)])
        label = f"[v{index}]"
        filters.append(
            f"[{index}:v:0]setpts=PTS-STARTPTS,fps={FPS},trim=start_frame={first}:end_frame={last},"
            "setpts=PTS-STARTPTS,scale=720:1280:force_original_aspect_ratio=decrease,"
            f"pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p{label}"
        )
        # Keep the source A/V offset. At 48 kHz, each edit frame is 2000 samples.
        seconds = (last - first) / FPS
        fades = ""
        if fade > 0 and seconds > 2 * fade:
            fades = (f",afade=t=in:st=0:d={fade:.4f}"
                     f",afade=t=out:st={seconds - fade:.4f}:d={fade:.4f}")
        filters.append(
            f"[{index}:a:0]asetpts=PTS-({video_start})/TB,aresample=48000:async=1:first_pts=0,"
            f"aformat=channel_layouts=stereo,apad,atrim=start_sample={first * 2000}:"
            f"end_sample={last * 2000},asetpts=PTS-STARTPTS{fades}[a{index}]"
        )
        labels.extend([label, f"[a{index}]"])
    filters.append(f"{''.join(labels)}concat=n={len(cuts)}:v=1:a=1[picture][sound]")
    with TemporaryDirectory(dir=destination.parent) as temp:
        picture = Path(temp) / "picture.mp4"
        subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-copyts", *inputs,
            "-filter_complex", ";".join(filters), "-map", "[picture]", "-map", "[sound]",
            "-c:v", "libx264", "-crf", "16", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(picture),
        ], check=True)
        if int(stream_field(picture, "nb_frames")) != total_frames:
            raise ValueError("Encoded frame count differs from the shot list")
        # Publish only the verified file, without replacing another render.
        try:
            os.link(picture, destination)
        except OSError:  # file systems without hard links
            if destination.exists():
                raise ValueError(f"Output already exists: {destination}")
            os.rename(picture, destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--render", type=Path, metavar="OUTPUT.mp4")
    parser.add_argument("--target", type=float, help="expected final runtime in seconds")
    parser.add_argument("--remotion", action="store_true", help="print Remotion input props as JSON")
    args = parser.parse_args()
    try:
        cuts = read_cuts(args.plan)
        frames = sum(last - first for _, first, last in cuts)
        if args.target is not None and (not math.isfinite(args.target) or
                                        round(args.target * FPS) != frames):
            raise ValueError(f"Planned edit is {frames / FPS:.3f}s; expected {args.target}s")
        if args.render:
            render(cuts, args.render, frames)
        if args.remotion:
            root = args.plan.resolve().parent
            shots = [{"src": path.relative_to(root).as_posix(), "trimBefore": first,
                      "durationInFrames": last - first} for path, first, last in cuts]
            print(json.dumps({"shots": shots}, indent=2))
        else:
            print(f"{len(cuts)} shots, {frames} frames, {frames / FPS:.3f}s at {FPS} fps")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")
