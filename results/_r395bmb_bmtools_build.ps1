# r395 bm-b T-110 slice: .bm-tools venv scan-stack build (O-1750 needs-based, T-110 bm-b slice)
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path C:\Users\Administrator\.bm-tools | Out-Null
if (-not (Test-Path 'C:\Users\Administrator\.bm-tools\venv\Scripts\python.exe')) {
  python -m venv C:\Users\Administrator\.bm-tools\venv
}
$py = 'C:\Users\Administrator\.bm-tools\venv\Scripts\python.exe'
& $py -m pip install --quiet --upgrade pip
Write-Output "PIP_UPGRADE_DONE rc=$LASTEXITCODE"
& $py -m pip install backtrader backtesting vectorbt rqalpha akshare baostock tushare easyquotation quantstats stockstats alphalens-reloaded duckdb
Write-Output "PIP_INSTALL_DONE rc=$LASTEXITCODE"
foreach ($p in @('backtrader','backtesting','vectorbt','rqalpha','akshare','baostock','tushare','easyquotation','quantstats','stockstats','alphalens_reloaded','duckdb')) {
  & $py -c "import $p; print('IMPORT_OK $p')"
}
& $py -c "import backtrader, backtesting, vectorbt, rqalpha, akshare, baostock, tushare, easyquotation, quantstats, stockstats, alphalens_reloaded, duckdb; print('IMPORT_SMOKE_ALL12_PASS')"
Write-Output 'BMTOOLS_VENV_DONE'
