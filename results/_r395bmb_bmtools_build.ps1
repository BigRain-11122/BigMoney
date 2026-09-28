# r395 bm-b T-110 slice attempt-2: split install (rqalpha resolver backtrack fix, ticket-law honest)
# attempt-1: joint resolve backtracked rqalpha 6.4.0(no py311 wheel)->6.1.1->5.6.5 sdist build error rc=1
$ErrorActionPreference = 'Continue'
$py = 'C:\Users\Administrator\.bm-tools\venv\Scripts\python.exe'
$log = 'C:\Users\Administrator\.bm-tools\install-log.txt'
"=== bm-b .bm-tools install log (attempt-2 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) ===" | Out-File $log -Append ascii
& $py -m pip install backtrader backtesting vectorbt akshare baostock tushare easyquotation quantstats stockstats alphalens-reloaded duckdb 2>&1 | Out-File $log -Append ascii
"PIP_INSTALL_MAIN11 rc=$LASTEXITCODE" | Out-File $log -Append ascii
Write-Output "PIP_INSTALL_MAIN11 rc=$LASTEXITCODE"
& $py -m pip install "rqalpha==6.1.1" 2>&1 | Out-File $log -Append ascii
"PIP_INSTALL_RQALPHA rc=$LASTEXITCODE" | Out-File $log -Append ascii
Write-Output "PIP_INSTALL_RQALPHA rc=$LASTEXITCODE"
foreach ($p in @('backtrader','backtesting','vectorbt','akshare','baostock','tushare','easyquotation','quantstats','stockstats','alphalens_reloaded','duckdb','rqalpha')) {
  & $py -c "import $p; print('IMPORT_OK $p')" 2>&1 | Out-File $log -Append ascii
}
& $py -c "import backtrader, backtesting, vectorbt, akshare, baostock, tushare, easyquotation, quantstats, stockstats, alphalens_reloaded, duckdb; print('IMPORT_SMOKE_MAIN11_PASS')"
Write-Output 'BMTOOLS_VENV_ATTEMPT2_DONE'
