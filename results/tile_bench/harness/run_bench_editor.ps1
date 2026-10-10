# CPH4 low-tier 2D rendering benchmark driver - editor-batchmode route (r845)
# Row: fleet/backlog.md #9 "低配机 2D 渲染性能基准（bm-b 3070 档·确定 tile 大城帧预算）"
# Claim: bm-b r844 2026-10-10T21:59:03+08:00
# Route: r844 diagnosed the hidden standalone player window as frozen (never enters
# the player loop; visible window conflicts with the zero-popup law), so the r845
# route is editor -batchmode + TileBenchEditorRun manual render loop (RT 1600x900,
# per-tick cam.Render + 1x1 ReadPixels GPU sync). No player build needed.
# Idempotent per run (skips completed jsons) so cross-round reruns resume cleanly.
# Zero-window discipline: batchmode editor has no UI; Start-Process -WindowStyle
# Hidden is belt-and-suspenders (same as the r844 build step).

$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$proj = Join-Path $root 'TileBenchProj'
$ed   = 'C:\Program Files\Tuanjie\Hub\Editor\2022.3.62t15\Editor\Tuanjie.exe'
$res  = Join-Path $root 'results'
$log  = Join-Path $root 'bench_run_editor.log'
$stateFile = Join-Path $root 'bench_state_editor.json'

New-Item $res -ItemType Directory -Force | Out-Null
function L($m) { Add-Content $log ("{0} {1}" -f (Get-Date -Format o), $m) }
function State($p) { @{ phase = $p; ts = (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') } | ConvertTo-Json | Set-Content $stateFile }

L 'driver start (editor-batchmode route r845)'
State 'inject'
New-Item (Join-Path $proj 'Assets\Editor') -ItemType Directory -Force | Out-Null
Copy-Item (Join-Path $root 'src\TileBenchEditorRun.cs') (Join-Path $proj 'Assets\Editor\TileBenchEditorRun.cs') -Force
L 'editor script injected'

# matrix identical to player route: size sweep / layer sweep / ortho sweep / repeatability
$matrix = @(
    @{ n = 's256_L1_o17';    size = 256;  layers = 1; ortho = 17   },
    @{ n = 's512_L1_o17';    size = 512;  layers = 1; ortho = 17   },
    @{ n = 's1024_L1_o17';   size = 1024; layers = 1; ortho = 17   },
    @{ n = 's1024_L3_o17';   size = 1024; layers = 3; ortho = 17   },
    @{ n = 's1024_L1_o34';   size = 1024; layers = 1; ortho = 34   },
    @{ n = 's1024_L3_o34';   size = 1024; layers = 3; ortho = 34   },
    @{ n = 's1024_L3_o8_5';  size = 1024; layers = 3; ortho = 8.5  },
    @{ n = 's1024_L3_o17_r2'; size = 1024; layers = 3; ortho = 17  }
)
$i = 0
foreach ($c in $matrix) {
    $i++
    $out = Join-Path $res ("run{0:d2}_{1}.json" -f $i, $c.n)
    if (Test-Path $out) { L ("skip existing " + $c.n); continue }
    State ("run " + $c.n)
    $runLog = Join-Path $res ("run{0:d2}_{1}.log" -f $i, $c.n)
    $p = Start-Process -FilePath $ed -ArgumentList '-batchmode','-projectPath',"$proj",
        '-executeMethod','TileBenchEditorRun.Run','-mapSize', $c.size, '-layers', $c.layers,
        '-ortho', $c.ortho, '-durationSec', 10, '-outFile', $out, '-logFile', $runLog -PassThru -WindowStyle Hidden
    if (-not $p.WaitForExit(300000)) {
        $p.Kill(); L ("run TIMEOUT " + $c.n)
        if ($i -eq 1) { L 'CANARY-FAIL: first run timed out, aborting matrix'; State 'canary-timeout'; exit 5 }
        continue
    }
    $ok = Test-Path $out
    L ("run " + $c.n + " rc=" + $p.ExitCode + " json=" + $ok)
    if ($i -eq 1 -and -not $ok) {
        L 'CANARY-FAIL: first run produced no json, aborting matrix'
        if (Test-Path $runLog) { Get-Content $runLog | Select-Object -Last 25 | ForEach-Object { L ("  | " + $_) } }
        State 'canary-fail'; exit 5
    }
}

State 'report'
python (Join-Path $root 'report.py')
L ("report rc=" + $LASTEXITCODE)
State 'done'
L 'driver done'
