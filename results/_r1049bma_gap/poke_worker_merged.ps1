# fleet-poke-worker.ps1 - FleetLink background pull+wake worker v1.8 (CEO order O-20261009-1750 "very fast sync").
# v1.10 (2026-10-18 hung-round revival, bm-a fleet-ops seat, CEO order "recover
# the fleet - my accidental shutdown of other machines' tasks"): a Running
# round-runner task (Bigmoney-IterationLoop / MiniGameEngineTick) whose LANE
# heartbeat has been frozen >120 min is a HUNG round (bm-c 10-14 / 10-17 / 10-18
# three occurrences; the 10-17 verdict said remote channels can only signal and
# repair needed on-machine Stop-ScheduledTask->Start - this closes that gap).
# Evidence-gated: only restarts with POSITIVE staleness proof from the machine's
# own lane heartbeat file; a 20-min restart stamp prevents killing a fresh round
# that has not written its heartbeat yet; off-skip freeze-face protection unchanged.
# v1.8 (2026-10-17 force-repos concat fix, bm-b live-fire x2): with a single-element
# poke_repos (all nodes use ['.']) the pipeline `@($node.poke_repos) | ForEach-Object`
# UNROLLED the array into a scalar string, so `$pullSet += $fs` did string CONCATENATION
# ('.' + 'quant/bigmoney' = '.quant/bigmoney' -> ':no-repo' on both the v1.8 listener at
# 21:52 and the v1.9.3 listener at 08:33) - the force-repos COLD-tier pull channel was
# broken fleet-wide since v1.5. Array-wrap @(...) keeps $pullSet an array. Normal '.'
# HOT pulls were unaffected (a scalar still iterates fine), which is why this hid until
# first live use.
# v1.6 (2026-10-16 fleet-linkup order): lock now stores its pid - a FRESH lock
# owned by a DEAD process (crashed worker) no longer blocks pokes for 10min;
# the stale-but-fresh lock is reclaimed immediately and the takeover is logged
# (lock-reclaim). Live-owner semantics unchanged. Backward compatible: parses
# legacy "pid=N" text locks too.
# v1.7 (2026-10-16 bm-b blood-swap live-fire): the listener freshness gate now
# VERIFIES each spawn tier by watching the local /health version actually flip
# before trusting it; silent-start failures fall through to the next tier (bm-b
# 20:18 evidence: gate fired, tier-2 register reported success, listener stayed
# v1.8 - Interactive-principal tasks never start without an interactive logon
# session). Gate trigger widened: also fires when the LIVE /health version
# differs from the on-disk version (covers a dead same-version listener and a
# stale-version listener holding the port while state.json lies either way).
# v1.5 (2026-10-16 CEO check "is fleet sync fastest/most effective" - bm-c stuck on
# v1.7 root cure): listener freshness gate - if the on-disk fleet-link.ps1 version
# is newer than the RUNNING listener (state.json), start a fresh instance; the
# existing port-contention self-upgrade replaces the old one. This is the remote
# upgrade channel for nodes whose FluxGroup-FleetLink keepalive task is not
# cycling (bm-c: task trigger dead, listener frozen on v1.7, large-body /sync
# rejected forever). If the task is MISSING, re-registers it via
# register-fleet-link.ps1 (idempotent) so 5-min supervision is healed too.
# v1.1 = O-20261009-1750 "very fast sync" upgrade).
# Spawned hidden by the listener's /poke handler so the accept loop NEVER blocks on
# git pulls (v1.0 inline pull blocked /health for the whole pull duration - the
# "timeout while busy" root cause). Lock-serialized: one worker at a time per node;
# a fresh lock means a pull is already in flight (it fetches the newest anyway).
#   - lock file   : ~\.codely-cli\fleet-link\worker.lock  (stale >10min = crashed worker, reclaimed)
#   - stamp file  : ~\.codely-cli\fleet-link\last-pull-<node>.json (ts + repo HEADs -> /status)
# Law anchors unchanged: signals only, data stays in git; allowlisted tasks only.
param(
  [string]$Root = "C:\Users\sjs20\Desktop\FluxGroup",
  [string]$NodeId = "",
  [string]$Reason = "poke",
  [string]$TasksJson = "[]",
  [string]$PullReposJson = "[]",
  [string]$TasksB64 = "",
  [string]$ReposB64 = ""
)
# v1.3 (C-20261009-04): base64 channel from listener v1.4 - the old quoted
# -TasksJson argument embedded JSON double-quotes inside a quoted -ArgumentList
# string, which broke param binding (workers always received []). Legacy params
# still honored for older listeners.
if ($TasksB64 -ne "") { try { $TasksJson = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($TasksB64)) } catch { } }
if ($ReposB64 -ne "") { try { $PullReposJson = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($ReposB64)) } catch { } }
$ErrorActionPreference = 'Continue'
$Dir = Join-Path $env:USERPROFILE '.codely-cli\fleet-link'
if (-not (Test-Path $Dir)) { New-Item -ItemType Directory -Path $Dir | Out-Null }
$LogF = Join-Path $Dir 'log.jsonl'
$LockF = Join-Path $Dir 'worker.lock'
$StampF = Join-Path $Dir ('last-pull-' + $NodeId + '.json')

function WK-Log([string]$evt, [string]$detail) {
  try {
    $o = [ordered]@{ ts = (Get-Date -Format s); event = $evt; detail = $detail }
    ($o | ConvertTo-Json -Compress) | Add-Content -LiteralPath $LogF -Encoding UTF8
  } catch { }
}

# ---- v1.7: live listener version probe + version-flip watcher (gate ground truth) ----
function WK-ListenerPort() {
  $p = 8790
  try { if ($cfg -and ($cfg.PSObject.Properties.Name -contains 'port')) { $p = [int]$cfg.port } } catch { }
  return $p
}
function WK-LiveListenerVers() {
  try {
    $h = Invoke-RestMethod -Uri ('http://127.0.0.1:' + (WK-ListenerPort) + '/health') -TimeoutSec 3
    return [string]$h.version
  } catch { return '' }
}
function WK-WaitListenerVers([string]$want, [int]$secs) {
  $deadline = (Get-Date).AddSeconds($secs)
  while ((Get-Date) -lt $deadline) {
    if ((WK-LiveListenerVers) -eq $want) { return $true }
    Start-Sleep -Milliseconds 700
  }
  return $false
}

# ---- single-flight lock (v1.6: pid-verified - a fresh lock owned by a dead
# process is reclaimed immediately instead of blocking pokes for 10min) ----
if (Test-Path $LockF) {
  try {
    $age = ((Get-Date) - (Get-Item $LockF).LastWriteTime).TotalMinutes
    $olk = Get-Content -Raw -LiteralPath $LockF -ErrorAction SilentlyContinue
    $opid = 0
    try { $opid = [int]($olk | ConvertFrom-Json).pid } catch { if ($olk -match 'pid=(\d+)') { $opid = [int]$Matches[1] } }
    $alive = $false
    if ($opid -gt 0) { $alive = [bool](Get-Process -Id $opid -ErrorAction SilentlyContinue) }
    if ($alive -and $age -lt 10) { WK-Log 'worker-skip' ('lock fresh ' + [math]::Round($age, 1) + 'm pid=' + $opid); exit 0 }
    WK-Log 'lock-reclaim' ('age=' + [math]::Round($age, 1) + 'm pid=' + $opid + ' alive=' + $alive)
    Remove-Item $LockF -Force -ErrorAction SilentlyContinue
  } catch { }
}
try { [IO.File]::WriteAllText($LockF, ('{"pid":' + $PID + ',"ts":"' + (Get-Date -Format s) + '","reason":"' + $Reason + '"}'), (New-Object System.Text.UTF8Encoding($false))) } catch { }

# ---- roster ----
$node = $null
try {
  $cfg = Get-Content -Raw -Encoding UTF8 (Join-Path $Root 'Tools\fleet-nodes.json') | ConvertFrom-Json
  foreach ($n in @($cfg.nodes)) {
    if ($NodeId -ne '' -and [string]$n.id -eq $NodeId) { $node = $n; break }
    if ($NodeId -eq '' -and [string]$n.host -ne '' -and ([string]$n.host -ieq $env:COMPUTERNAME)) { $node = $n; $NodeId = [string]$n.id; break }
  }
} catch { }
if ($NodeId -eq '') { $NodeId = $env:COMPUTERNAME }

# ---- pull policy (O-20261009-1755 sync tiers): HOT = node.poke_repos + explicitly
# forced repos (request must be allowlisted against node.repos). WARM repos are
# pulled by their OWN loop tasks on round cadence - NOT duplicated here. The
# stamp below still reports ALL registered repo HEADs (rev-parse is cheap). ----
$git = 'git'
$heads = @()
$force = @()
try { $force = @((($PullReposJson) | ConvertFrom-Json) | ForEach-Object { [string]$_ }) } catch { }
$force = @($force | Where-Object { $_ -and $_.Trim() -ne '' })
$pullSet = @()
if ($node -and ($node.PSObject.Properties.Name -contains 'poke_repos')) { $pullSet = @(@($node.poke_repos) | ForEach-Object { [string]$_ }) }
if ($pullSet.Count -eq 0) { $pullSet = @('.') }
foreach ($f in $force) {
  $fs = [string]$f
  $registered = ($node -and ($node.PSObject.Properties.Name -contains 'repos') -and (@($node.repos) -contains $fs))
  if ($registered -and ($pullSet -notcontains $fs)) { $pullSet += $fs }
  elseif (-not $registered) { $heads += ($fs + ':force-deny') }
}
foreach ($rel in $pullSet) {
    $p = Join-Path $Root ([string]$rel)
    if (-not (Test-Path (Join-Path $p '.git'))) { $heads += ([string]$rel + ':no-repo'); continue }
    $lines = @()
    try { $lines = @(& $git -C $p pull --ff-only 2>&1 | ForEach-Object { [string]$_ }) } catch { $lines = @([string]$_.Exception.Message) }
    $s = $lines -join ' | '
    if ($s -match 'up to date') { $heads += ([string]$rel + ':current') }
    elseif ($s -match 'Fast-forward') { $heads += ([string]$rel + ':updated') }
    elseif ($s -match 'would be overwritten by merge') {
      # v1.2 (O-20261009-1755): dirty in-flight files (usually session CODELY.md
      # memory) must NEVER block the command plane and NEVER be lost.
      # Directed autostash: stash ONLY the blocking paths -> ff-merge -> pop.
      # Pop conflict (upstream touched same file): keep the LOCAL session
      # version (theirs in stash-pop = stashed local edits); upstream version
      # stays in history; owning window commits its version at round end.
      $block = @()
      $inBlock = $false
      foreach ($ln in $lines) {
        if ($ln -match 'would be overwritten by merge') { $inBlock = $true; continue }
        if ($inBlock) {
          if ($ln -match '^\s+(\S+)\s*$') { $block += $Matches[1]; continue }
          $inBlock = $false
        }
      }
      $block = @($block | Where-Object { $_ -and (Test-Path (Join-Path $p $_)) } | Select-Object -First 12)
      if ($block.Count -eq 0) {
        $heads += ([string]$rel + ':fail')
        WK-Log 'pull-fail' ([string]$rel + ' ' + $s.Substring(0, [Math]::Min(200, $s.Length)))
        continue
      }
      $tag = 'fleet-autostash-' + (Get-Date -Format 'yyyyMMddHHmmss')
      $stashArgs = @('-C', $p, 'stash', 'push', '-m', $tag, '--') + $block
      $null = & $git @stashArgs 2>&1
      $mlines = @(& $git -C $p merge --ff-only origin/main 2>&1 | ForEach-Object { [string]$_ })
      $m = $mlines -join ' | '
      if ($m -match 'Fast-forward|up to date|Already up to date') {
        $plines = @(& $git -C $p stash pop 2>&1 | ForEach-Object { [string]$_ })
        $pop = $plines -join ' | '
        if ($pop -match 'CONFLICT') {
          foreach ($bf in $block) { $null = & $git -C $p checkout --theirs -- $bf 2>&1 }
          $unstageArgs = @('-C', $p, 'restore', '--staged', '--') + $block
          $null = & $git @unstageArgs 2>&1
          $null = & $git -C $p stash drop 2>&1
          $heads += ([string]$rel + ':updated-kept-local')
          WK-Log 'autostash-conflict-kept-local' ([string]$rel + ' ' + ($block -join ','))
        } else { $heads += ([string]$rel + ':updated-restored-inflight') }
      } else {
        # merge still failed - restore stashed edits immediately (never hold them)
        $null = & $git -C $p stash pop 2>&1
        $heads += ([string]$rel + ':fail')
        WK-Log 'pull-fail' ([string]$rel + ' ' + $s.Substring(0, [Math]::Min(200, $s.Length)))
      }
    }
    else {
      $heads += ([string]$rel + ':fail')
      if ($s.Length -gt 200) { $s = $s.Substring(0, 200) }
      WK-Log 'pull-fail' ([string]$rel + ' ' + $s)
    }
}

# ---- global memory union-sync RETIRED (v1.9, 2026-10-18, memory-curator seat, CEO
# order "control memory bloat"): the union/replace-down loop fought the per-machine
# L0 budget gate - the gate trimmed 375KB->117KB every 4h and the next poke replaced
# the local file with the 375KB canonical verbatim (gate-log.txt 10-16..10-17
# evidence; 66 fleet-memory git commits). Superseded by memory.md S8 (cross-machine
# value travels via git canon + L1) and S10 (L0 = per-machine injection face with a
# hard budget). The canonical is frozen under cph4/fleet/memory/archive/;
# fleet-memory-sync.ps1 is now a no-op stub. Keep this tombstone for history. ----

# ---- v1.5 listener freshness gate: upgrade/revive the local listener when a
# newer fleet-link.ps1 shipped via git (runs AFTER pulls so the newest code is on
# disk; zero side effects when versions already match). Try the scheduled task
# first (durable), then idempotent re-registration (heals a missing task), then a
# raw hidden instance as last resort. v1.7: every tier is VERIFIED against the
# live /health version; failures fall through to the next tier. ----
try {
  $flScript = Join-Path $Root 'Tools\fleet-link.ps1'
  $stateF2 = Join-Path $Dir 'state.json'
  if (Test-Path $flScript) {
    $diskVers = ''
    $m = [regex]::Match([IO.File]::ReadAllText($flScript), "\`$Vers\s*=\s*'([0-9.]+)'")
    if ($m.Success) { $diskVers = $m.Groups[1].Value }
    $runVers = ''
    if (Test-Path $stateF2) { try { $runVers = [string]((Get-Content -Raw $stateF2 | ConvertFrom-Json).version) } catch { } }
    $liveVers = WK-LiveListenerVers
    $need = $false
    if ($diskVers -ne '') {
      if ($runVers -ne '' -and ([version]$diskVers -gt [version]$runVers)) { $need = $true }
      elseif ($liveVers -ne $diskVers) { $need = $true }
    }
    if ($need) {
      # v1.7: verify each tier actually flipped the listener; fall through on
      # failure. Misfires are harmless - a same-version extra instance exits
      # 'no bind' via port contention, and a takeover replaces the old listener.
      $tiers = @()
      $ok = $false
      try { Start-ScheduledTask -TaskName 'FluxGroup-FleetLink' -ErrorAction Stop; $tiers += 'task:start'; $ok = WK-WaitListenerVers $diskVers 15 } catch { $tiers += 'task:fail' }
      if (-not $ok) {
        try {
          $reg = Join-Path $Root 'Tools\register-fleet-link.ps1'
          if (Test-Path $reg) { & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $reg -Root $Root 2>&1 | Out-Null; $tiers += 'reg:run'; $ok = WK-WaitListenerVers $diskVers 15 }
        } catch { $tiers += 'reg:fail' }
      }
      if (-not $ok) {
        $argz = '-NoProfile -ExecutionPolicy Bypass -File "' + $flScript + '" -Root "' + $Root + '" -NodeId ' + $NodeId
        Start-Process -FilePath 'powershell.exe' -ArgumentList $argz -WindowStyle Hidden | Out-Null
        $tiers += 'raw:spawn'
        $ok = WK-WaitListenerVers $diskVers 20
      }
      WK-Log 'listener-refresh' ('running=' + $runVers + ' live=' + $liveVers + ' disk=' + $diskVers + ' tiers=' + ($tiers -join ' ') + ' upgraded=' + $ok)
    }
  }
} catch { WK-Log 'listener-refresh-fail' ([string]$_.Exception.Message) }

# ---- wake allowlisted tasks ----
$woke = @()
$reqTasks = @()
try { $reqTasks = @((($TasksJson) | ConvertFrom-Json) | ForEach-Object { [string]$_ }) } catch { }
$reqTasks = @($reqTasks | Where-Object { $_ -and $_.Trim() -ne '' })
$allow = @()
if ($node -and ($node.PSObject.Properties.Name -contains 'wake_tasks')) { $allow = @($node.wake_tasks) | ForEach-Object { [string]$_ } }
foreach ($t in $reqTasks) {
  $ts = [string]$t
  if ($allow -notcontains $ts) { $woke += ($ts + ':deny'); continue }
  $task = Get-ScheduledTask -TaskName $ts -ErrorAction SilentlyContinue
  if (-not $task) { $woke += ($ts + ':no-task'); continue }
  if ($task.State.ToString() -eq 'Running') {
    # v1.10 hung-round revival (see header). Only the two round-runners, only with
    # positive heartbeat-staleness evidence, only once per 20 min per task.
    $hungRestarted = $false
    if (($ts -eq 'Bigmoney-IterationLoop') -or ($ts -eq 'MiniGameEngineTick')) {
      $hrLock = Join-Path $Dir ('hung-restart-' + $ts + '.stamp')
      $recentRestart = $false
      if (Test-Path $hrLock) { try { $recentRestart = (((Get-Date) - (Get-Item $hrLock).LastWriteTime).TotalMinutes -lt 20) } catch { } }
      $hbAgeMin = -1
      if (-not $recentRestart) {
        $hbFile = $null; $hbField = ''
        if ($ts -eq 'Bigmoney-IterationLoop') {
          $hbFile = Join-Path $Root ('quant/bigmoney/fleet/machines/' + $NodeId + '.json')
          $hbField = 'last_seen'
        } else {
          $hbFile = Join-Path $Root ('gaming/MiniGame/Design/configs/GLOBAL/fleet/' + ($NodeId -replace '^bm-', '') + '.json')
          $hbField = 'ts'
        }
        try {
          if ($NodeId -and (Test-Path $hbFile)) {
            $hbRaw = Get-Content -Raw -LiteralPath $hbFile
            $m1 = [regex]::Match($hbRaw, ('"' + $hbField + '"\s*:\s*"([^"]+)"'))
            if (-not $m1.Success -and $ts -eq 'Bigmoney-IterationLoop') { $m1 = [regex]::Match($hbRaw, '"clock_read"\s*:\s*"([^"]+)"') }
            if ($m1.Success) {
              $hbDto = [DateTimeOffset]::Parse($m1.Groups[1].Value, [Globalization.CultureInfo]::InvariantCulture)
              $hbAgeMin = [math]::Round(((Get-Date) - $hbDto.LocalDateTime).TotalMinutes, 0)
            }
          }
        } catch { $hbAgeMin = -1 }
      }
      if ((-not $recentRestart) -and ($hbAgeMin -gt 120)) {
        try {
          try { [IO.File]::WriteAllText($hrLock, (Get-Date -Format s)) } catch { }
          Stop-ScheduledTask -TaskName $ts -ErrorAction Stop
          Start-Sleep -Seconds 6
          try { Start-ScheduledTask -TaskName $ts } catch { }
          $woke += ($ts + ':HUNG-RESTART-hb' + $hbAgeMin + 'm')
          WK-Log 'hung-restart' ($ts + ' hb_age_min=' + $hbAgeMin + ' node=' + $NodeId + ' reason=' + $Reason)
          $hungRestarted = $true
        } catch {
          $woke += ($ts + ':busy-skip-stopfail')
          WK-Log 'hung-stop-fail' ($ts + ' ' + [string]$_.Exception.Message)
        }
      }
    }
    if (-not $hungRestarted) { $woke += ($ts + ':busy-skip') }
    continue
  }
  # v1.3 (C-20261009-04): CEO freeze faces (design-state Disabled tasks) must not
  # be re-armed by a remote wake - same off-skip protection as the local sentinel.
  if ($task.State.ToString() -eq 'Disabled') { $woke += ($ts + ':off-skip'); continue }
  try { Start-ScheduledTask -TaskName $ts; $woke += ($ts + ':WAKE') } catch { $woke += ($ts + ':wake-fail') }
}

# ---- stamp (repo HEADs for /status + dispatcher verification) ----
$repoHeads = @{}
try {
  if ($node -and ($node.PSObject.Properties.Name -contains 'repos')) {
    foreach ($rel in @($node.repos)) {
      $p = Join-Path $Root ([string]$rel)
      if (Test-Path (Join-Path $p '.git')) {
        $h = ''
        try { $h = [string](& $git -C $p rev-parse HEAD) } catch { }
        if ($h) { $repoHeads[[string]$rel] = $h.Trim() }
      }
    }
  }
} catch { }
try {
  # v1.4 stamp: origin_main = fetched canonical head (local main may run AHEAD via
  # memory-union commits - node still synced; dispatcher verify reads this field).
  $om = ''
  try { $om = [string](& $git -C $Root rev-parse origin/main) } catch { }
  $st = [ordered]@{ node = $NodeId; ts = (Get-Date -Format s); reason = $Reason
                    pulls = @($heads); wakes = @($woke); repo_heads = $repoHeads
                    origin_main = $om }
  [IO.File]::WriteAllText($StampF, ($st | ConvertTo-Json -Depth 4 -Compress), (New-Object System.Text.UTF8Encoding($false)))
} catch { }
WK-Log 'worker-done' ('reason=' + $Reason + ' pull=' + ($heads -join ' ') + ' wake=' + ($woke -join ' '))
try { Remove-Item $LockF -Force -ErrorAction SilentlyContinue } catch { }
exit 0
