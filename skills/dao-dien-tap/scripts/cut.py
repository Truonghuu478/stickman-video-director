"""Check a Flow shot list or assemble its silent picture edit with FFmpeg."""

import argparse
import csv
import math
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


FPS = 24


def read_cuts(plan):
    cuts = []
    root = plan.resolve().parent
    with plan.open(encoding="utf-8-sig", newline="") as source:
        rows = csv.reader(source, delimiter="\t")
        if next(rows, None) != ["clip", "flow_s", "in_s", "out_s"]:
            raise ValueError("Expected TSV header: clip, flow_s, in_s, out_s")
        for line, row in enumerate(rows, 2):
            try:
                clip, length, start, end = row
                length, start, end = map(float, [length, start, end])
                if not (4 <= length <= 10 and 0 <= start < end <= length):
                    raise ValueError("expected 4..10 source seconds and 0 <= in < out <= flow_s")
                path = (root / clip).resolve()
                if not clip.strip() or Path(clip).is_absolute() or not path.is_relative_to(root):
                    raise ValueError("clip must be a relative path in the episode folder")
                first, last = round(start * FPS), round(end * FPS)
                if first == last:
                    raise ValueError("cut is shorter than one frame")
                cuts.append((path, first, last))
            except ValueError as error:
                raise ValueError(f"{plan}:{line}: {error}") from error
    if not cuts:
        raise ValueError("Shot list is empty")
    return cuts


def video_field(path, field):
    return subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", f"stream={field}", "-of", "csv=p=0", str(path),
    ], text=True).strip()


def render(cuts, destination, total_frames):
    if destination.exists():
        raise ValueError(f"Output already exists: {destination}")
    inputs, filters, labels = [], [], []
    for index, (path, first, last) in enumerate(cuts):
        if not path.is_file():
            raise ValueError(f"Missing clip: {path}")
        duration = float(video_field(path, "duration"))
        if not math.isfinite(duration) or round(duration * FPS) < last:
            raise ValueError(f"{path}: actual picture ends before the planned cut")
        inputs.extend(["-i", str(path)])
        label = f"[v{index}]"
        filters.append(
            f"[{index}:v:0]setpts=PTS-STARTPTS,fps={FPS},trim=start_frame={first}:end_frame={last},"
            "setpts=PTS-STARTPTS,scale=720:1280:force_original_aspect_ratio=decrease,"
            f"pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p{label}"
        )
        labels.append(label)
    filters.append(f"{''.join(labels)}concat=n={len(cuts)}:v=1:a=0[picture]")
    with TemporaryDirectory(dir=destination.parent) as temp:
        picture = Path(temp) / "picture.mp4"
        subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-xerror", *inputs,
            "-filter_complex", ";".join(filters), "-map", "[picture]", "-an",
            "-c:v", "libx264", "-movflags", "+faststart", str(picture),
        ], check=True)
        if int(video_field(picture, "nb_frames")) != total_frames:
            raise ValueError("Encoded frame count differs from the shot list")
        # Publish only the verified file, without replacing another render.
        os.link(picture, destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--render", type=Path, metavar="OUTPUT.mp4")
    args = parser.parse_args()
    try:
        cuts = read_cuts(args.plan)
        frames = sum(last - first for _, first, last in cuts)
        if args.render:
            render(cuts, args.render, frames)
        print(f"{len(cuts)} shots, {frames} frames, {frames / FPS:.3f}s at {FPS} fps")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")
