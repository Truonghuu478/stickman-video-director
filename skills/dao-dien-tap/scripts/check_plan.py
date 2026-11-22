"""Check an episode's shots.tsv before images are made and again after clips arrive.

Columns (tab-separated, header row required):
  shot    S01, S02 ... (a shot may appear twice if it is cut in two)
  clip    clips/S01.mp4 (relative to the episode folder; the file may not exist yet)
  flow_s  duration requested in Flow; one of the durations the live Flow UI offers
  in_s    planned in point inside the clip
  out_s   planned out point inside the clip
  beat    what the viewer sees in this segment, in one line
  turn    "yes" on the segment(s) where the character makes the story's choice

Errors stop production. Warnings are pacing advice that the director may overrule
with a reason written in FLOW.md.

  python3 check_plan.py shots.tsv --target 22
  python3 check_plan.py shots.tsv --markdown      # table to paste into FLOW.md
  python3 check_plan.py shots.tsv --clips         # after clips exist: compare with real files
"""

import argparse
import math
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cut import FPS, read_rows  # noqa: E402

COLUMNS = ("shot", "clip", "flow_s", "in_s", "out_s", "beat", "turn")


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def smallest_fitting(durations, needed):
    fitting = [d for d in durations if d >= needed]
    return min(fitting) if fitting else max(durations)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--target", type=float, help="planned final runtime in seconds")
    parser.add_argument("--durations", default="4,6,8,10",
                        help="clip durations the live Flow model offers (default 4,6,8,10)")
    parser.add_argument("--clips", action="store_true", help="also check the real clip files")
    parser.add_argument("--markdown", action="store_true", help="print the shot table for FLOW.md")
    args = parser.parse_args()

    durations = sorted(float(d) for d in args.durations.split(","))
    errors, warnings = [], []
    try:
        header, rows = read_rows(args.plan)
    except (OSError, ValueError) as error:
        print(f"ERROR {error}")
        return 1
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        print(f"ERROR {args.plan}: missing columns {', '.join(missing)}; need {' '.join(COLUMNS)}")
        return 1

    root = args.plan.resolve().parent
    film = 0
    table = []
    turns = 0
    for index, row in enumerate(rows):
        where = f"line {row['_line']} ({row['shot'] or '?'})"
        try:
            flow, start, end = (float(row[k]) for k in ("flow_s", "in_s", "out_s"))
        except ValueError:
            errors.append(f"{where}: flow_s, in_s and out_s must be numbers")
            continue
        if not row["shot"]:
            errors.append(f"{where}: shot code is empty")
        if not row["beat"]:
            errors.append(f"{where}: beat is empty; say what the viewer sees")
        if flow not in durations:
            errors.append(f"{where}: flow_s {flow:g} is not an offered duration "
                          f"({', '.join(f'{d:g}' for d in durations)})")
        if not (0 <= start < end <= flow):
            errors.append(f"{where}: need 0 <= in_s < out_s <= flow_s")
            continue
        kept = end - start
        if kept < 0.5:
            errors.append(f"{where}: keeps {kept:.2f}s; under 0.5s does not read")
        is_turn = row["turn"].lower() in ("yes", "y", "x", "1", "true")
        if is_turn:
            turns += 1
            if kept < 1.0:
                errors.append(f"{where}: the turn is on screen for {kept:.2f}s; give the choice >= 1s")
        # Pacing: Veo spreads one action over the whole clip, so an oversized clip plays slow.
        if flow > durations[0] and kept / flow < 0.5:
            better = smallest_fitting(durations, kept + 1.0)
            if better < flow:
                warnings.append(f"{where}: keeps {kept:.1f}s of a {flow:g}s clip; "
                                f"request {better:g}s so the action is not stretched")
        if index == 0 and kept > 3.0:
            warnings.append(f"{where}: first segment is {kept:.1f}s; the hook should land by ~2s")
        if kept > 4.5 and index != len(rows) - 1:
            warnings.append(f"{where}: {kept:.1f}s on one shot; check it is not dead time")
        if args.clips:
            clip = (root / row["clip"]).resolve()
            if not clip.is_file():
                errors.append(f"{where}: clip not found: {row['clip']}")
            else:
                real = probe_duration(clip)
                if real is None:
                    errors.append(f"{where}: cannot read {row['clip']}")
                elif round(real * FPS) < round(end * FPS):
                    errors.append(f"{where}: {row['clip']} is {real:.2f}s, shorter than out_s {end:g}")
                elif abs(real - flow) > 0.5:
                    warnings.append(f"{where}: {row['clip']} is {real:.2f}s but flow_s says {flow:g}; "
                                    "record what Flow actually returned")
        frames = round(end * FPS) - round(start * FPS)
        table.append((row["shot"], f"{flow:g} s", f"{start:g}–{end:g}",
                      f"{film / FPS:.1f}–{(film + frames) / FPS:.1f}",
                      "**yes**" if is_turn else "", row["beat"]))
        film += frames

    if turns == 0:
        errors.append("no segment has turn=yes: mark where the character makes the story's choice; "
                      "a choice that happens between two clips is invisible")
    total = film / FPS
    if args.target is not None and round(args.target * FPS) != film:
        errors.append(f"edit is {total:.3f}s; target is {args.target:g}s")
    if not 12 <= total <= 40:
        warnings.append(f"edit is {total:.1f}s; short stories on TikTok usually sit between 12 and 40s")

    if args.markdown:
        print("| Shot | Flow duration | Keep (source s) | Film (s) | Turn | Beat |")
        print("| --- | --- | --- | --- | --- | --- |")
        for cells in table:
            print("| " + " | ".join(cells) + " |")
        print(f"\nTotal: {total:.2f} s ({film} frames at {FPS} fps)\n")
    for message in errors:
        print(f"ERROR {message}")
    for message in warnings:
        print(f"WARN  {message}")
    if not errors:
        print(f"OK    {len(rows)} segments, {total:.2f}s, {turns} turn segment(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
