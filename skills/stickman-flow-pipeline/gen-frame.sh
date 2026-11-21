#!/usr/bin/env bash
# Usage: gen-frame.sh "<full prompt>" <out.png> [ratio_w ratio_h]   (default 9 16)
# Generates via 9Router Antigravity, then center-crops to ratio and scales to 720x1280 (9:16).
set -euo pipefail
prompt=$1; out=$2; rw=${3:-9}; rh=${4:-16}
set -a; source ~/.9router/.agents/9router.env; set +a
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
jq -n --arg p "$prompt" '{model:"ag/gemini-3.1-flash-image",prompt:$p}' |
  curl -fsS -X POST "http://127.0.0.1:20128/v1/images/generations?response_format=binary" \
    -H "Authorization: Bearer $NINEROUTER_KEY" -H "Content-Type: application/json" -d @- -o "$tmp/raw"
ffmpeg -loglevel error -y -i "$tmp/raw" \
  -vf "crop='if(gt(iw/ih,$rw/$rh),ih*$rw/$rh,iw)':'if(gt(iw/ih,$rw/$rh),ih,iw*$rh/$rw)',scale=720:1280" "$out"
echo "$out $(ffprobe -v error -show_entries stream=width,height -of csv=p=0 "$out")"
