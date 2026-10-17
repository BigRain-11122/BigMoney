# r999 commit-A driver: restore r998+r999 estate own-faces from stash, land commit with O-0348 prescribed message.
# ASCII-only. Live daemon faces (autofill/saturation x4) + machine-health + d19_check intentionally NOT restored
# (live-wins / shared newer-wins; S6 rerun covers). post_review faces via line-union (not stash-overwrite).
$ErrorActionPreference = 'Stop'
Set-Location C:\Fluxgroup\FluxGroup\quant\bigmoney
$sha = git rev-parse refs/stash

$own = @(
 'CODELY.md','state.json','fleet/machines/bm-b.json','fleet/orders/O-20261018-0137-bm-a.md',
 'results/_orphan_face_probe.bm-b.json','results/astock_daily_update_status.json','results/compute_audit.bm-b.json',
 'results/etf_daily_pull_status.json','results/futures_update_status.bm-b.json','results/idle_trigger.bm-b.json',
 'results/idle_trigger_state.bm-b.json','results/lhb_update_status.bm-b.json','results/orders_ack_scan.bm-b.json',
 'results/pool_dualrun.bm-b.jsonl','results/regime_state.bm-b.json','results/rev_osc_live/_export_state.json',
 'results/token_usage.bm-b.json','results/update_status.bm-b.json'
)
git checkout $sha -- $own
Write-Output "restored=$($own.Count)"

# MSG-2232 inbox move completion (processed copy already on disk)
git rm --quiet fleet/inbox/MSG-20261017-2232-bma-dramapickup-reply.md
Write-Output 'MSG-2232 original removed (processed copy in place)'

# line-union the two post_review faces (HEAD incl bm-c r1081 rows UNION stash-extra)
python _r999bmb_stash_union3.py

$adds = @(
 'CODELY.md','state.json','fleet/machines/bm-b.json','fleet/orders/O-20261018-0137-bm-a.md',
 'results/_orphan_face_probe.bm-b.json','results/astock_daily_update_status.json','results/compute_audit.bm-b.json',
 'results/etf_daily_pull_status.json','results/futures_update_status.bm-b.json','results/idle_trigger.bm-b.json',
 'results/idle_trigger_state.bm-b.json','results/lhb_update_status.bm-b.json','results/orders_ack_scan.bm-b.json',
 'results/pool_dualrun.bm-b.jsonl','results/regime_state.bm-b.json','results/rev_osc_live/_export_state.json',
 'results/token_usage.bm-b.json','results/update_status.bm-b.json','results/watermark_red.json',
 'results/post_review.jsonl','results/post_review/REPORT-20261018.md',
 '_r997bmb_surgery_push.py','_r998bmb_closeout.py','_r998bmb_s6.py','_r999_uu.txt',
 '_r999bmb_clip_refine.py','_r999bmb_conflict_resolve.py','_r999bmb_minichain.ps1','_r999bmb_s6chain.ps1',
 '_r999bmb_stash_union2.py','_r999bmb_stash_union3.py','_r999bmb_voice_audition.py',
 'fleet/inbox/MSG-20261018-0216-bm-b-taskaudit.md','fleet/inbox/MSG-20261018-0319-bmb-voicegen-audition-reel.md',
 'fleet/inbox/processed/MSG-20261017-2232-bma-dramapickup-reply.md',
 'results/_r998bmb_f0probe.json','results/_r998bmb_f0probe.py','results/_r998bmb_s6_log.txt',
 'results/_r998bmb_speakers.txt','results/_r999bmb_voice_audition.json',
 'results/rev_osc_live/BARS-2026-10-16.json','results/rev_osc_live/SIG-2026-10-16.json'
)
git add -- $adds
$n = (git diff --cached --name-only | Measure-Object -Line).Lines
Write-Output "staged=$n"

git commit -m 'round 998 git-face closeout: O-0137 taskaudit receipt landed late (estate absorb per O-20261018-0348-bm-a)'
Write-Output "commit_rc=$LASTEXITCODE head=$(git rev-parse --short HEAD)"
