# fleet-workspace-audit.ps1 - Fleet workspace baseline self-audit (CEO order O-20261009-1715, council case C-20261009-03).
# Runs ON EACH FLEET MACHINE against its FluxGroup root. Verifies workspace baseline v1:
#   A. total repo sync  : HEAD == origin/main HEAD (after fetch) -> machine-verifiable "files identical" test
#   B. dirty-face split : modified / staged / untracked counts (post-baseline .gitignore: noise should be near zero)
#   C. conflict remnants: codely sync-conflict files (pattern built from char codes: PS5.1 no-CHINESE-in-script law)
#   D. nested repos     : remote present? ahead/behind? dirty? .git size flag (>2GB = GIT_BIG chronic flag)
#   E. root junk        : root-level FILES outside the canonical whitelist
# Output: compact lines (for order receipts) + JSON snapshot to .codely-cli/patrol/fleet-workspace-audit-<host>.json
# Fail-soft: failed checks are reported, never block the rest. Exit 0 always (advisory tool).
# PS 5.1 safe: pure ASCII body; real git located explicitly (PATH git may be the gitsilent shim which swallows stdout).
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [switch]$NoFetch
)
$ErrorActionPreference = 'Continue'

# real git, bypass any PATH shim
$git = 'C:\Program Files\Git\cmd\git.exe'
if (-not (Test-Path $git)) { $git = 'git' }

function Gx([string]$dir, [string]$ga) {
    try { return ,@(& $git -C $dir @($ga -split ' ')) } catch { return ,@() }
}

# conflict-file pattern "DE-CHONG-TU" built from char codes (U+7684 U+51B2 U+7A81)
$confPat = [string][char]0x7684 + [string][char]0x51B2 + [string][char]0x7A81

$host_name = $env:COMPUTERNAME
$report = [ordered]@{ tool = 'fleet-workspace-audit v1.0'; host = $host_name; root = $Root; ts = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') }
$lines = @()
$lines += "== fleet-workspace-audit v1.0 host=$host_name root=$Root =="

# --- A. total repo sync ---
if (-not $NoFetch) { Gx $Root 'fetch -q origin' | Out-Null }
$head = (Gx $Root 'rev-parse HEAD') | Select-Object -First 1
$origin = (Gx $Root 'rev-parse origin/main') | Select-Object -First 1
$sync = 'FAIL'
if ($head -and $origin -and $head -eq $origin) { $sync = 'PASS' } elseif (-not $head) { $sync = 'NOGIT' }
$report.total_head = $head; $report.total_origin_main = $origin; $report.total_sync = $sync
$lines += "A total-repo sync=$sync HEAD=$head origin/main=$origin"

# --- B. dirty-face split (counts only; in-flight files belong to their authoring window per baseline v1) ---
$st = Gx $Root 'status --porcelain=v1'
$mod = @($st | Where-Object { $_ -match '^ M' }).Count
$stg = @($st | Where-Object { $_ -match '^[MADR]' }).Count
$unt = @($st | Where-Object { $_ -match '^\?\?' }).Count
$report.dirty = @{ modified = $mod; staged = $stg; untracked = $unt; total = @($st).Count }
$lines += "B dirty-face modified=$mod staged=$stg untracked=$unt total=$(@($st).Count)"

# --- C. conflict remnants ---
$conf = @()
foreach ($l in @($st)) { if ($l -match ('^\?\?') -and ($l -match $confPat)) { $conf += $l } }
if (@($conf).Count -eq 0) {
    foreach ($d in @('.codely-cli', 'gaming\.codely-cli', 'quant\.codely-cli', 'life\.codely-cli', 'media\.codely-cli', 'compute\.codely-cli', 'domain\.codely-cli', 'house\.codely-cli')) {
        $p = Join-Path $Root $d
        if (Test-Path $p) { $conf += @(Get-ChildItem $p -File -Filter ('*' + $confPat + '*') -ErrorAction SilentlyContinue | ForEach-Object { 'FS ' + $d + '\' + $_.Name }) }
    }
}
$report.conflict_remnants = @($conf).Count
$extra = ''; if (@($conf).Count -gt 0) { $extra = ($conf -join '; ') }
$lines += "C conflict-remnants count=$(@($conf).Count) $extra"

# --- D. nested repos (from fleet-nodes.json repos of this host; fallback = standard set) ---
$repoSet = @('gaming/MiniGame', 'gaming/FluxVerse', 'quant/bigmoney', 'media/BigStream', 'life/BigLife', 'domain/BigDomain', 'compute/BigCompute', 'house/BigHouse')
$nodesF = Join-Path $Root 'Tools\fleet-nodes.json'
if (Test-Path $nodesF) {
    try {
        $cfg = Get-Content -Raw -Encoding UTF8 $nodesF | ConvertFrom-Json
        $me = @($cfg.nodes) | Where-Object { $_.host -ieq $host_name } | Select-Object -First 1
        if ($me -and $me.repos) { $repoSet = @(@($me.repos) | Where-Object { $_ -ne '.' }) + @($repoSet | Where-Object { @($me.repos) -notcontains $_ }) }
    } catch { }
}
$nested = @()
foreach ($r in $repoSet) {
    $p = Join-Path $Root ($r -replace '/', '\')
    if (-not (Test-Path (Join-Path $p '.git'))) { $nested += "$r NOGIT"; $lines += "D $r NOGIT"; continue }
    if (-not $NoFetch) { Gx $p 'fetch -q origin' | Out-Null }
    $rem = (Gx $p 'remote') | Select-Object -First 1
    $remS = 'ok'; if (-not $rem) { $remS = 'NO-REMOTE' }
    $ab = (Gx $p 'status -sb') | Select-Object -First 1
    $abF = 'sync'
    if ($ab -match 'ahead (\d+)') { $abF = 'ahead' + $Matches[1] }
    if ($ab -match 'behind (\d+)') { $abF = $abF + '+behind' + $Matches[1] }
    $dr = @((Gx $p 'status --porcelain=v1')).Count
    $gs = 0
    try { $gs = [math]::Round(((Get-ChildItem (Join-Path $p '.git') -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum) / 1MB, 0) } catch { }
    $flag = ''; if ($gs -gt 2048) { $flag = ' GIT_BIG' }
    $lines += "D $r remote=$remS $abF dirty=$dr git=${gs}MB$flag"
    $nested += "$r=$abF"
}
$report.nested = $nested

# --- E. root junk (root-level FILES outside canonical whitelist; directories are exempt, listed dirs are governed by the tree) ---
$whitelist = @('AI.md', 'BRAND.md', 'CODELY.md', 'README.md', 'RULES.md', 'handover.md', '.gitignore', '.gitattributes')
$junk = @(Get-ChildItem $Root -File -ErrorAction SilentlyContinue | Where-Object { $whitelist -notcontains $_.Name } | ForEach-Object { $_.Name })
$report.root_junk = $junk
$extra2 = ''; if (@($junk).Count -gt 0) { $extra2 = ($junk -join ', ') }
$lines += "E root-junk count=$(@($junk).Count) $extra2"

# --- verdict ---
$verdict = 'PASS'
if ($sync -ne 'PASS') { $verdict = 'FAIL' }
elseif (@($conf).Count -gt 0) { $verdict = 'WARN' }
elseif (@($junk).Count -gt 0) { $verdict = 'WARN' }
$report.verdict = $verdict
$stN = @($st).Count; $confN = @($conf).Count; $junkN = @($junk).Count
$lines += "VERDICT: $verdict (A sync=$sync B total=$stN C conflict=$confN E junk=$junkN)"

# --- JSON snapshot (runtime telemetry, ignored path) ---
try {
    $patrolDir = Join-Path $Root '.codely-cli\patrol'
    if (-not (Test-Path $patrolDir)) { New-Item -ItemType Directory -Path $patrolDir -Force | Out-Null }
    ($report | ConvertTo-Json -Depth 4) | Out-File (Join-Path $patrolDir ("fleet-workspace-audit-{0}.json" -f $host_name)) -Encoding utf8
} catch { }
$lines | ForEach-Object { Write-Output $_ }
exit 0
