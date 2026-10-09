# _r824bmc_krea2_dl.ps1 -- Krea-2 training weights x3 from ModelScope mirror (Comfy-Org/Krea-2)
# Channel decision (r824): bm-a taildrop lane died zero-transfer (PID 31932, 01:29, empty logs);
#   bm-a HTTP-over-DERP fallback measured 0.19 MB/s single / 1.48 MB/s x8 aggregate (26GB ~= 5h);
#   ModelScope mirror (bm-c proven fastest channel, ~25MB/s x8) has byte-exact same three files.
#   Integrity gate: sha256 extracted programmatically from MSG-20261010-0055 (published by r821,
#   itself lfs.oid-derived per 10-10 zero-manual-transcription law) vs local Get-FileHash.
#   Hash mismatch on any file -> receipt verdict FAIL + no file promoted; fallback = bm-a HTTP lane.
# 8-segment parallel ranged downloader, part-resume rounds (dl_multi.ps1 lineage, 2026-10-02).
$ErrorActionPreference = 'Stop'
$root    = 'D:\krea2_weights'
$log     = Join-Path $root 'dl3_log.txt'
$receipt = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r824bmc_krea2_dl_receipt.json'
$msgPath = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\inbox\processed\MSG-20261010-0055-bmc-bma-JMANW841TDDROP.md'
$base    = 'https://modelscope.cn/api/v1/models/Comfy-Org/Krea-2/repo?Revision=master&FilePath='
$files = @(
    @{ path='diffusion_models/krea2_raw_bf16.safetensors';  name='krea2_raw_bf16.safetensors' },
    @{ path='text_encoders/qwen3vl_4b_bf16.safetensors';   name='qwen3vl_4b_bf16.safetensors' },
    @{ path='vae/qwen_image_vae.safetensors';               name='qwen_image_vae.safetensors' }
)
function Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Add-Content -Encoding UTF8 $log }
New-Item -ItemType Directory -Force $root | Out-Null
Set-Content -Encoding UTF8 $log "r824 krea2 weights download driver start (ModelScope mirror, 8-seg parallel)"

$msg = Get-Content $msgPath -Raw
$report = @{ started = (Get-Date -Format o); channel = 'modelscope Comfy-Org/Krea-2 mirror'; files = @() }

function Part-Expected([long]$i, [long]$chunk, [long]$total) {
    if ($i * $chunk -ge $total) { return 0L }
    $e = $total - ($i * $chunk)
    if ($e -gt $chunk) { $e = $chunk }
    return [long]$e
}
function Download-One([string]$url, [long]$total, [string]$outFile) {
    $partDir = "$outFile.parts"
    New-Item -ItemType Directory -Force $partDir | Out-Null
    $n = 8; $chunk = [math]::Ceiling($total / $n)
    for ($round = 1; $round -le 40; $round++) {
        $todo = @()
        for ($i = 0; $i -lt $n; $i++) {
            $exp = Part-Expected $i $chunk $total
            if ($exp -eq 0) { continue }
            $p = Join-Path $partDir "part$i"
            $have = 0L; if (Test-Path $p) { $have = (Get-Item $p).Length }
            if ($have -ne $exp) { $todo += ,@($i, $have) }
        }
        if ($todo.Count -eq 0) { Log "$outFile : all parts complete"; break }
        Log "$outFile : round $round parts to fetch/continue = $($todo.Count)"
        $procs = @()
        foreach ($t in $todo) {
            $i = $t[0]; $have = $t[1]
            $start = [long]($i * $chunk) + $have
            $end = [math]::Min(([long]($i + 1) * $chunk) - 1, $total - 1)
            $p = Join-Path $partDir "part$i"
            if ($have -gt 0) {
                $tmp = "$p.tmp"
                $a = "-L -sS --retry 6 --retry-all-errors --max-time 5400 -r $start-$end -o `"$tmp`" `"$url`""
                Log "$outFile part $i : resume from offset $have"
                $procs += ,@($i, (Start-Process -FilePath curl.exe -ArgumentList $a -NoNewWindow -PassThru), $tmp, $p)
            } else {
                if (Test-Path $p) { Remove-Item $p -Force }
                $a = "-L -sS --retry 6 --retry-all-errors --max-time 5400 -r $start-$end -o `"$p`" `"$url`""
                Log "$outFile part $i : fetch range $start-$end"
                $procs += ,@($i, (Start-Process -FilePath curl.exe -ArgumentList $a -NoNewWindow -PassThru), $null, $p)
            }
        }
        foreach ($t in $procs) { $t[1].WaitForExit() }
        foreach ($t in $procs) {
            $i = $t[0]; $tmp = $t[2]; $p = $t[3]
            if ($tmp -and (Test-Path $tmp)) {
                $fs = [IO.File]::Open($p, 'Append', 'Write')
                $ts = [IO.File]::OpenRead($tmp)
                $ts.CopyTo($fs); $ts.Close(); $fs.Close()
                Remove-Item $tmp -Force
                Log "$outFile part $i : appended resume chunk"
            }
        }
    }
    $bad = @()
    for ($i = 0; $i -lt $n; $i++) {
        $exp = Part-Expected $i $chunk $total
        if ($exp -eq 0) { continue }
        $p = Join-Path $partDir "part$i"
        $have = 0L; if (Test-Path $p) { $have = (Get-Item $p).Length }
        if ($have -ne $exp) { $bad += $i }
    }
    if ($bad.Count -gt 0) { Log "$outFile FAILED parts: $($bad -join ',')"; throw "parts incomplete: $($bad -join ',')" }
    Log "$outFile concat begin"
    if (Test-Path $outFile) { Remove-Item $outFile -Force }
    $fs = [IO.File]::Create($outFile)
    $buf = New-Object byte[] (16MB)
    for ($i = 0; $i -lt $n; $i++) {
        $p = Join-Path $partDir "part$i"
        if (-not (Test-Path $p)) { continue }
        $s = [IO.File]::OpenRead($p)
        while (($r = $s.Read($buf, 0, $buf.Length)) -gt 0) { $fs.Write($buf, 0, $r) }
        $s.Close()
    }
    $fs.Close()
    $final = (Get-Item $outFile).Length
    Log "$outFile concat done size=$final expected=$total"
    if ($final -ne $total) { throw "$outFile final size mismatch $final" }
    Remove-Item $partDir -Recurse -Force
}

$overall = 'PASS'
foreach ($f in $files) {
    $nm = $f.name
    if ($msg -match "- $([regex]::Escape($nm)) \| (?<sz>[\d,]+) B \| sha256 (?<sha>[0-9a-f]{64})") {
        $expSize  = [long]($Matches.sz -replace ',', '')
        $expSha   = $Matches.sha
    } else { Log "META-PARSE-FAIL for $nm"; throw "sha meta not found in MSG for $nm" }
    $outFile = Join-Path $root $nm
    $t0 = Get-Date
    if ((Test-Path $outFile) -and ((Get-Item $outFile).Length -eq $expSize)) {
        Log "$nm already present at expected size, skip download"
    } else {
        Download-One ($base + $f.path) $expSize $outFile
    }
    Log "$nm hashing begin"
    # r824 fix: Get-FileHash unavailable in hidden-PS runner context (predecessor death);
    # certutil is a native OS binary, locale-proof via pure-hex line match.
    $h = ((& certutil -hashfile $outFile SHA256) | Where-Object { $_ -match '^[0-9a-fA-F]{64}$' } | Select-Object -First 1).ToString().ToLower()
    $hashOk = ($h -eq $expSha)
    $sizeOk = ((Get-Item $outFile).Length -eq $expSize)
    $verdict = if ($hashOk -and $sizeOk) { 'PASS' } else { 'FAIL' }
    if ($verdict -eq 'FAIL') { $overall = 'FAIL' }
    Log "$nm gate: size_ok=$sizeOk sha_ok=$hashOk sha_local=$h sha_expected=$expSha verdict=$verdict"
    $report.files += @{ name = $nm; size = (Get-Item $outFile).Length; size_expected = $expSize;
                        size_ok = $sizeOk; sha_ok = $hashOk; sha_local = $h; sha_expected = $expSha;
                        verdict = $verdict; elapsed_sec = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1) }
}
$report.verdict = $overall
$report.finished = (Get-Date -Format o)
$report | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 $receipt
Log "RECEIPT written $receipt overall=$overall"
if ($overall -ne 'PASS') { throw "hash gate FAIL" }
Log "DOWNLOAD_DRIVER_OK"
