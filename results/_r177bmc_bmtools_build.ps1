# r177 bm-c T-110 slice: .bm-tools venv collection stack build (O-1750 needs-based)
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path C:\Users\Dasheng\.bm-tools | Out-Null
python -m venv C:\Users\Dasheng\.bm-tools\venv
$py = 'C:\Users\Dasheng\.bm-tools\venv\Scripts\python.exe'
& $py -m pip install --quiet --upgrade pip
Write-Output "PIP_UPGRADE_DONE rc=$LASTEXITCODE"
& $py -m pip install akshare baostock tushare easyquotation quantstats
Write-Output "PIP_INSTALL_DONE rc=$LASTEXITCODE"
foreach ($p in @('akshare','baostock','tushare','easyquotation','quantstats')) {
  & $py -c "import $p; print('IMPORT_OK $p ' + $p.__version__)"
}
& $py -c "import akshare,baostock,tushare,easyquotation,quantstats; print('IMPORT_SMOKE_ALL5_PASS')"
Write-Output 'BMTOOLS_VENV_DONE'
