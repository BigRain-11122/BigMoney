$ErrorActionPreference = 'Continue'
python -c "
import csv
for code in ['sh510300','sh510050','sh510500','sh512100','sh588000']:
    with open('data/daily/%s.csv' % code) as f:
        rows = list(csv.reader(f))
    print(code, 'tail:', rows[-1][0])
"
Write-Output '--- chain B: paper lanes (new bar 2026-10-09 present) ---'
$env:BIGMONEY_REGIME_GUARD = 'enforce'
$legs = @(
  @('live_paper',               'python -m live.paper'),
  @('t35_open_fill_verify',     'python scripts\t35_open_fill_verify.py'),
  @('t24_prospect_paper',       'python scripts\t24_prospect_paper.py run'),
  @('t24_prospect_promotion',   'python scripts\t24_prospect_promotion.py run'),
  @('aggressive_lab',           'python scripts\aggressive_lab.py paper'),
  @('alloc_paper',              'python scripts\alloc_paper.py run'),
  @('grid_paper',               'python scripts\grid_paper.py run'),
  @('system_v1_paper',          'python scripts\system_v1_paper.py run'),
  @('t35_paper_export',         'python scripts\t35_paper_export.py run'),
  @('daily_scorecard',          'python scripts\daily_scorecard.py'),
  @('daily_report',             'python scripts\daily_report.py run'),
  @('ceo_live_usage',           'python scripts\ceo_live_usage.py'),
  @('build_status',             'python -m monitor.build_status'),
  @('token_meter',              'python scripts\token_meter.py')
)
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  $out = cmd /c "$cmd 2>&1"
  $rc = $LASTEXITCODE
  $last = ($out | Select-Object -Last 1)
  Write-Output ("LEG {0} rc={1} last={2}" -f $name, $rc, ($last -replace "`r|`n",''))
  if ($rc -ne 0) { Write-Output ("  DETAIL: {0}" -f (($out | Select-Object -First 6) -join ' | ')) }
}
