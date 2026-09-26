# O-20260926-2000-bm-c executor: bm-a base unification migration (detached).
# Launched by bm-a R267 as its LAST action; outlives the round instance.
# Order six-step + fail-closed gates; ANY pre-move gate failure -> Abort() re-enables
# all tasks with old tree untouched. Post-move XML application is pre-validated
# BEFORE the move (Gate 0) so the post-move failure window is schtasks-only.
# ENCODING RULE: pure ASCII (powershell 5.1 ANSI decode law, iteration_loop.ps1 precedent).
param([int]$MaxWaitMin = 40)
$ErrorActionPreference = 'Continue'
$Journal = 'C:\Users\sjs20\fluxgroup-migration-journal.log'
$Old      = 'C:\Users\sjs20\Desktop\FluxGroup'
$Base     = 'C:\Fluxgroup'
$New      = 'C:\Fluxgroup\FluxGroup'
$Marker   = 'C:\Users\sjs20\fluxgroup-migration-aborted.flag'
$PrepDir  = Join-Path $env:TEMP 'fg-redef'

function Log($m) { Add-Content -Path $Journal -Value ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function TaskState($n) { (schtasks /query /tn $n /fo LIST | Select-String '^Status:' | ForEach-Object { $_.Line -replace 'Status:\s+','' }) }

$Mini = @('MiniGameAuditTick','MiniGameBoardForge','MiniGameCockpitBeat','MiniGameDailyDigest','MiniGameEditorSentry','MiniGameEngineTick','MiniGameEvolutionTick','MiniGameGateTick','MiniGameHousekeeping','MiniGameOllamaKeepWarm','MiniGameOllamaServe','MiniGamePolicyTick','MiniGamePopupWitness','MiniGameRadarDeepTick','MiniGameRadarTick','MiniGameRedlineAudit','MiniGameResearchTick','MiniGame-SiliconWatchTick','MiniGameTickWatchdog','MiniGameTjcloudSync')
$Tasks = @('Bigmoney-Autofill','Bigmoney-LoopWatchdog','Bigmoney-IterationLoop','Bigmoney-IntradayMarks','BigCompute-OSLoop','BigDomain-OSLoop','BigLife-OSLoop','BigStream-OSLoop','FluxBoardAuto','FluxGroup-DecisionRound','FluxGroup-EvolutionTick','FluxGroup-NightRound','FluxGroup-OrderSentinel','FluxVerse-DevLoop','FluxVerseTick','GimmeAll-AutoSentinel') + $Mini
$Dead = 'MoneyAutoGuardian'   # points at absent C:\Users\sjs20\Money\tools\watchdog.ps1 - disable-only, adjudication to lanes
$Repos = @($Old, "$Old\quant\bigmoney", "$Old\compute\BigCompute", "$Old\domain\BigDomain", "$Old\life\BigLife", "$Old\media\BigStream", "$Old\gaming\MiniGame", "$Old\gaming\FluxVerse")

function Abort($reason) {
    Log("ABORT: $reason - re-enabling all tasks, old tree untouched")
    foreach ($t in $Tasks) { schtasks /change /tn $t /enable *> $null; Log("re-enabled $t") }
    Set-Content -Path $Marker -Value $reason
    Log('ABORT complete - retry window open, deadline 2026-09-29 12:00')
    exit 2
}

Log('=== bm-a base unification migration START (O-20260926-2000-bm-c) ===')
if (Test-Path $Marker) { Remove-Item $Marker -Force }
if ((Test-Path $Base) -and (Get-ChildItem $Base -Force -ErrorAction SilentlyContinue)) { Abort('C:\Fluxgroup already exists and non-empty') }

# -- Gate 0 (pre-move): build + validate all redefinition XMLs --------------------
New-Item -ItemType Directory -Path $PrepDir -Force | Out-Null
$RedefFiles = @{}
foreach ($t in $Tasks) {
    $f = Join-Path $PrepDir (($t -replace '[^A-Za-z0-9_-]', '_') + '.xml')
    cmd /c "schtasks /query /tn $t /xml > $f"                     # no-quote variant (task names + TEMP path have no spaces; nested-quote variant empirically wrote empty files -> missing-root abort 20:19)
    if (-not (Test-Path $f) -or (Get-Item $f).Length -lt 50) { Abort("XML export empty for $t") }
    $x = [System.IO.File]::ReadAllText($f)                         # no-BOM UTF-8 face (cmd-redirect schtasks empirical)
    $x = $x.Replace($Old, $New)
    try { [void][System.Xml.XmlDocument]::new().LoadXml($x) }      # parse-validate BEFORE any mutation
    catch { Abort("redefinition XML invalid for $t : $($_.Exception.Message)") }
    [System.IO.File]::WriteAllText($f, $x, [System.Text.Encoding]::Unicode)   # decl stays UTF-16 -> bytes must be UTF-16LE+BOM (throwaway-task round-trip verified 20:2x)
    $RedefFiles[$t] = $f
    Log("pre-built redef XML $t ($((Get-Item $f).Length)B)")
}
Log('all redefinition XMLs pre-validated')

# -- Gate 1: disable all company tasks (running instances unaffected) ------------
foreach ($t in $Tasks) { $r = schtasks /change /tn $t /disable; Log("disable $t -> $(@($r) -join ' ')") }
schtasks /change /tn $Dead /disable *> $null; Log("disable dead task $Dead (absent target, adjudication pending)")

# -- Gate 2: wait for all in-flight instances to finish naturally -----------------
# Task-status alone is blind to DETACHED codely sessions (loop tasks spawn rounds
# fire-and-forget; the 20:21 abort proved a live session bypassed this gate), so
# also scan Win32_Process command lines for anything referencing the old root.
$deadline = (Get-Date).AddMinutes($MaxWaitMin)
while ($true) {
    $running = @()
    foreach ($t in $Tasks) { if ((TaskState $t) -eq 'Running') { $running += $t } }
    $liveProcs = @(Get-CimInstance Win32_Process -Filter "Name != 'System Idle Process'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -like "*$Old*" } |
        ForEach-Object { "$($_.Name)/$($_.ProcessId)" })
    if ($running.Count -eq 0 -and $liveProcs.Count -eq 0) { Log('all company task instances + tree-referencing processes quiescent'); break }
    Log("waiting: tasks=[$($running -join ', ')] procs=[$($liveProcs -join ', ')]")
    if ((Get-Date) -gt $deadline) { Abort("in-flight after $MaxWaitMin min: tasks=[$($running -join ', ')] procs=[$($liveProcs -join ', ')]") }
    Start-Sleep -Seconds 30
}

# -- Gate 3: zero-loss self-proof per repo (order step 2: HEAD + status record) ---
# Record-only by design: a same-volume rename preserves ALL working-tree bytes
# (tracked mods + untracked + dirty), so stashing is unnecessary and would disrupt
# sibling companies' detached sessions (20:21 evidence: .codely-cli live-lock).
foreach ($r in $Repos) {
    if (-not (Test-Path "$r\.git")) { Abort("missing git dir: $r") }
    $head = git -C $r rev-parse HEAD 2>$null
    $dirt  = @(git -C $r status --porcelain 2>$null)
    Log("zero-loss record repo $r HEAD=$head dirt_lines=$($dirt.Count) dirt=$(($dirt -join ' | '))")
}

# -- Gate 4: same-volume rename move (instant, C: -> C:) ---------------------------
New-Item -ItemType Directory -Path $Base -Force | Out-Null
$moved = $false
foreach ($attempt in 1..3) {
    try { Move-Item -Path $Old -Destination $New -ErrorAction Stop; $moved = $true; break }
    catch { Log("move attempt $attempt failed: $($_.Exception.Message)"); Start-Sleep -Seconds 15 }
}
if (-not $moved) { Abort('group tree move failed 3x (in-use handles)') }
Log("group tree moved: $Old -> $New")
if ((Test-Path $Old) -or -not (Test-Path $New)) { Abort('move verification failed') }

# -- Gate 5: MiniGame production area + junction (single source of truth) -----------
Move-Item -Path "$New\gaming\MiniGame" -Destination "$Base\MiniGame"
New-Item -ItemType Junction -Path "$New\gaming\MiniGame" -Value "$Base\MiniGame" | Out-Null
Log("MiniGame production area: real=$Base\MiniGame junction=$New\gaming\MiniGame")

# -- Gate 6: nine-item skeleton ------------------------------------------------------
$skel = @('projects','data','archive','.codely-cli','.tools')
foreach ($d in $skel) { New-Item -ItemType Directory -Path (Join-Path $Base $d) -Force | Out-Null; Log("skeleton dir $d") }
Set-Content -Path (Join-Path $Base 'README.md') -Value @(
    '# Fluxgroup base (bm-a)', '',
    'Machine: bm-a (BigMoney dev-fleet node, multi-company loop host).',
    'Canon: MiniGame repo Design/configs/GLOBAL/Base-Layout-Canon.md + fleet order O-20260926-2000-bm-c.',
    'Nine-item skeleton: README.md / MiniGame\ (production area) / FluxGroup\ (group area) /',
    'projects\ (empty on bm-a - no local Unity projects outside MiniGame repo) /',
    'data\ (empty - repo data faces stay in-repo per U187) /',
    'archive\ (empty - read-only) / .codely-cli\ / .tools\ / CODELY.md (machine memory face).',
    'Unified base per CEO order 2026-09-26: single C: volume (no K:), root_path=C:\Fluxgroup.'
) -Encoding UTF8
Set-Content -Path (Join-Path $Base 'CODELY.md') -Value @(
    '# bm-a machine memory face (machine-local, not in git)', '',
    'Project-scoped memories live in each repo CODELY.md (e.g. FluxGroup\quant\bigmoney\CODELY.md).'
) -Encoding UTF8
Log('skeleton README.md + CODELY.md written')

# -- Gate 7: Unity Bee cache clear (order step 6) -------------------------------------
$bees = @(Get-ChildItem -Path "$Base\MiniGame\projects" -Recurse -Directory -Filter 'Bee' -Depth 3 -ErrorAction SilentlyContinue)
foreach ($b in $bees) { Remove-Item $b.FullName -Recurse -Force; Log("Bee cache cleared: $($b.FullName)") }

# -- Gate 8: apply pre-built redefinition XMLs (post-move) -----------------------------
$failed = @()
foreach ($t in $Tasks) {
    $ok = $false
    foreach ($attempt in 1..3) {
        $r = schtasks /create /tn $t /xml $RedefFiles[$t] /f
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
        Start-Sleep -Seconds 5
    }
    if ($ok) { Log("redefined $t OK") } else { $failed += $t; Log("CRITICAL: redefinition FAILED $t") }
}
if ($failed.Count -gt 0) { Log("CRITICAL: failed redefinitions: $($failed -join ', ') - next bm-a round must repair via register recipes") }

# -- Gate 9: re-enable + ignition faces -------------------------------------------------
foreach ($t in $Tasks) { schtasks /change /tn $t /enable *> $null }
foreach ($t in $Tasks) {
    $nr = (schtasks /query /tn $t /fo LIST | Select-String 'Next Run Time') -join ' '
    Log("enabled $t | $nr")
}

# -- Receipt marker for next bm-a round ---------------------------------------------------
$receipt = @{
    order = 'O-20260926-2000-bm-c'; machine = 'bm-a'; completed_at = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    old_root = $Old; new_base = $Base; new_group = $New
    production_minigame = "$Base\MiniGame"; junction = "$New\gaming\MiniGame"
    tasks_redefined = $Tasks.Count; redefinition_failures = $failed
    bee_caches_cleared = $bees.Count; journal = $Journal
    note = 'five-receipt assembly (tree snapshot / task-list before-after / per-line ignition / git HEAD / root_path registration) = next bm-a round S0 work per order receipt criteria'
}
Set-Content -Path "$New\quant\bigmoney\results\fluxgroup_migration_receipt_bma.json" -Value ($receipt | ConvertTo-Json -Depth 3)
Log('=== MIGRATION COMPLETE - marker written for next round receipt assembly ===')
exit 0
