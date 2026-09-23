# transfer_manifest.ps1 - fleet transfer manifest & verify tool (ASCII only)
# Docs: fleet/TRANSFER.md section 7
# Usage:
#   Manifest: Tools\transfer_manifest.ps1 -Path D:\dataset -Out fleet\transfers\T-...-sender.json [-Hash]
#   Verify:   Tools\transfer_manifest.ps1 -Path D:\received -Verify fleet\transfers\T-...-sender.json [-Hash]
# Exit codes: 0 = pass/written, 1 = verify fail, 3 = input error
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [string]$Out,
    [switch]$Hash,
    [string]$Verify
)

function Get-SHA256([string]$file) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $fs = [System.IO.File]::OpenRead($file)
        try { ([BitConverter]::ToString($sha.ComputeHash($fs))).Replace('-', '').ToLowerInvariant() } finally { $fs.Dispose() }
    } finally { $sha.Dispose() }
}

if (-not (Test-Path -LiteralPath $Path)) { Write-Output "ERROR path not found: $Path"; exit 3 }
$root = (Resolve-Path -LiteralPath $Path).Path
$files = @(Get-ChildItem -LiteralPath $Path -Recurse -File | Sort-Object FullName)
$totalBytes = 0L; foreach ($f in $files) { $totalBytes += $f.Length }

function Rel([string]$full) { $full.Substring($root.Length).TrimStart('\', '/') }

$sampledIdx = @()
if ($files.Count -gt 0) {
    $sampledIdx += 0
    if ($files.Count -gt 2) { $sampledIdx += [int][math]::Floor($files.Count / 2) }
    $sampledIdx += $files.Count - 1
}
$sampled = @()
foreach ($i in ($sampledIdx | Select-Object -Unique)) {
    $sampled += [ordered]@{ file = (Rel $files[$i].FullName); bytes = [long]$files[$i].Length; sha256 = (Get-SHA256 $files[$i].FullName) }
}

$manifest = [ordered]@{
    tool        = 'transfer_manifest.ps1 v1.0'
    path        = $root
    file_count  = $files.Count
    total_bytes = $totalBytes
    full_hash   = [bool]$Hash
    sampled     = $sampled
    files       = @()
}

if ($Hash) {
    $list = @()
    foreach ($f in $files) {
        $list += [ordered]@{ file = (Rel $f.FullName); bytes = [long]$f.Length; sha256 = (Get-SHA256 $f.FullName) }
    }
    $manifest.files = $list
}

if ($Out) {
    $dir = Split-Path -Parent $Out
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $manifest | ConvertTo-Json -Depth 6 | Out-File -LiteralPath $Out -Encoding utf8
    Write-Output "MANIFEST_WRITTEN file_count=$($manifest.file_count) total_bytes=$($manifest.total_bytes) full_hash=$([bool]$Hash) out=$Out"
}

if ($Verify) {
    if (-not (Test-Path -LiteralPath $Verify)) { Write-Output "ERROR verify manifest not found: $Verify"; exit 3 }
    $ref = Get-Content -LiteralPath $Verify -Raw -Encoding UTF8 | ConvertFrom-Json
    $ok = $true
    if ([long]$ref.file_count -ne [long]$manifest.file_count) { $ok = $false; Write-Output "FAIL file_count ref=$($ref.file_count) got=$($manifest.file_count)" }
    else { Write-Output "OK file_count=$($manifest.file_count)" }
    if ([long]$ref.total_bytes -ne [long]$manifest.total_bytes) { $ok = $false; Write-Output "FAIL total_bytes ref=$($ref.total_bytes) got=$($manifest.total_bytes)" }
    else { Write-Output "OK total_bytes=$($manifest.total_bytes)" }
    foreach ($s in @($ref.sampled)) {
        $local = @($manifest.sampled | Where-Object { $_.file -eq $s.file })
        if ($local.Count -eq 0) { $ok = $false; Write-Output "FAIL sampled missing: $($s.file)" }
        elseif ($local[0].sha256 -ne $s.sha256) { $ok = $false; Write-Output "FAIL sampled hash: $($s.file)" }
        else { Write-Output "OK sampled: $($s.file)" }
    }
    if ($ref.full_hash -and $Hash) {
        $refMap = @{}; foreach ($f in @($ref.files)) { $refMap[$f.file] = $f.sha256 }
        $gotMap = @{}; foreach ($f in @($manifest.files)) { $gotMap[$f.file] = $f.sha256 }
        $miss = 0; $bad = 0; $extra = 0
        foreach ($k in $refMap.Keys) {
            if (-not $gotMap.ContainsKey($k)) { $miss++; $ok = $false; if ($miss -le 10) { Write-Output "FAIL missing: $k" } }
            elseif ($gotMap[$k] -ne $refMap[$k]) { $bad++; $ok = $false; if ($bad -le 10) { Write-Output "FAIL hash: $k" } }
        }
        foreach ($k in $gotMap.Keys) { if (-not $refMap.ContainsKey($k)) { $extra++; $ok = $false; if ($extra -le 10) { Write-Output "FAIL extra: $k" } } }
        if ($miss -gt 10 -or $bad -gt 10 -or $extra -gt 10) { Write-Output "FAIL (truncated) missing=$miss bad_hash=$bad extra=$extra" }
    }
    elseif ($ref.full_hash -and -not $Hash) { Write-Output "WARN sender manifest has full hashes; rerun with -Hash for full verification" }
    if ($ok) { Write-Output "VERIFY PASS"; exit 0 } else { Write-Output "VERIFY FAIL"; exit 1 }
}
exit 0
