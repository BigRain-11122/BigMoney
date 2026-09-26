# O-20260926-2000-bm-c executor v2 (bm-a): base-unification migration, retry-hardened.
# v1 (r267) battle log: 20:19 XML-empty abort (fixed) / 20:21 stash-face abort (Gate-3
# record-only now) / 20:22 disable-first + 40min quiesce wait froze whole company then
# aborted on PERMANENT interactive holders (Code.exe = CEO's editor session, PopupWitness
# sentinel). v2 redesign:
#   - Gate 0.5 PRECHECK LOOP runs BEFORE any mutation: waits (poll, no freeze) until no
#     interactive user app (Code/Tuanjie/Unity/...) references the old root. CEO closing
#     the editor is the trigger; company loops keep running while waiting.
#   - Gate 1.5 KILL-LIST: persistent sentinels + detached refresh pullers referencing
#     the old root are killed at proceed time (all are checkpoint/respawn self-healing
#     by design: PopupWitness witness, ollama serve-warm, update_* refresh spawners).
#   - Internal retry: drain timeout / interactive reappearing mid-drain / move failure
#     -> re-enable tasks + back to precheck (soft unwind). Hard Abort only on: deadline
#     exceeded, 3 consecutive same-holder drain timeouts, 3 total move failures, XML
#     invalid, missing git dir, target already occupied.
# Single-instance: PID lockfile; stale lock (PID dead / not a migration proc) is taken over.
# ENCODING RULE: pure ASCII (powershell 5.1 ANSI decode law).
param([int]$DrainWaitMin = 15, [int]$PrecheckPollSec = 60)
$ErrorActionPreference = 'Continue'
$Journal  = 'C:\Users\sjs20\fluxgroup-migration-journal.log'
$Old      = 'C:\Users\sjs20\Desktop\FluxGroup'
$Base     = 'C:\Fluxgroup'
$New      = 'C:\Fluxgroup\FluxGroup'
$Marker   = 'C:\Users\sjs20\fluxgroup-migration-aborted.flag'
$Lock     = 'C:\Users\sjs20\fluxgroup-migration.lock'
$PrepDir  = Join-Path $env:TEMP 'fg-redef'
$HardDeadline = Get-Date -Year 2026 -Month 9 -Day 29 -Hour 12 -Minute 0 -Second 0   # order window end

function Log($m) { Add-Content -Path $Journal -Value ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function TaskState($n) { (schtasks /query /tn $n /fo LIST 2>$null | Select-String '^Status:' | ForEach-Object { $_.Line -replace 'Status:\s+','' }) }

$Mini = @('MiniGameAuditTick','MiniGameBoardForge','MiniGameCockpitBeat','MiniGameDailyDigest','MiniGameEditorSentry','MiniGameEngineTick','MiniGameEvolutionTick','MiniGameGateTick','MiniGameHousekeeping','MiniGameOllamaKeepWarm','MiniGameOllamaServe','MiniGamePolicyTick','MiniGamePopupWitness','MiniGameRadarDeepTick','MiniGameRadarTick','MiniGameRedlineAudit','MiniGameResearchTick','MiniGame-SiliconWatchTick','MiniGameTickWatchdog','MiniGameTjcloudSync')
$Tasks = @('Bigmoney-Autofill','Bigmoney-LoopWatchdog','Bigmoney-IterationLoop','Bigmoney-IntradayMarks','BigCompute-OSLoop','BigDomain-OSLoop','BigLife-OSLoop','BigStream-OSLoop','FluxBoardAuto','FluxGroup-DecisionRound','FluxGroup-EvolutionTick','FluxGroup-NightRound','FluxGroup-OrderSentinel','FluxVerse-DevLoop','FluxVerseTick','GimmeAll-AutoSentinel') + $Mini
$Dead = 'MoneyAutoGuardian'   # absent target - disable-only, adjudication to lanes
$Repos = @($Old, "$Old\quant\bigmoney", "$Old\compute\BigCompute", "$Old\domain\BigDomain", "$Old\life\BigLife", "$Old\media\BigStream", "$Old\gaming\MiniGame", "$Old\gaming\FluxVerse")

# Interactive user apps: NEVER killed (CEO session face); their old-root presence blocks
# the precheck until the user closes them. Tuanjie/Unity appeared live in v1 evidence.
$InteractiveNames = @('Code.exe','Tuanjie.exe','Unity.exe','Unity Hub.exe','Unity.Hub.exe','devenv.exe','notepad.exe','Notepad++.exe','winmergeu.exe','explorer.exe')
# Killable persistent/respawnable faces (checkpoint or sentinel self-healing by design).
$KillablePatterns = @('PopupWitness','ollama','llama-server','plastic','insight','update_moneyflow','update_sina_mf','update_options','update_ths_panel','update_fund_premium','ah_panel_puller','update_futures','update_heat','update_lhb')

function HardAbort($reason) {
    Log("ABORT: $reason - re-enabling all tasks, old tree untouched")
    foreach ($t in $Tasks) { schtasks /change /tn $t /enable *> $null; Log("re-enabled $t") }
    Set-Content -Path $Marker -Value $reason
    Log('ABORT complete - retry requires relaunch (window deadline 2026-09-29 12:00)')
    if (Test-Path $Lock) { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
    exit 2
}
function SoftUnwind($reason) {
    Log("UNWIND: $reason - re-enabling all tasks, back to precheck (no marker)")
    foreach ($t in $Tasks) { schtasks /change /tn $t /enable *> $null }
}
function Scan-OldRootProcs {
    @(Get-CimInstance Win32_Process -Filter "Name != 'System Idle Process'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -like "*$Old*" -and $_.ProcessId -ne $PID -and $_.CommandLine -notmatch 'fluxgroup_migration' } |
        ForEach-Object { $_ })
}

# ---- single-instance lock ----------------------------------------------------------
if (Test-Path $Lock) {
    $oldPid = 0; [int]::TryParse((Get-Content $Lock -ErrorAction SilentlyContinue), [ref]$oldPid) | Out-Null
    $holder = Get-CimInstance Win32_Process -Filter "ProcessId=$oldPid" -ErrorAction SilentlyContinue
    if ($holder -and $holder.CommandLine -and $holder.CommandLine -match 'fluxgroup_migration') {
        Log("another live executor instance running (pid $oldPid) - this instance exits quietly"); exit 0
    }
    Log("stale lock (pid $oldPid not a live executor) - taking over")
}
Set-Content -Path $Lock -Value $PID

Log('=== bm-a migration v2 START (O-20260926-2000-bm-c, precheck-first design) ===')
if (Test-Path $Marker) { Remove-Item $Marker -Force }
if ((Test-Path $Base) -and (Get-ChildItem $Base -Force -ErrorAction SilentlyContinue)) { HardAbort('C:\Fluxgroup already exists and non-empty') }

# ---- Gate 0: build + validate all redefinition XMLs (no mutation) ------------------
New-Item -ItemType Directory -Path $PrepDir -Force | Out-Null
$RedefFiles = @{}
foreach ($t in $Tasks) {
    $f = Join-Path $PrepDir (($t -replace '[^A-Za-z0-9_-]', '_') + '.xml')
    cmd /c "schtasks /query /tn $t /xml > $f"                     # no-quote variant (space-free names; v1 20:19 law)
    if (-not (Test-Path $f) -or (Get-Item $f).Length -lt 50) { HardAbort("XML export empty for $t") }
    $x = [System.IO.File]::ReadAllText($f)                        # no-BOM UTF-8 face
    $x = $x.Replace($Old, $New)
    try { [void][System.Xml.XmlDocument]::new().LoadXml($x) }     # parse-validate BEFORE any mutation
    catch { HardAbort("redefinition XML invalid for $t : $($_.Exception.Message)") }
    [System.IO.File]::WriteAllText($f, $x, [System.Text.Encoding]::Unicode)   # UTF-16LE+BOM write-back (v1 20:2x round-trip law)
    $RedefFiles[$t] = $f
    Log("pre-built redef XML $t ($((Get-Item $f).Length)B)")
}
Log('all redefinition XMLs pre-validated')

# ---- attempt loop: precheck -> disable -> kill-list -> drain -> move -> finish ------
$drainFailsSame = 0; $lastDrainSet = ''; $moveFailsTotal = 0; $attempt = 0
while ($true) {
    $attempt++

    # Gate 0.5: precheck loop (NO mutation; company keeps running while we wait)
    $lastInter = $null; $lastBeat = Get-Date
    while ($true) {
        $inter = @(Scan-OldRootProcs | Where-Object { $InteractiveNames -contains $_.Name })
        $sig = ($inter | ForEach-Object { "$($_.Name)/$($_.ProcessId)" } | Sort-Object) -join ', '
        if ($inter.Count -eq 0) { Log('precheck PASS: no interactive holder references old root'); break }
        if ($sig -ne $lastInter) { Log("precheck waiting on interactive holders: $sig"); $lastInter = $sig }
        elseif (((Get-Date) - $lastBeat).TotalMinutes -ge 15) { Log("precheck still waiting: $sig"); $lastBeat = Get-Date }
        if ((Get-Date) -gt $HardDeadline) { HardAbort("deadline 09-29 12:00 exceeded while interactive holders present: $sig") }
        Start-Sleep -Seconds $PrecheckPollSec
    }

    # Gate 1: disable all company tasks (running instances unaffected)
    foreach ($t in $Tasks) { $r = schtasks /change /tn $t /disable; Log("disable $t -> $(@($r) -join ' ')") }
    schtasks /change /tn $Dead /disable *> $null; Log("disable dead task $Dead (absent target, adjudication pending)")

    # Gate 1.5: kill persistent/respawnable holders (checkpoint self-healing by design)
    $killProcs = @(Scan-OldRootProcs | Where-Object { $n = $_.CommandLine; ($KillablePatterns | Where-Object { $n -match $_ }).Count -gt 0 })
    foreach ($p in $killProcs) {
        Log("kill-list: $($p.Name)/$($p.ProcessId) (pattern match, respawn/checkpoint self-healing)")
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
    if ($killProcs.Count -gt 0) { Start-Sleep -Seconds 3 }

    # Gate 2: drain wait (in-flight loop instances exit naturally; fire-and-forget codely
    # sessions are caught by the command-line scan, v1 20:21 law)
    $deadline = (Get-Date).AddMinutes($DrainWaitMin)
    $unwind = ''; $quiescent = $false
    while ($true) {
        $running = @()
        foreach ($t in $Tasks) { if ((TaskState $t) -eq 'Running') { $running += $t } }
        $live = @(Scan-OldRootProcs)
        $interLive = @($live | Where-Object { $InteractiveNames -contains $_.Name })
        $otherLive = @($live | Where-Object { $InteractiveNames -notcontains $_.Name })
        if ($running.Count -eq 0 -and $live.Count -eq 0) { $quiescent = $true; break }
        if ($running.Count -eq 0 -and $otherLive.Count -eq 0 -and $interLive.Count -gt 0) {
            $unwind = "interactive holder appeared mid-drain: $(($interLive | ForEach-Object { $_.Name + '/' + $_.ProcessId }) -join ', ')"; break
        }
        if ((Get-Date) -gt $deadline) {
            $set = ($live | ForEach-Object { "$($_.Name)/$($_.ProcessId)" } | Sort-Object) -join ', '
            if ($set -eq $lastDrainSet) { $drainFailsSame++ } else { $drainFailsSame = 1; $lastDrainSet = $set }
            if ($drainFailsSame -ge 3) { HardAbort("persistent non-interactive holder x3 drains: $set") }
            $unwind = "drain timeout after $DrainWaitMin min: tasks=[$($running -join ', ')] procs=[$set]"; break
        }
        Start-Sleep -Seconds 30
    }
    if ($unwind -ne '') { SoftUnwind($unwind); Start-Sleep -Seconds 60; continue }
    if (-not $quiescent) { SoftUnwind('drain loop exit without quiescence'); Start-Sleep -Seconds 60; continue }
    Log('all company task instances + tree-referencing processes quiescent')

    # Gate 3: zero-loss record per repo (record-only; same-volume rename preserves
    # all working-tree bytes incl tracked mods + untracked; v1 20:21 stash-face lesson)
    $gate3ok = $true
    foreach ($r in $Repos) {
        if (-not (Test-Path "$r\.git")) { Log("missing git dir: $r"); $gate3ok = $false; break }
        $head = git -C $r rev-parse HEAD 2>$null
        $dirt = @(git -C $r status --porcelain 2>$null)
        Log("zero-loss record repo $r HEAD=$head dirt_lines=$($dirt.Count) dirt=$(($dirt -join ' | '))")
    }
    if (-not $gate3ok) { SoftUnwind('Gate-3 git-dir missing (recorded above, needs human look)'); Start-Sleep -Seconds 300; continue }

    # Gate 4: same-volume rename move (instant, C: -> C:)
    New-Item -ItemType Directory -Path $Base -Force | Out-Null
    $moved = $false
    foreach ($try in 1..3) {
        try { Move-Item -Path $Old -Destination $New -ErrorAction Stop; $moved = $true; break }
        catch { Log("move try $try failed: $($_.Exception.Message)"); Start-Sleep -Seconds 15 }
    }
    if (-not $moved) {
        $moveFailsTotal++
        $holders = (Scan-OldRootProcs | ForEach-Object { "$($_.Name)/$($_.ProcessId)" }) -join ', '
        if ($moveFailsTotal -ge 3) { HardAbort("move failed 3x total (cwd-holder below or fs lock): [$holders]") }
        SoftUnwind("move attempt set failed (total $moveFailsTotal) - likely invisible cwd holder: [$holders]")
        Start-Sleep -Seconds 120; continue
    }
    Log("group tree moved: $Old -> $New")
    if ((Test-Path $Old) -or -not (Test-Path $New)) { HardAbort('move verification failed') }

    # Gate 5: MiniGame production area + junction (single source of truth)
    Move-Item -Path "$New\gaming\MiniGame" -Destination "$Base\MiniGame"
    New-Item -ItemType Junction -Path "$New\gaming\MiniGame" -Value "$Base\MiniGame" | Out-Null
    Log("MiniGame production area: real=$Base\MiniGame junction=$New\gaming\MiniGame")

    # Gate 6: nine-item skeleton
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

    # Gate 7: Unity Bee cache clear (order step 6)
    $bees = @(Get-ChildItem -Path "$Base\MiniGame\projects" -Recurse -Directory -Filter 'Bee' -Depth 3 -ErrorAction SilentlyContinue)
    foreach ($b in $bees) { Remove-Item $b.FullName -Recurse -Force; Log("Bee cache cleared: $($b.FullName)") }

    # Gate 8: apply pre-built redefinition XMLs (post-move)
    $failed = @()
    foreach ($t in $Tasks) {
        $ok = $false
        foreach ($try in 1..3) {
            $r = schtasks /create /tn $t /xml $RedefFiles[$t] /f
            if ($LASTEXITCODE -eq 0) { $ok = $true; break }
            Start-Sleep -Seconds 5
        }
        if ($ok) { Log("redefined $t OK") } else { $failed += $t; Log("CRITICAL: redefinition FAILED $t") }
    }
    if ($failed.Count -gt 0) { Log("CRITICAL: failed redefinitions: $($failed -join ', ') - next bm-a round must repair via register recipes") }

    # Gate 9: re-enable + ignition faces
    foreach ($t in $Tasks) { schtasks /change /tn $t /enable *> $null }
    foreach ($t in $Tasks) {
        $nr = (schtasks /query /tn $t /fo LIST | Select-String 'Next Run Time') -join ' '
        Log("enabled $t | $nr")
    }

    # Receipt marker for next bm-a round
    $receipt = @{
        order = 'O-20260926-2000-bm-c'; machine = 'bm-a'; completed_at = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        old_root = $Old; new_base = $Base; new_group = $New
        production_minigame = "$Base\MiniGame"; junction = "$New\gaming\MiniGame"
        tasks_redefined = $Tasks.Count; redefinition_failures = $failed
        bee_caches_cleared = $bees.Count; journal = $Journal
        note = 'five-receipt assembly (tree snapshot / task-list before-after / per-line ignition / git HEAD / root_path registration) = next bm-a round S0 work per order receipt criteria'
    }
    Set-Content -Path "$New\quant\bigmoney\results\fluxgroup_migration_receipt_bma.json" -Value ($receipt | ConvertTo-Json -Depth 3)
    Remove-Item $Lock -Force -ErrorAction SilentlyContinue
    Log('=== MIGRATION COMPLETE - marker written for next round receipt assembly ===')
    exit 0
}
