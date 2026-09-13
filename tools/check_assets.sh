#!/usr/bin/env bash
# Fail if index.html points at a local file that does not exist.
#
# A missing image or stylesheet does not break the build - the browser just
# gets a 404 and draws nothing, which is easy to miss until the site is live.
# Run directly, or let the pre-commit hook run it:  tools/check_assets.sh
set -uo pipefail
cd "$(dirname "$0")/.."

EXT='html|css|js|png|jpg|jpeg|svg|webp|gif|pdf|ico|woff2?'

missing=0
checked=0
while IFS= read -r ref; do
    case "$ref" in
        http:*|https:*|mailto:*|data:*|"#"*|"") continue ;;
    esac
    target="${ref%%#*}"          # drop any #fragment
    target="${target%%\?*}"      # drop any ?query
    # only consider things that actually look like a file path
    printf '%s' "$target" | grep -qiE "\.($EXT)$" || continue
    checked=$((checked + 1))
    if [ ! -e "$target" ]; then
        echo "  MISSING  $target"
        missing=$((missing + 1))
    fi
done < <(grep -oE '(src|href|srcset|content)="[^"]*"' index.html \
         | sed -E 's/^[a-z]+="//; s/"$//')

if [ "$missing" -gt 0 ]; then
    echo
    echo "index.html references $missing file(s) that do not exist."
    echo "Check the spelling and the extension - .jpg and .jpeg are different filenames."
    echo "Files actually in images/:"
    ls images/ | sed 's/^/  /'
    exit 1
fi

echo "OK: all $checked local files referenced by index.html exist."
