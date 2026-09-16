#!/usr/bin/env bash
# Fail if any page points at a local file that does not exist.
#
# A missing image or stylesheet does not break the build - the browser just
# gets a 404 and draws nothing, which is easy to miss until the site is live.
# Run directly, or let the pre-commit hook run it:  tools/check_assets.sh
set -uo pipefail
cd "$(dirname "$0")/.."

EXT='html|css|js|png|jpg|jpeg|svg|webp|gif|pdf|ico|woff2?'

missing=0
checked=0
for page in *.html; do
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
            echo "  MISSING  $target   (referenced by $page)"
            missing=$((missing + 1))
        fi
    done < <(grep -oE '(src|href|srcset|content)="[^"]*"' "$page" \
             | sed -E 's/^[a-z]+="//; s/"$//')
done

if [ "$missing" -gt 0 ]; then
    echo
    echo "$missing broken local reference(s)."
    echo "Check the spelling and the extension - .jpg and .jpeg are different filenames."
    echo "Files actually in images/:"
    ls images/ | sed 's/^/  /'
    exit 1
fi

echo "OK: all $checked local references across $(ls *.html | wc -l) pages exist."
