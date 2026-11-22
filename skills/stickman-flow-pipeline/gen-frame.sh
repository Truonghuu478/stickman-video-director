#!/usr/bin/env bash
# Usage: gen-frame.sh [--ref cast.png]... [--no-style-ref] "<full prompt>" <out.png> [ratio_w ratio_h]   (default 9 16)
# Generates via 9Router with reference images, then center-crops to ratio and scales to 720x1280 (9:16).
# Image 1 is always the bundled A6 style reference (drawing method only), unless --no-style-ref.
# Each --ref is a cast/identity reference (e.g. an approved earlier shot): keep that character identical.
# Needs a model with the `edit`+`multiImage` capability (default cx/gpt-image-2).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd -P)
style="$here/../directing-stickman-videos/assets/a6/apartment-style-example.png"
refs=(); use_style=1
while [[ ${1:-} == --* ]]; do
  case $1 in
    --ref) refs+=("$2"); shift 2 ;;
    --no-style-ref) use_style=0; shift ;;
    *) echo "unknown flag $1" >&2; exit 2 ;;
  esac
done
prompt=$1; out=$2; rw=${3:-9}; rh=${4:-16}
set -a; source ~/.9router/.agents/9router.env; set +a
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

files=(); pre=""
if [[ $use_style == 1 ]]; then
  [[ -r $style ]] || { echo "missing style reference $style" >&2; exit 1; }
  files+=("$style")
  pre="Image 1 is a STYLE reference only: copy its drawing method, proportions, flat angular shapes, restrained cel shading, amber light and deep plum shadows. Do NOT copy its character, outfit, room or props. "
fi
for r in "${refs[@]+"${refs[@]}"}"; do
  [[ -r $r ]] || { echo "missing reference $r" >&2; exit 1; }
  files+=("$r")
  pre+="Image ${#files[@]} is the approved CAST reference: keep this exact character (head, face marks, outfit colors, proportions) identical; only pose, setting and action change. "
done

# base64 goes through files (--rawfile/--slurpfile): large inline args hit "argument list too long".
: > "$tmp/imgs.jsonl"
i=0
for f in "${files[@]+"${files[@]}"}"; do
  case ${f##*.} in jpg|jpeg|JPG|JPEG) mime=jpeg ;; *) mime=png ;; esac
  { printf 'data:image/%s;base64,' "$mime"; base64 < "$f" | tr -d '\n'; } > "$tmp/b$i"
  jq -n --rawfile b "$tmp/b$i" '$b' >> "$tmp/imgs.jsonl"
  i=$((i+1))
done

jq -n --arg p "$pre$prompt" --arg model "${NINEROUTER_IMAGE_MODEL:-cx/gpt-image-2}" --slurpfile imgs "$tmp/imgs.jsonl" \
  '{model:$model,prompt:$p} + (if ($imgs|length)>0 then {images:$imgs} else {} end)' > "$tmp/req.json"
curl -fsS -X POST "${NINEROUTER_URL:-http://127.0.0.1:20128}/v1/images/generations?response_format=binary" \
  -H "Authorization: Bearer $NINEROUTER_KEY" -H "Content-Type: application/json" -d @"$tmp/req.json" -o "$tmp/raw" --max-time 300
ffmpeg -loglevel error -y -i "$tmp/raw" \
  -vf "crop='if(gt(iw/ih,$rw/$rh),ih*$rw/$rh,iw)':'if(gt(iw/ih,$rw/$rh),ih,iw*$rh/$rw)',scale=720:1280" "$out"
echo "$out $(ffprobe -v error -show_entries stream=width,height -of csv=p=0 "$out")"
