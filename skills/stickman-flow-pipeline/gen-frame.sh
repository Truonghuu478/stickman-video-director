#!/usr/bin/env bash
# Moved: this skill was merged into dao-dien-tap. Forward to the maintained copy.
here=$(cd "$(dirname "$0")" && pwd -P)
exec "$here/../dao-dien-tap/scripts/gen-frame.sh" "$@"
