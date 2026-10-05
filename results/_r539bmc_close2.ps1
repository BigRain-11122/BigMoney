# _r539bmc_close2.ps1 -- S7 close phase 2: delivery self-check -> close row (measured values only,
# r532/r533 tail-defer law) -> targeted close commit -> push -> final verify.
$root = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$wrap = Join-Path $root 'Tools\Invoke-SilentExe.ps1'
$rr = Join-Path $root 'round_reports-bm-c.md'
$roundSha = 'bc4703bcf'

"=== DELIVERY VERIFY ==="
& $wrap -Exe git.exe -ArgString 'fetch origin' -Cwd $root | Out-Null
"FETCH_RC=$LASTEXITCODE"
$ah = & $wrap -Exe git.exe -ArgString 'rev-list --count origin/main..HEAD' -Cwd $root -StdoutOnly
$bh = & $wrap -Exe git.exe -ArgString 'rev-list --count HEAD..origin/main' -Cwd $root -StdoutOnly
"AHEAD=$ah BEHIND=$bh"
$lt = & $wrap -Exe git.exe -ArgString 'ls-tree origin/main -- state-bm-c.json fleet/machines/bm-c.json round_reports-bm-c.md qa/smoke-r539.md qa/equity-curve-r539.png results/_r539bmc_s6_log.txt' -Cwd $root -StdoutOnly
$ltl = if ($lt) { $lt -split "`n" } else { @() }
$blobs = @($ltl | Where-Object { $_ -match '^[0-7]{6} blob [0-9a-f]{40}' })
"LS_TREE_PROBE=$($blobs.Count)/6"
$ltl

if ($blobs.Count -ne 6 -or [int]$ah -ne 0 -or [int]$bh -ne 0) {
  Write-Output "ABORT: delivery verify failed (probe=$($blobs.Count)/6 ahead=$ah behind=$bh)"
  exit 1
}

"=== CLOSE ROW APPEND (measured values only) ==="
$ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss+08:00'
$row = "$ts | r539 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED 首过单跳：round commit $roundSha〔40 面=簿记三写 state/心跳/轮报+qa 证据包 r539 双件+S6 log 38 腿收据+S6 再生面族+attrition 证据+S7 facts+探针/链脚手架件+daemon lane churn〕push origin main 首过 rc=0 过双爪零 --no-verify→push_verify 复证 fetch 后 ahead=0·behind=0·ls-tree 送达探针 6/6 blob 40hex 在册）| 零清扫/归档/删除/恢复类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）| 轮产品计分：2（qa/ 证据包 r539=能跑/能看实物〔93 trades·sharpe 0.1586·determinism=True·十二连证〕+S6 38 面 CEO 再生+零 UU 干净窗集成）"
$raw = [System.IO.File]::ReadAllBytes($rr)
$tailStr = [System.Text.Encoding]::UTF8.GetString($raw[[Math]::Max(0, $raw.Length - 2000)..($raw.Length - 1)])
if ($tailStr -match "`r`n") {
  [System.IO.File]::AppendAllText($rr, $row + "`r`n", (New-Object System.Text.UTF8Encoding($false)))
  "ROW_APPENDED eol=CRLF"
} else {
  [System.IO.File]::AppendAllText($rr, $row + "`n", (New-Object System.Text.UTF8Encoding($false)))
  "ROW_APPENDED eol=LF"
}

"=== CLOSE COMMIT (targeted add round_reports only) + PUSH ==="
& $wrap -Exe git.exe -ArgString 'add round_reports-bm-c.md' -Cwd $root | Out-Null
"ADD_RC=$LASTEXITCODE"
Set-Content -Path "$env:TEMP\msg_r539c.txt" -Value 'r539 bm-c S7-close: round report close row (first-try push, delivery verify 0/0, ls-tree 6/6)' -Encoding ascii
$c = & $wrap -Exe git.exe -ArgString "commit -F `"$env:TEMP\msg_r539c.txt`"" -Cwd $root
"COMMIT_RC=$LASTEXITCODE"
if ($c) { ($c -split "`n") | Select-Object -First 2 }
$p = & $wrap -Exe git.exe -ArgString 'push origin main' -Cwd $root
"PUSH_RC=$LASTEXITCODE"
if ($p) { ($p -split "`n") | Select-Object -Last 3 }

"=== FINAL VERIFY ==="
& $wrap -Exe git.exe -ArgString 'fetch origin' -Cwd $root | Out-Null
$ah2 = & $wrap -Exe git.exe -ArgString 'rev-list --count origin/main..HEAD' -Cwd $root -StdoutOnly
$bh2 = & $wrap -Exe git.exe -ArgString 'rev-list --count HEAD..origin/main' -Cwd $root -StdoutOnly
"FINAL_AHEAD=$ah2 FINAL_BEHIND=$bh2"
$w = & $wrap -Exe git.exe -ArgString 'status --porcelain' -Cwd $root -StdoutOnly
$wl2 = if ($w) { $w -split "`n" } else { @() }
"RESIDUAL_DIRTY=$($wl2.Count)"
$wl2 | Select-Object -First 6
