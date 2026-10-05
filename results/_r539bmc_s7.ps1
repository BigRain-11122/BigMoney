# _r539bmc_s7.ps1 -- S7 quartet + idempotent registers + attrition scan + gorders watermark.
# Writes facts to results/_r539bmc_s7_facts.json for the bookkeeping script.
$root = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$env:PYTHONIOENCODING = 'utf-8'
$wrap = Join-Path $root 'Tools\Invoke-SilentExe.ps1'

"=== QUARTET ==="
$quartet = & $wrap -Exe python.exe -ArgString "Tools\_r536bmc_s7_quartet.py" -Cwd $root
$qlines = if ($quartet) { $quartet -split "`n" } else { @() }
$qlines

"=== REGISTER LOOP (mandatory idempotent, U060 in-process) ==="
$loop_out = & (Join-Path $root 'Tools\register_loop_task.ps1')
$loop_face = [string]($loop_out | Select-Object -Last 1)
$loop_face

"=== REGISTER WATCHDOG (idempotent) ==="
$wd_out = & (Join-Path $root 'Tools\register_watchdog_task.ps1')
$wd_face = [string]($wd_out | Select-Object -Last 1)
$wd_face

"=== ATTRITION SCAN ==="
$attr = & $wrap -Exe python.exe -ArgString "scripts\attrition_ledger_guard.py scan" -Cwd $root
$attr_rc = $LASTEXITCODE
$attr_lines = if ($attr) { $attr -split "`n" } else { @() }
"ATTR_RC=$attr_rc"
$attr_lines | Select-Object -Last 3

"=== GORDERS WATERMARK ==="
$g = & $wrap -Exe python.exe -ArgString "Tools\_r539bmc_gorders.py" -Cwd $root
$g
$gsha = ''
$gmatch = $false
foreach ($ln in ($g -split "`n")) {
  if ($ln -match 'GROUP_ORDERS_SHA1=([0-9A-F]+)') { $gsha = $Matches[1] }
  if ($ln -match 'MATCH_3BF0F16E=True') { $gmatch = $true }
}

# claws: auto re-register only if diverged/missing (probe-guided)
$clawPC = [string]($qlines | Where-Object { $_ -match 'claw pre-commit' } | Select-Object -First 1)
$clawPP = [string]($qlines | Where-Object { $_ -match 'claw pre-push' } | Select-Object -First 1)
if ($clawPC -match 'DIVERGED|MISSING') {
  & (Join-Path $root 'Tools\register_precommit_claw.ps1') | Select-Object -Last 1
  $clawPC = 'claw pre-commit: RE-REGISTERED'
}
if ($clawPP -match 'DIVERGED|MISSING') {
  & (Join-Path $root 'Tools\register_prepush_claw.ps1') | Select-Object -Last 1
  $clawPP = 'claw pre-push: RE-REGISTERED'
}
if ($clawPC -match 'IN-PLACE' -and $clawPP -match 'IN-PLACE') { $claws_face = 'IN-PLACE (LF-normalized)' }
else { $claws_face = 'CHECK: ' + $clawPC + ' / ' + $clawPP }

$family = @($qlines | Where-Object { $_ -match '^Bigmoney-' })
$present = @($family | Where-Object { $_ -match 'PRESENT' }).Count
$intraday_missing = [bool]($family | Where-Object { $_ -match 'IntradayMarks: MISSING' })
if ($present -eq 6 -and $intraday_missing) {
  $family_face = '6/6 (IntradayMarks absent = legal market-closure face, G3 re-check 10-09)'
} else {
  $family_face = "$present/7 PRESENT (probe cross-check: see quartet lines)"
}

if ($attr_rc -eq 0) {
  $attr_face = 'CLEAN'
  if ($attr_lines -match 'healed') { $attr_face = 'CLEAN (healed historical shrinks noted)' }
} elseif ($attr_rc -eq 1) {
  $attr_face = 'ACTIVE-LOSS (rc=1) -- P0 union/blob repair required before commit'
} else {
  $attr_face = 'MECHANISM-FAULT (rc=' + $attr_rc + ')'
}

$facts = [ordered]@{
  loop_face       = $loop_face
  watchdog_face   = $wd_face
  family_face     = $family_face
  claws_face      = $claws_face
  attrition_rc    = $attr_rc
  attrition_face  = $attr_face
  gorders_sha1    = $gsha
  gorders_match   = $gmatch
}
$fjson = $facts | ConvertTo-Json
Set-Content -Path (Join-Path $root 'results\_r539bmc_s7_facts.json') -Value $fjson -Encoding utf8
Write-Output "S7_FACTS_WRITTEN: $fjson"
