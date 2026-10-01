# r328 bm-c surgical push 2: W17 heal (mirror restore vs r517 stale-sweep) + finalize landing.
# Payload = 5 paths from the working tree onto origin/main temp-index (r512 law).
# Mirrors = my versions (17 rows, W19 rows REMOVED per bm-a r529 law-side adjudication
# + MSG-184x commit-time ruling -- mirrors realigned to the adjudicated law, single-source).
$ErrorActionPreference = "Stop"
$g = "K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1"
Set-Location "K:\Fluxgroup\FluxGroup\quant\bigmoney"

& $g -GitArgs "fetch origin" | Out-Null
$parent = (& $g -GitArgs "rev-parse origin/main").Trim()
"BASE=$parent"

$payload = @(
  "scripts/perpetual_faces.py",
  "scripts/perpetual_faces_n1.py",
  "research/PERPETUAL_FACES.md",
  "research/PERPETUAL_N1_W17_PREREG.md",
  "results/perpetual_faces/n1_w17_results.json"
)

$idx = Join-Path $env:TEMP "r328bmc_heal_idx"
if (Test-Path $idx) { Remove-Item $idx -Force }
$env:GIT_INDEX_FILE = $idx
& $g -GitArgs "read-tree origin/main" | Out-Null
foreach ($p in $payload) { & $g -GitArgs ("add " + $p) }
$tree = (& $g -GitArgs "write-tree").Trim()
"TREE=$tree"
Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue

# post-tree assertions (r516 payload law): W17 rows present, W19 mirror rows GONE,
# finalize product present, law row intact (bm-a adjudicated version).
$all_pf = (& $g -GitArgs ("show " + $tree + ":scripts/perpetual_faces.py")) -join "`n"
$bands17 = ([regex]::Matches($all_pf, "17: \{`"a`": \(76_001, 78_000\)")).Count
$bands19 = ([regex]::Matches($all_pf, "19: \{`"a`": \(76_001, 78_000\)")).Count
"MIRROR_BANDS_17=$bands17 MIRROR_BANDS_19=$bands19"
if ($bands17 -ne 1 -or $bands19 -ne 0) { "ASSERT FAIL: mirror band rows"; exit 1 }
$all_cfg = (& $g -GitArgs ("show " + $tree + ":scripts/perpetual_faces_n1.py")) -join "`n"
$cfg17 = ([regex]::Matches($all_cfg, "17: \{`"batch`": `"PERPETUAL-N1-W17`"")).Count
$cfg19 = ([regex]::Matches($all_cfg, "19: \{`"batch`": `"PERPETUAL-N1-W19`"")).Count
"WAVE_CONFIGS_17=$cfg17 WAVE_CONFIGS_19=$cfg19"
if ($cfg17 -ne 1 -or $cfg19 -ne 0) { "ASSERT FAIL: wave configs"; exit 1 }
& $g -GitArgs ("cat-file -e " + $tree + ":results/perpetual_faces/n1_w17_results.json") | Out-Null
"FINALIZE_PRODUCT_PRESENT_RC=$LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { "ASSERT FAIL: finalize product missing from tree"; exit 1 }

$msg = "round 328 heal+finalize surgical: W17 mirror rows restored (r517 stale-sweep heal, r326 law; mirrors realigned to bm-a r529 law-side adjudication + MSG-184x commit-time ruling -- W17 stands [freeze 7e03101fb origin 18:23 EARLIER, 12/12 engine-burned, finalize K=35,320 mu -0.09192 sigma 0.24452 se_mu 0.001301, ledger 399,748+2,200=401,948, S5 4/4 PASS, S7/S8 backfilled; N3-R1 x W17 DISJOINT machine-checked per r529 ruling leg]; W19 registration rows removed from mirrors [bm-b yield per MSG-184x: dup bands A 76_001..78_000/B 38_100..38_299, shards discard-at-yield bm-b side]; selftests n1+pf 8/8+engine 36/36 green on healed set) [via bm-c]"
$new = (& $g -GitArgs ("commit-tree " + $tree + " -p " + $parent + " -m `"" + $msg + "`"")).Trim()
"NEW_COMMIT=$new"

& $g -GitArgs ("push origin " + $new + ":refs/heads/main")
"PUSH_EXIT=$LASTEXITCODE"
if ($LASTEXITCODE -ne 0) {
    "push rejected -- per r512 law: fetch, rebuild, new parent, cheap retry"
    exit 1
}
& $g -GitArgs "fetch origin" | Out-Null
"ORIGIN_NOW=" + (& $g -GitArgs "rev-parse origin/main").Trim()
