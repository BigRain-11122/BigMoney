# subsidiary-load-audit.ps1 - v1.0 2026-10-09
# Council load monitor per CEO order O-20261009-1255 (manman-yi... see orders.md).
# Enforces existing law: docs/self-drive.md v2.0 (09-28 CEO order) + audit-charter.
# ASCII-only script body (PS5.1 encoding law). Output one verdict line per subsidiary.
# Verdicts: GREEN (full load) / AMBER (degrading) / RED (idle or off-track -> E1 same shift)
# Thresholds (from self-drive.md): P2 tech commit every 24h -> product/tech commit age
#   <=24h else RED; queue files main>=5 tech>=10 explore>=10 else AMBER;
#   idle-declaration ratio >=50% of last 30 commits -> AMBER.
param([string]$Root = "C:\Users\sjs20\Desktop\FluxGroup")

$git = "C:\Program Files\Git\cmd\git.exe"
$bkRegex = 'chore|closeout|heartbeat|no-pullable|queue-empty|five-checks|state tick|probes green|probes flat|absorb|declaration|fold|ledger|snapshot|kanban|tick done|water-level|census-data-hygiene|maintenance|bookkeeping|jie-lu|shou-|kai-|xin-|shou-ban|kuaizhao|kanban|xintiao'
$companies = @(
    @{n='Biggame'; p='gaming\MiniGame'},
    @{n='FluxVerse'; p='gaming\FluxVerse'},
    @{n='BigMoney'; p='quant\bigmoney'},
    @{n='BigStream'; p='media\BigStream'},
    @{n='BigDomain'; p='domain\BigDomain'},
    @{n='BigLife'; p='life\BigLife'},
    @{n='BigCompute'; p='compute\BigCompute'},
    @{n='BigHouse'; p='house\BigHouse'}
)

$now = Get-Date
foreach ($c in $companies) {
    $repo = Join-Path $Root $c.p
    if (-not (Test-Path (Join-Path $repo '.git'))) { Write-Output ("{0}|NO-REPO" -f $c.n); continue }
    # last 30 commits: timestamp + subject
    $raw = & $git -C $repo log -30 --pretty=format:"%ad|%s" --date=format:"%Y-%m-%d %H:%M:%S" 2>$null
    if (-not $raw) { Write-Output ("{0}|NO-LOG" -f $c.n); continue }
    $prodAgeH = 999; $prodCount = 0; $idleDecl = 0; $lastSubj = ''
    foreach ($line in $raw) {
        if ($line -notmatch '^\d{4}-') { continue }
        $parts = $line -split '\|', 2
        $ts = [datetime]::ParseExact($parts[0], 'yyyy-MM-dd HH:mm:ss', $null)
        $subj = $parts[1]
        $ageH = ($now - $ts).TotalHours
        if ($subj -imatch $bkRegex) { $idleDecl++ }
        else {
            $prodCount++
            if ($ageH -lt $prodAgeH) { $prodAgeH = [math]::Round($ageH, 1); $lastSubj = $subj }
        }
    }
    # queue face
    $qdir = Join-Path $repo 'state\queue'
    $q = 'MISSING'
    if (Test-Path $qdir) {
        $m = @(); $t = @(); $e = @()
        if (Test-Path (Join-Path $qdir 'main.md'))    { $m = Get-Content (Join-Path $qdir 'main.md')    | Where-Object { $_ -match '\S' } }
        if (Test-Path (Join-Path $qdir 'tech.md'))    { $t = Get-Content (Join-Path $qdir 'tech.md')    | Where-Object { $_ -match '\S' } }
        if (Test-Path (Join-Path $qdir 'explore.md')) { $e = Get-Content (Join-Path $qdir 'explore.md') | Where-Object { $_ -match '\S' } }
        $q = ("m{0}/t{1}/e{2}" -f $m.Count, $t.Count, $e.Count)
        if ($m.Count -lt 5 -or $t.Count -lt 10 -or $e.Count -lt 10) { $q = $q + '/LOW' } else { $q = $q + '/OK' }
    }
    # verdict
    $v = 'GREEN'
    if ($prodAgeH -gt 24) { $v = 'RED' }
    elseif ($prodAgeH -gt 12 -or $q -match 'LOW|MISSING' -or $idleDecl -ge 15) { $v = 'AMBER' }
    $lastSnip = if ($lastSubj.Length -gt 40) { $lastSubj.Substring(0, 40) } else { $lastSubj }
    Write-Output ("{0}|{1}|prodAge={2}h|prod30={3}|idleDecl30={4}|queue={5}|lastProd=`"{6}`"" -f $c.n, $v, $prodAgeH, $prodCount, $idleDecl, $q, $lastSnip)
}
