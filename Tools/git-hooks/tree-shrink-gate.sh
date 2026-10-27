#!/bin/sh
# TREE-SHRINK-GATE (birth-grade, r1134 bm-a, 2026-10-27)
# Why: the group tip ceebc703 (2026-10-27 22:31) was committed from a PARTIAL
# index and pushed a 2-file tree over a 3,494-file tree -- docs/decisions.md,
# docs/orders.md and all of cph4/ vanished while the commit looked like a normal
# two-receipt closeout. pre-commit stayed silent because commit-tree never runs
# it; pre-push still runs on every push, so this is the birth-place interception
# point (r1133 found the damage only because a consumer tried to read the file).
# Rule: for every commit being pushed, count files in its tree and in its first
# parent. BLOCK when the drop exceeds MAX_DROP files AND MAX_PCT of the parent.
# Escape hatch for a legitimate bulk deletion: git push --no-verify + one
# law-note line in the round report.
# Pure sh + git plumbing (no python/wc/tr: the hook PATH has none of them).
# Reads the standard pre-push ref list on stdin.
# Kept in sync with FluxGroup/Tools/hooks/pre-push (same constants and rule).
MAX_DROP=${TREE_SHRINK_MAX_DROP:-25}
MAX_PCT=${TREE_SHRINK_MAX_PCT:-20}
ZERO=0000000000000000000000000000000000000000

count_files() {
    n=0
    while IFS= read -r _line; do
        n=$((n + 1))
    done <<EOF
$(git ls-tree -r --name-only "$1" 2>/dev/null)
EOF
    echo $n
}

status=0
while read -r local_ref local_sha remote_ref remote_sha; do
    [ -n "$local_sha" ] || continue
    [ "$local_sha" = "$ZERO" ] && continue          # ref deletion, not a tree write
    # Only commits the remote does not have yet are "being introduced". Scanning
    # the whole history would keep blocking forever on a shrink that was already
    # repaired in history (ceebc703 is exactly that case). A brand-new branch has
    # no range to compute, so only its tip is judged.
    if [ "$remote_sha" != "$ZERO" ] && git cat-file -e "$remote_sha^{commit}" 2>/dev/null; then
        commits=$(git rev-list --max-count=200 "$remote_sha..$local_sha" 2>/dev/null)
        [ -n "$commits" ] || commits=$local_sha     # force push: no common commits
    else
        commits=$local_sha
    fi
    for c in $commits; do
        set -- $(git rev-list --parents -n 1 "$c" 2>/dev/null)
        first=$2
        [ -n "$first" ] || continue                 # root commit: nothing to shrink
        n_new=$(count_files "$c")
        n_par=$(count_files "$first")
        case $n_new in '' | *[!0-9]*) continue ;; esac
        case $n_par in '' | *[!0-9]*) continue ;; esac
        drop=$((n_par - n_new))
        [ "$drop" -gt 0 ] || continue
        pct=$((drop * 100 / n_par))
        if [ "$drop" -gt "$MAX_DROP" ] && [ "$pct" -gt "$MAX_PCT" ]; then
            echo "[TREE-SHRINK-GATE] BLOCK: $c pushes a ${n_new}-file tree over its parent ${first} (${n_par} files, -${drop}, ${pct}%)." >&2
            echo "[TREE-SHRINK-GATE] A commit built from a partial index looks exactly like this (ceebc703, 2026-10-27)." >&2
            echo "[TREE-SHRINK-GATE] Seed the temp index with 'git read-tree <parent>' and assert the tree size before committing." >&2
            echo "[TREE-SHRINK-GATE] Legitimate bulk deletion: git push --no-verify + one law-note line." >&2
            status=1
        fi
    done
done
exit $status