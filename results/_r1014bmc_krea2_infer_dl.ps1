# _r1014bmc_krea2_infer_dl.ps1 -- Krea-2 INFERENCE weights x2 from ModelScope mirror (Comfy-Org/Krea-2)
# Purpose (r1014): bm-c lane-capability fill per O-20261012-2215 dinggang law (bm-c = Krea2 KF GPU lane).
#   ComfyUI currently H3-INT8-only (disk-verified r1014); wave3 XQ A-34 KF + casting-16 need Krea2 t2i.
# Files: diffusion_models/krea2_turbo_fp8_scaled.safetensors + text_encoders/qwen3vl_4b_fp8_scaled.safetensors.
#   (qwen_image_vae.safetensors already local, sha-gated PASS r824.)
# Meta source: LIVE ModelScope API Sha256+Size per 10-10 zero-manual-transcription law (no hardcoded hashes).
# Clone of Tools/_r824bmc_krea2_dl.ps1 (8-seg parallel ranged downloader, part-resume, certutil SHA gate).
$ErrorActionPreference = 'Stop'
$root    = 'D:\krea2_weights'
$log     = Join-Path $root 'dl5_log.txt'
$receipt = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1014bmc_krea2_infer_dl_receipt.json'
$base    = 'https://modelscope.cn/api/v1/models/Comfy-Org/Krea-2/repo?Revision=master&FilePath='
$metaUrl = 'https://modelscope.cn/api/v1/models/Comfy-Org/Krea-2/repo/files?Recursive=true'
$files = @(
    @{ path='diffusion_models/krea2_turbo_fp8_scaled.safetensors'; name='krea2_turbo_fp8_scaled.safetensors';
       dest='D:\ComfyUI\models\diffusion_models\krea2_turbo_fp8_scaled.safetensors' },
    @{ path='text_encoders/qwen3vl_4b_fp8_scaled.safetensors';    name='qwen3vl_4b_fp8_scaled.safetensors';
       dest='D:\ComfyUI\models\text_encoders\qwen3vl_4b_fp8_scaled.safetensors' }
)
function Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Add-Content -Encoding UTF8 $log }
New-Item -ItemType Directory -Force $root | Out-Null
Set-Content -Encoding UTF8 $log "r1014 krea2 inference weights download driver start (ModelScope mirror, 8-seg parallel)"

# live meta pull (programmatic, zero transcription)
$listing = Invoke-RestMethod -Uri $metaUrl -TimeoutSec 30
$report = @{ started = (Get-Date -Format o); channel = 'modelscope Comfy-Org/Krea-2 mirror (r1014 inference fill)'; files = @() }

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
    $entry = $null
    foreach ($x in $listing.Data.Files) { if ($x.Path -eq $f.path) { $entry = $x; break } }
    if ($null -eq $entry) { Log "META-LOOKUP-FAIL for $($f.path)"; throw "meta entry not found for $($f.path)" }
    $expSize = [long]$entry.Size
    $expSha  = [string]$entry.Sha256
    $expSha  = $expSha.ToLower()
    Log "$nm meta (live API): size=$expSize sha256=$expSha"
    $outFile = Join-Path $root $nm
    $t0 = Get-Date
    if ((Test-Path $outFile) -and ((Get-Item $outFile).Length -eq $expSize)) {
        Log "$nm already present at expected size, skip download"
    } else {
        Download-One ($base + $f.path) $expSize $outFile
    }
    Log "$nm hashing begin"
    # certutil per r824 fix (Get-FileHash unavailable in hidden-PS runner context)
    $h = ((& certutil -hashfile $outFile SHA256) | Where-Object { $_ -match '^[0-9a-fA-F]{64}$' } | Select-Object -First 1).ToString().ToLower()
    $hashOk = ($h -eq $expSha)
    $sizeOk = ((Get-Item $outFile).Length -eq $expSize)
    $verdict = if ($hashOk -and $sizeOk) { 'PASS' } else { 'FAIL' }
    if ($verdict -eq 'FAIL') { $overall = 'FAIL' }
    Log "$nm gate: size_ok=$sizeOk sha_ok=$hashOk sha_local=$h sha_expected=$expSha verdict=$verdict"
    $report.files += @{ name = $nm; size = (Get-Item $outFile).Length; size_expected = $expSize;
                        size_ok = $sizeOk; sha_ok = $hashOk; sha_local = $h; sha_expected = $expSha;
                        verdict = $verdict; elapsed_sec = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1) }
    if ($verdict -eq 'PASS') {
        $destDir = Split-Path $f.dest -Parent
        New-Item -ItemType Directory -Force $destDir | Out-Null
        Copy-Item $outFile $f.dest -Force
        Log "$nm promoted -> $($f.dest)"
    }
}
# VAE promotion (already sha-gated r824) into ComfyUI vae dir for the KF workflow
$vaeSrc = Join-Path $root 'qwen_image_vae.safetensors'
$vaeDst = 'D:\ComfyUI\models\vae\qwen_image_vae.safetensors'
if ((Test-Path $vaeSrc) -and -not (Test-Path $vaeDst)) {
    New-Item -ItemType Directory -Force (Split-Path $vaeDst -Parent) | Out-Null
    Copy-Item $vaeSrc $vaeDst -Force
    Log "vae promoted -> $vaeDst"
}
$report.verdict = $overall
$report.finished = (Get-Date -Format o)
$report | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 $receipt
Log "RECEIPT written $receipt overall=$overall"
if ($overall -ne 'PASS') { throw "hash gate FAIL" }
Log "DOWNLOAD_DRIVER_OK"
