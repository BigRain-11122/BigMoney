# O-20260926-2000-bm-c executor: bm-b base unification migration (detached).
# Armed by bm-b R273 as its LAST action; outlives the round instance.
# Pattern source: bm-a r267 executor (results/_r267bma_fluxgroup_migration.ps1)
# adapted to bm-b inventory: TWO old-root literals (Desktop\Bigmoney + E:\Minigame),
# cross-volume BigMoney copy (robocopy + verify gates) instead of same-volume rename,
# plastic/ollama handle-holder faces, HKCU PATH face.
# Order six-step + fail-closed gates; ANY pre-move gate failure -> Abort() re-enables
# all tasks with old trees untouched. Post-move XML application is pre-validated
# BEFORE any mutation (Gate 0) so the post-move failure window is schtasks-only.
# ENCODING RULE: pure ASCII (powershell 5.1 ANSI decode law).
# DryRun switch: Gate 0 validation only (build+parse all redefinition XMLs, log plan,
# exit 0). No disable / no move / no registry write.
#
# r275 AMENDMENT (precheck-first + single-instance lock, bm-a v2.1 design adopted):
# run-3 21:04->22:04 ABORT burned the whole disable-first Gate-2 budget on ONE
# unbounded user face (leftover interactive shell / hung-codely parent, PID 4036)
# with all 19 lanes frozen for the hour -- and with the Tuanjie editor open the MG
# move was structurally doomed anyway (editor holds project handles no CWD probe
# needs to see for the rename to fail). Fixes: (f) Gate 0.5 precheck loop waits for
# UNBOUNDED user faces (editors by name; explorer windows / >2h-old root holders;
# hung codely chains) with ZERO mutation -- lane loops keep producing while waiting,
# freeze window starts only when the environment can actually clear; (g) single-
# instance PID lock prevents a later round from double-arming a second executor;
# (h) idempotence face: new roots already present -> exit 0 without freeze.
#
# r274 AMENDMENT (post-abort root-cause hardening): the 20:48 ABORT was caused by
# CWD-class handle holders that the CommandLine quiesce scan is STRUCTURALLY blind to
# (live probe results/_r274bmb_holder_probe.json: powershell.exe -NoLogo interactive
# shell parked at E:\Minigame, Tuanjie websockify node with CWD=MonsterInn, blender-mcp
# MCP servers with CWD=project roots -- none of these command lines mention the old
# root, so ProcHolders saw "quiescent" while the rename could never succeed).
# Fixes: (a) executor moves its own CWD off the roots; (b) Gate 1.5 kill list extended
# to blender-mcp + websockify; (c) NEW Gate 3.5 = CWD-aware sweep between record and
# move: kills CWD holders under the old MG root (interactive -NoLogo shells are
# killable -- empty shell, no preservable state; codely lane sessions route back to
# the Gate-2 wait loop instead), navigates any parked explorer folder windows away,
# fail-closed abort with the full holder roster if anything unkillable remains;
# (d) move failures now dump a 3-face holder snapshot to the journal (no more blind
# 3x-fail); (e) move retries 3 -> 6.
param([int]$MaxWaitMin = 60, [switch]$DryRun)
$ErrorActionPreference = 'Continue'
$Journal = 'C:\Users\Administrator\fluxgroup-migration-journal.log'
$Marker   = 'C:\Users\Administrator\fluxgroup-migration-aborted.flag'
$LockFile = 'C:\Users\Administrator\fluxgroup-migration-executor.lock'
$PrepDir  = Join-Path $env:TEMP 'fg-redef-bmb'
Set-Location $env:TEMP   # r274: executor must never hold a CWD on either old root (self-deadlock face)

$Base   = 'E:\Fluxgroup'
$OldBM  = 'C:\Users\Administrator\Desktop\Bigmoney'
$NewBM  = 'E:\Fluxgroup\FluxGroup\quant\bigmoney'
$OldMG  = 'E:\Minigame'
$NewMG  = 'E:\Fluxgroup\MiniGame'
$OldBMBak = 'C:\Users\Administrator\Desktop\Bigmoney.migrated-20260926'

# Discovery-verified task sets (results/_r273bmb_migration_discovery.json,
# literal scan over ALL 245 scheduled tasks, zero variants, zero dump failures).
$TasksBM = @('Bigmoney-Autofill','Bigmoney-IterationLoop','Bigmoney-LoopWatchdog')
$TasksMG = @('ArtQueueWorker','BiuNiYiXia-Autopilot','BiuNiYiXia-IterationLoop','HomeWreck-CruiseLoop',
             'MiniGameAuditTick','MiniGameClashKeepAlive','MiniGameCockpitBeat','MiniGameEngineTick',
             'MiniGameGateTick','MiniGameOllamaKeepWarm','MiniGameOllamaServe','MiniGameRadarDeepTick',
             'MiniGameRadarTick','MiniGameRedlineAudit','MiniGameTickWatchdog','PhantomEscapeGo-ProducerLoop')
$Tasks = $TasksBM + $TasksMG

function Log($m) { Add-Content -Path $Journal -Value ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) }
function TaskState($n) { (schtasks /query /tn $n /fo LIST 2>$null | Select-String '^Status:' | ForEach-Object { $_.Line -replace 'Status:\s+','' }) }

# r274: CWD probe (PEB CurrentDirectory via NtQueryInformationProcess) -- the handle
# face the CommandLine scan cannot see. Validated live in results/_r274bmb_holder_probe.ps1.
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class CwdProbe {
    [StructLayout(LayoutKind.Sequential)]
    public struct PROCESS_BASIC_INFORMATION {
        public IntPtr Reserved1;
        public IntPtr PebBaseAddress;
        public IntPtr Reserved2_0;
        public IntPtr Reserved2_1;
        public IntPtr UniqueProcessId;
        public IntPtr Reserved3;
    }
    [DllImport("ntdll.dll")]
    public static extern int NtQueryInformationProcess(IntPtr hProcess, int pic, ref PROCESS_BASIC_INFORMATION pbi, int cb, out int pSize);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern IntPtr OpenProcess(int access, bool inherit, int pid);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr baseAddress, byte[] buffer, int size, out IntPtr bytesRead);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool CloseHandle(IntPtr hObject);
    public static string GetCwd(int pid) {
        IntPtr h = OpenProcess(0x0410, false, pid);
        if (h == IntPtr.Zero) return null;
        try {
            PROCESS_BASIC_INFORMATION pbi = new PROCESS_BASIC_INFORMATION();
            int sz;
            int st = NtQueryInformationProcess(h, 0, ref pbi, Marshal.SizeOf(pbi), out sz);
            if (st != 0 || pbi.PebBaseAddress == IntPtr.Zero) return null;
            byte[] buf = new byte[8];
            IntPtr br;
            if (!ReadProcessMemory(h, (IntPtr)((long)pbi.PebBaseAddress + 0x20), buf, 8, out br)) return null;
            long pp = BitConverter.ToInt64(buf, 0);
            if (pp == 0) return null;
            byte[] us = new byte[16];
            if (!ReadProcessMemory(h, (IntPtr)(pp + 0x38), us, 16, out br)) return null;
            int len = BitConverter.ToUInt16(us, 0);
            if (len <= 0 || len > 52000) return null;
            byte[] str = new byte[len];
            long strAddr = BitConverter.ToInt64(us, 8);
            if (strAddr == 0 || !ReadProcessMemory(h, (IntPtr)strAddr, str, len, out br)) return null;
            return Encoding.Unicode.GetString(str, 0, len);
        } finally { CloseHandle(h); }
    }
}
"@
function CwdHolders($root) {
    $hits = @()
    foreach ($p in (Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) {
        if ([int]$p.ProcessId -eq $PID) { continue }             # executor self (CWD=TEMP anyway)
        $cwd = [CwdProbe]::GetCwd([int]$p.ProcessId)
        if ($cwd -and $cwd.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
            $hits += @{ pid = [int]$p.ProcessId; name = [string]$p.Name; cwd = $cwd; cmdline = [string]$p.CommandLine }
        }
    }
    return $hits
}
function HolderSnapshot() {   # 3-face failure-forensics dump for the journal
    $cw = CwdHolders $OldMG
    $cl = @()
    foreach ($p in (Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) {
        $c = $p.CommandLine
        if ($c -and $c -notmatch 'fluxgroup-migration' -and (($c -match [regex]::Escape($OldBM)) -or ($c -match [regex]::Escape($OldMG)))) { $cl += "$($p.ProcessId):$($p.Name)" }
    }
    Log("holder snapshot: cwd_holders=[$(($cw | ForEach-Object { "$($_.pid):$($_.name)@$($_.cwd) cmd=$($_.cmdline)" }) -join ' || ')] cmdline_holders=[$($cl -join ', ')]")
}

function Abort($reason) {
    Log("ABORT: $reason - re-enabling all tasks, old trees untouched")
    foreach ($t in $Tasks) { schtasks /change /tn $t /enable *> $null; Log("re-enabled $t") }
    Set-Content -Path $Marker -Value $reason
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    Log('ABORT complete - retry window open, deadline 2026-09-29 12:00')
    exit 2
}

Log('=== bm-b base unification migration START (O-20260926-2000-bm-c) ===')
if (Test-Path $Marker) { Remove-Item $Marker -Force }

# r275: single-instance lock (execute mode only) -- prevents a later round from
# double-arming a second executor while one is alive (two movers = task/disable races).
if (-not $DryRun) {
    if (Test-Path $LockFile) {
        $lp = 0; [void][int]::TryParse((Get-Content $LockFile -ErrorAction SilentlyContinue), [ref]$lp)
        $lpc = Get-Process -Id $lp -ErrorAction SilentlyContinue
        if ($lpc -and $lpc.ProcessName -match '(?i)powershell') { Log("single-instance lock: executor pid=$lp already ACTIVE - this instance exits (no mutation)"); exit 4 }
        Log("stale lock discarded (pid=$lp not alive as powershell)")
    }
    Set-Content -Path $LockFile -Value $PID
    Log("single-instance lock acquired: pid=$PID")
}

# -- Gate 0 (pre-move): build + validate all redefinition XMLs --------------------
# bm-a r267 closeout-2 battle laws: cmd nested quotes wrote empty files -> no-quote
# variant (task names + TEMP path space-free); 50B empty-guard; schtasks /xml export
# emits 8-bit bytes while decl claims UTF-16 -> write-back MUST be UTF-16LE+BOM
# ([System.Text.Encoding]::Unicode via WriteAllText); live throwaway-task round-trip
# proves /create acceptance end-to-end.
New-Item -ItemType Directory -Path $PrepDir -Force | Out-Null
$RedefFiles = @{}
foreach ($t in $Tasks) {
    $f = Join-Path $PrepDir (($t -replace '[^A-Za-z0-9_-]', '_') + '.xml')
    cmd /c schtasks /query /tn $t /xml > $f                        # no-quote (space-free names)
    if (-not (Test-Path $f) -or (Get-Item $f).Length -lt 50) { Abort("XML export empty/missing for $t") }
    $x = [System.IO.File]::ReadAllText($f)                        # BOM-aware decode (empirical 8-bit face)
    $old = if ($TasksBM -contains $t) { $OldBM } else { $OldMG }
    $new = if ($TasksBM -contains $t) { $NewBM } else { $NewMG }
    $x = $x.Replace($old, $new)
    if ($x -match [regex]::Escape($old)) { Abort("residual old literal after replace in task $t") }
    try { [void][System.Xml.XmlDocument]::new().LoadXml($x) }     # parse-validate BEFORE any mutation
    catch { Abort("redefinition XML invalid for $t : $($_.Exception.Message)") }
    [System.IO.File]::WriteAllText($f, $x, [System.Text.Encoding]::Unicode)   # UTF-16LE+BOM (bm-a verified /create face)
    $RedefFiles[$t] = $f
    Log("pre-built redef XML $t ($old -> $new, new-literal present: $($x -match [regex]::Escape($new)))")
}
Log('all redefinition XMLs pre-validated (19/19)')
# throwaway live round-trip: URI-patched copy of one redef XML -> create -> query -> delete
$TestTN = 'fg-bmb-xmltest'
$probe = $RedefFiles[$Tasks[0]]
$tx = [System.IO.File]::ReadAllText($probe, [System.Text.Encoding]::Unicode)
$tx = $tx.Replace($Tasks[0], $TestTN)
$tf = Join-Path $PrepDir 'xmltest.xml'
[System.IO.File]::WriteAllText($tf, $tx, [System.Text.Encoding]::Unicode)
schtasks /create /tn $TestTN /xml $tf /f *> $null
if ($LASTEXITCODE -ne 0) { Abort("throwaway round-trip CREATE failed (write-back face rejected)") }
$ts = schtasks /query /tn $TestTN 2>&1
if ($LASTEXITCODE -ne 0) { Abort("throwaway round-trip QUERY failed") }
schtasks /delete /tn $TestTN /f *> $null
if ($LASTEXITCODE -ne 0) { Abort("throwaway round-trip DELETE failed") }
Log("throwaway round-trip PASS (create+query+delete of $TestTN from redef XML write-back face)")
if ($DryRun) { Log('DRYRUN complete - no mutation performed; execute mode = precheck/disable/quiesce/move/skeleton/apply/enable'); exit 0 }

# -- Gate 0.5 (r275): precheck-first interactive-face wait (ZERO mutation until clear) --
# Unbounded user faces (editors by name, explorer windows on roots, >2h-old root
# holders = leftover interactive shells / hung codely chains) outlive ANY Gate-2
# budget; waiting for them AFTER the disable = frozen lanes + guaranteed ABORT
# (run-3 lesson). Kill-list residue is NOT waited for (Gates 1.5/3.5 own it) and
# young (<2h) lane rounds are NOT waited for (bounded; Gate 2 owns them once the
# short freeze starts).
$WindowDeadline = Get-Date '2026-09-29 12:00'
$EditorPat  = '^(?i)(tuanjie(\.licensing\.client)?|unity( hub)?|blender|code)$'
$ResiduePat = '(serve-warm|clash-keepalive|unity-insight-cli|blender-mcp|websockify|ollama|llama-server|plastic)'
if ((Test-Path $NewMG) -or (Test-Path "$NewBM\.git")) {
    Log('precheck: new roots already present (migration done?) - exiting 0 WITHOUT freeze')
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    exit 0
}
function PrecheckBlockers() {
    $b = @()
    foreach ($p in (Get-Process -ErrorAction SilentlyContinue)) {
        if ($p.ProcessName -match $EditorPat) { $b += "editor:$($p.Id):$($p.ProcessName)" }
    }
    foreach ($root in @($OldMG, $OldBM)) {
        foreach ($h in (CwdHolders $root)) {
            if ($h.name -match $ResiduePat -or $h.cmdline -match $ResiduePat) { continue }
            if ($h.name -match '(?i)explorer') { $b += "explorer-cwd:$($h.pid)@$($h.cwd)"; continue }
            # r274 killable class: empty interactive shells (no script payload) -- Gate 3.5 owns them
            if ($h.name -match '(?i)(powershell|cmd|wscript|conhost|windowsterminal)' -and [string]$h.cmdline -notmatch '(-File|-Command|-enc|-EncodedCommand|\.ps1|\.py|\.js)') { continue }
            $age = $null; try { $age = ((Get-Date) - (Get-Process -Id $h.pid -ErrorAction Stop).StartTime).TotalHours } catch {}
            if ($null -ne $age -and $age -lt 2.0) { continue }        # young = active lane round
            $b += "cwd-holder(age>2h):$($h.pid):$($h.name)@$($h.cwd)"
        }
    }
    foreach ($p in (Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) {
        $cl = $p.CommandLine
        if (-not $cl) { continue }
        if ($cl -match 'fluxgroup-migration') { continue }
        if (-not (($cl -match [regex]::Escape($OldBM)) -or ($cl -match [regex]::Escape($OldMG)))) { continue }
        if ($cl -match $ResiduePat) { continue }
        if ([string]$p.Name -notmatch '(?i)(codely|powershell|cmd|wscript|node|python)') { continue }
        $age = $null; try { $age = ((Get-Date) - (Get-Process -Id $p.ProcessId -ErrorAction Stop).StartTime).TotalHours } catch {}
        if ($null -ne $age -and $age -lt 2.0) { continue }            # young = active lane round
        $b += "cmd-holder(age>2h):$($p.ProcessId):$($p.Name)"
    }
    return $b
}
Log('precheck: waiting for unbounded user faces (zero mutation; loops keep running) - window deadline 2026-09-29 12:00')
while ($true) {
    $pb = PrecheckBlockers
    if ($pb.Count -eq 0) { Log('precheck CLEAR: zero unbounded user faces - starting freeze window'); break }
    Log("precheck waiting: [$($pb -join ', ')]")
    if ((Get-Date) -gt $WindowDeadline) {
        Set-Content -Path $Marker -Value 'precheck window deadline 2026-09-29 12:00 expired with unbounded user faces still present (zero mutation performed)'
        Log('precheck: order window deadline reached - exiting WITHOUT any mutation; retry needs a new CEO order')
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
        exit 3
    }
    Start-Sleep -Seconds 60
}

# -- Gate 1: disable all production tasks (running instances unaffected) -----------
foreach ($t in $Tasks) { $r = schtasks /change /tn $t /disable; Log("disable $t -> $(@($r) -join ' ')") }

# -- Gate 1.5: kill RESTARTABLE PERSISTENT holders BEFORE quiesce ------------------
# Live-probed faces (r273): ollama serve stack = wscript(8376)->powershell serve-warm.ps1
# ->ollama.exe serve->llama-server.exe (persistent, holds E:\Minigame handles, would
# deadlock the CommandLine quiesce scan); unity-insight daemon --project E:\Minigame\*
# (persistent, holds project-tree handles). All restartable: Ollama via
# MiniGameOllamaServe task at re-enable, insight daemon respawns on demand from new path.
$KillCl = @('serve-warm\.ps1', 'clash-keepalive', 'unity-insight-cli\.js.*--project E:.Minigame')
# r274 NOTE: blender-mcp / websockify CWD holders are NOT pre-quiesce killed here --
# they may be live MCP infrastructure of in-flight lane rounds (HomeWreck/BiuNiYiXia).
# They are killed ONLY in Gate 3.5 (post-quiesce, CWD-aware) where they are residue.
foreach ($p in (Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) {
    $cl = $p.CommandLine
    if (-not $cl) { continue }
    if ($cl -match 'fluxgroup-migration') { continue }
    $hit = $false
    foreach ($pat in $KillCl) { if ($cl -match $pat) { $hit = $true; break } }
    if (-not $hit) { continue }
    Log("kill persistent holder pid=$($p.ProcessId) name=$($p.Name)")
    taskkill /F /PID $p.ProcessId *> $null
}
foreach ($n in @('ollama', 'llama-server')) {
    foreach ($p in (Get-Process -Name $n -ErrorAction SilentlyContinue)) { Log("kill $n pid=$($p.Id)"); taskkill /F /PID $p.Id *> $null }
}
foreach ($svc in @('plasticchangetrackerservice','plasticd')) {
    $r = sc.exe stop $svc 2>&1; Log("sc stop $svc -> $r")
    if (Get-Process -Name $svc -ErrorAction SilentlyContinue) { taskkill /F /IM "$svc.exe" *> $null; Log("taskkill fallback $svc") }
}
Log('persistent holder faces handled (serve-warm chain / ollama / llama-server / insight daemon / clash-keepalive / plastic)')

# -- Gate 2: wait for all in-flight instances to finish naturally -------------------
# bm-a r267 closeout-3 law: task-status alone is BLIND to detached fire-and-forget
# codely sessions spawned by loop rounds -> add Win32_Process CommandLine scan for
# anything referencing either old root (excludes this executor's own script path).
$deadline = (Get-Date).AddMinutes($MaxWaitMin)
# ASCII-only source (PS5.1 ANSI decode law): localized status matched via char codes.
$RunPat = 'Running|' + [string][char]0x8FD0 + [string][char]0x884C   # English 'Running' or CJK yun-xing
function ProcHolders() {
    $hits = @()
    foreach ($p in (Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) {
        $cl = $p.CommandLine
        if (-not $cl) { continue }
        if ($cl -match 'fluxgroup-migration') { continue }          # this executor + journal probes
        if (($cl -match [regex]::Escape($OldBM)) -or ($cl -match [regex]::Escape($OldMG))) { $hits += "$($p.ProcessId):$($p.Name)" }
    }
    return $hits
}
while ($true) {
    $running = @()
    foreach ($t in $Tasks) { if ((TaskState $t) -match $RunPat) { $running += $t } }
    $procs = ProcHolders
    if ($running.Count -eq 0 -and $procs.Count -eq 0) { Log('all production task instances + old-root processes quiescent'); break }
    Log("waiting: tasks=[$($running -join ', ')] procs=[$($procs -join ', ')]")
    if ((Get-Date) -gt $deadline) { Abort("in-flight still running after $MaxWaitMin min: tasks=[$($running -join ', ')] procs=[$($procs -join ', ')]") }
    Start-Sleep -Seconds 30
}

# -- Gate 3: zero-loss RECORD-ONLY journal (order step 2; bm-a r267 closeout-3 law) ----
# Both moves are byte-preserving (MG = same-volume rename; BM = robocopy full-tree copy
# of current bytes incl tracked mods + untracked) -> stash mutates nothing that the move
# would lose; stash instead risks disrupting sibling WIP (BigLife live-lock precedent).
# Record HEAD + dirt lines for the receipt; verification moves to copy-equality gates.
foreach ($repo in @($OldBM, "$OldMG\MiniGame")) {
    if (-not (Test-Path "$repo\.git")) { Abort("missing git dir: $repo") }
    $head = git -C $repo rev-parse HEAD 2>$null
    $dirt = @(git -C $repo status --porcelain 2>$null)
    Log("record repo $repo HEAD=$head dirt_lines=$($dirt.Count) dirt=$(($dirt -join ' | '))")
}
$BMPorcelainOld = (git -C $OldBM status --porcelain 2>$null) -join '|'
Log('zero-loss record gate done (record-only, no mutation; copy-equality gates at Gate 5)')

# -- Gate 3.5 (r274): CWD-aware sweep of old-MG-root handle holders -------------------
# The CommandLine scan above cannot see CWD holders (20:48 ABORT root cause). Policy:
#  - codely.exe lane sessions still alive -> route BACK to the Gate-2 wait loop (they
#    own round state; never kill a live lane round);
#  - empty interactive shells (powershell -NoLogo), blender-mcp, websockify, other
#    service residue -> killable (no preservable state; journal records pid+cmdline);
#  - explorer folder windows parked under the old root -> Navigate away to C:\ (no
#    window closure, zero popups, silence law);
#  - anything unkillable left -> fail-closed Abort with the full roster.
foreach ($round3_5 in 1..30) {
    $holders = CwdHolders $OldMG
    if ($holders.Count -eq 0) { Log('Gate 3.5: zero CWD holders under old MG root'); break }
    $laneBusy = $false
    foreach ($h in $holders) {
        if ($h.cmdline -match 'codely\.exe') { $laneBusy = $true; Log("Gate 3.5: lane session still alive, back to wait: pid=$($h.pid) cwd=$($h.cwd)"); continue }
        if ($h.name -match '(?i)(editor|tuanjie|unity|blender|explorer)') { Abort("protected user-face process holds old-root CWD (manual intervention): pid=$($h.pid) name=$($h.name) cwd=$($h.cwd)") }
        Log("Gate 3.5: killing CWD holder pid=$($h.pid) name=$($h.name) cwd=$($h.cwd) cmd=$($h.cmdline)")
        taskkill /F /PID $h.pid *> $null
    }
    if ($laneBusy) { Log('Gate 3.5: waiting 60s for lane round(s) to finish, then re-sweep'); Start-Sleep -Seconds 60; continue }
    Start-Sleep -Seconds 3
    $again = CwdHolders $OldMG
    if ($again.Count -gt 0) {
        Log("Gate 3.5: after kill sweep, still held: $(($again | ForEach-Object { "$($_.pid):$($_.name)@$($_.cwd)" }) -join ' || ')")
        if ($round3_5 -eq 30) { Abort("CWD holders unkillable after 30 sweeps: $(($again | ForEach-Object { "$($_.pid):$($_.name)" }) -join ', ')") }
    } else { Log('Gate 3.5: zero CWD holders under old MG root (post-kill)'); break }
}
# explorer folder windows parked under the old root: navigate away (window preserved)
try {
    $sh = New-Object -ComObject Shell.Application
    foreach ($w in $sh.Windows()) {
        $loc = [string]$w.LocationURL
        if ($loc -like ('file:///' + ($OldMG -replace '\\','/') + '*')) {
            Log("Gate 3.5: navigating parked explorer window away: $loc")
            $w.Navigate('file:///C:/') | Out-Null
            Start-Sleep -Seconds 2
        }
    }
} catch { Log("Gate 3.5: explorer window sweep skipped: $($_.Exception.Message)") }

# -- Gate 4: same-volume rename move E:\Minigame -> E:\Fluxgroup\MiniGame (instant) ---
if (Test-Path $NewMG) { Abort("$NewMG already exists (partial migration residue?)") }
New-Item -ItemType Directory -Path $Base -Force | Out-Null
$moved = $false
foreach ($attempt in 1..6) {
    try { Move-Item -Path $OldMG -Destination $NewMG -ErrorAction Stop; $moved = $true; break }
    catch {
        Log("MG move attempt $attempt failed: $($_.Exception.Message)")
        HolderSnapshot   # r274: no more blind failures -- 3-face forensics to journal
        Start-Sleep -Seconds 15
    }
}
if (-not $moved) { Abort('E:\Minigame tree move failed 6x (in-use handles; snapshots above)') }
if ((Test-Path $OldMG) -or -not (Test-Path "$NewMG\MiniGame\.git")) { Abort('MG move verification failed') }
Log("production tree moved: $OldMG -> $NewMG (MiniGame repo verified at new root)")

# -- Gate 5: BigMoney cross-volume copy (robocopy) + verification gates -------------
if (Test-Path $NewBM) { Abort("$NewBM already exists (partial migration residue?)") }
New-Item -ItemType Directory -Path (Split-Path $NewBM) -Force | Out-Null
$rcLog = Join-Path $env:TEMP 'fg-robocopy-bmb.log'
$rc = Start-Process -FilePath robocopy.exe -ArgumentList "`"$OldBM`" `"$NewBM`" /E /COPY:DAT /DCOPY:DAT /R:1 /W:5 /MT:16 /NFL /NDL /NP /LOG:$rcLog" -Wait -PassThru -WindowStyle Hidden
Log("robocopy exit=$($rc.ExitCode) log=$rcLog")
if ($rc.ExitCode -ge 8) {
    Log("removing partial copy $NewBM after robocopy failure (old tree intact)")
    Remove-Item $NewBM -Recurse -Force -ErrorAction SilentlyContinue
    Abort("robocopy failed (exit $($rc.ExitCode) >= 8); partial copy removed, old tree untouched")
}
$oldHead = git -C $OldBM rev-parse HEAD 2>$null
$newHead = git -C $NewBM rev-parse HEAD 2>$null
if ($oldHead -ne $newHead) { Abort("HEAD mismatch old=$oldHead new=$newHead") }
$BMPorcelainNew = (git -C $NewBM status --porcelain 2>$null) -join '|'
if ($BMPorcelainNew -ne $BMPorcelainOld) { Abort("porcelain mismatch after copy (old='$BMPorcelainOld' new='$BMPorcelainNew')") }
$oldCount = (Get-ChildItem $OldBM -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object).Count
$newCount = (Get-ChildItem $NewBM -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object).Count
if ($oldCount -ne $newCount) { Abort("file count mismatch old=$oldCount new=$newCount") }
Log("copy verification PASS (HEAD=$newHead, clean tree, file count $newCount == $oldCount)")
$renamed = $false
foreach ($attempt in 1..3) {
    try { Move-Item -Path $OldBM -Destination $OldBMBak -ErrorAction Stop; $renamed = $true; break }
    catch { Log("old-root rename attempt $attempt failed: $($_.Exception.Message)"); Start-Sleep -Seconds 10 }
}
if ($renamed) { Log("old root renamed to backup: $OldBMBak (deletion = next bm-b round after ignition receipt)") }
else { Log("NOTE: old root rename failed (open handles) - tasks repointed to new root anyway; old tree = stale no-task backup, cleanup next round") }

# -- Gate 6: nine-item skeleton + group-area faces -------------------------------------
foreach ($d in @("$Base\projects", "$Base\data", "$Base\archive", "$Base\.codely-cli", "$Base\.tools", "$Base\FluxGroup\gaming", "$Base\FluxGroup\quant")) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null; Log("skeleton dir $d")
}
Set-Content -Path (Join-Path $Base 'README.md') -Value @(
    '# Fluxgroup base (bm-b)', '',
    'Machine: bm-b (BigMoney fleet compute-node, multi-company loop host).',
    'root_path: E:\Fluxgroup (no physical K:; optional subst K: facade = CEO navigation only,',
    '  non-persistent across reboot, never used in task definitions).',
    'Canon: MiniGame repo Design/configs/GLOBAL canon doc v2.0 (U238) + fleet order O-20260926-2000-bm-c.',
    'Nine-item skeleton: README.md / MiniGame\ (production area, former E:\Minigame) /',
    'FluxGroup\ (group area: quant\bigmoney real repo; gaming\MiniGame junction -> production real) /',
    'projects\ (empty on bm-b: Unity/Plastic workspaces live inside MiniGame\ per-machine-role) /',
    'data\ (empty: repo data faces stay in-repo per U187) /',
    'archive\ (empty: E:\AGENT / E:\AGENT_repo_restore / E:\GPU / E:\Graybox kept in place at drive root,',
    '  classified non-production, see results/fleet_unification/bm-b-ack-20260926.json) /',
    '.codely-cli\ / .tools\ / CODELY.md (machine memory face).',
    'Migration receipt: FluxGroup\quant\bigmoney\results\fluxgroup_migration_receipt_bmb.json'
) -Encoding UTF8
Set-Content -Path (Join-Path $Base 'CODELY.md') -Value @(
    '# bm-b machine memory face (machine-local, not in git)', '',
    'Project-scoped memories live in each repo CODELY.md (e.g. FluxGroup\quant\bigmoney\CODELY.md).',
    'Migration journal: C:\Users\Administrator\fluxgroup-migration-journal.log (O-20260926-2000-bm-c).'
) -Encoding UTF8
Log('skeleton README.md + CODELY.md written (nine items complete)')

# -- Gate 6.5: gaming\MiniGame junction (single source of truth, no re-clone) -----------
New-Item -ItemType Junction -Path "$Base\FluxGroup\gaming\MiniGame" -Value "$NewMG\MiniGame" -ErrorAction SilentlyContinue | Out-Null
Log("junction: $Base\FluxGroup\gaming\MiniGame -> $NewMG\MiniGame")

# -- Gate 7: HKCU PATH face (ffmpeg entry follows the moved tree) -----------------------
try {
    $pv = (Get-ItemProperty -Path 'HKCU:\Environment' -Name Path).Path
    $pn = $pv.Replace('E:\Minigame\Tools\ffmpeg\bin', 'E:\Fluxgroup\MiniGame\Tools\ffmpeg\bin')
    if ($pn -ne $pv) { Set-ItemProperty -Path 'HKCU:\Environment' -Name Path -Value $pn -Type String; Log("HKCU PATH repointed (ffmpeg entry)") }
    else { Log('HKCU PATH: no old literal found (already migrated or absent)') }
} catch { Log("HKCU PATH face ERROR (non-fatal): $($_.Exception.Message)") }

# -- Gate 8: Unity/Tuanjie Bee cache clear (order step 6, G15 pit family) ---------------
$bees = @(Get-ChildItem -Path "$NewMG\*\Library\Bee" -Directory -ErrorAction SilentlyContinue)
foreach ($b in $bees) { Remove-Item $b.FullName -Recurse -Force; Log("Bee cache cleared: $($b.FullName)") }
Log("Bee scan done: $($bees.Count) cleared")

# -- Gate 9: apply pre-built redefinition XMLs (post-move) --------------------------------
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
if ($failed.Count -gt 0) { Log("CRITICAL: failed redefinitions: $($failed -join ', ') - next bm-b round must repair via register recipes") }

# -- Gate 10: restart services + re-enable + ignition faces ------------------------------
foreach ($svc in @('plasticchangetrackerservice','plasticd')) { $r = sc.exe start $svc 2>&1; Log("sc start $svc -> $r") }
foreach ($t in $Tasks) {
    if ($failed -contains $t) { schtasks /change /tn $t /disable *> $null; Log("left DISABLED (redefinition failed, old path dead): $t - next round repairs via register recipes"); continue }
    schtasks /change /tn $t /enable *> $null
}
foreach ($t in $Tasks) {
    $nr = (schtasks /query /tn $t /fo LIST | Select-String 'Next Run Time') -join ' '
    Log("enabled $t | $nr")
}
Log('all tasks re-enabled; ignition = natural next tick per line (receipt assembly = next bm-b round)')

# -- Gate 11: optional subst K: facade (CEO navigation only) -----------------------------
if (Test-Path 'K:\') { Log("K: already mapped (facade present)") }
else { $r = subst K: $Base 2>&1; Log("subst K: -> $Base => $r (CEO-nav facade, non-persistent)") }

# -- Receipt marker for next bm-b round ---------------------------------------------------
$receipt = @{
    order = 'O-20260926-2000-bm-c'; machine = 'bm-b'; completed_at = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    old_bm_root = $OldBM; old_bm_backup = $OldBMBak; new_bm_root = $NewBM
    old_mg_root = $OldMG; new_mg_root = $NewMG; base_root = $Base
    tasks_redefined = $Tasks.Count; redefinition_failures = $failed
    bee_caches_cleared = $bees.Count; journal = $Journal; robocopy_log = $rcLog
    git_head = $newHead; file_count = $newCount
    note = 'five-receipt assembly (tree snapshot / task-list before-after / per-line ignition / git HEAD / root_path registration) = next bm-b round S0 work per order receipt criteria; delete old-root backup after ignition receipt'
}
Set-Content -Path "$NewBM\results\fluxgroup_migration_receipt_bmb.json" -Value ($receipt | ConvertTo-Json -Depth 3)
Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
Log('=== MIGRATION COMPLETE - marker written for next round receipt assembly ===')
exit 0
