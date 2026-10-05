# r540 bm-c S7 task-family probe (schtasks CSV canonical, r517 law; wrapper single-string split, r535 law)
$wrap = "K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\Invoke-SilentExe.ps1"
$out = & $wrap -Exe "schtasks.exe" -ArgString "/query /fo csv" -Cwd "K:\Fluxgroup\FluxGroup\quant\bigmoney"
$rc = $LASTEXITCODE
if ($rc -ne 0) { Write-Output "SCHTASKS_CSV_FAIL rc=$rc"; exit 2 }
$lines = $out -split "`n"
$names = foreach ($l in $lines) {
  $cols = $l -split '","'
  if ($cols.Count -ge 1) {
    $n = $cols[0].Trim('"', '\', ' ', "`r")
    if ($n -match 'Bigmoney') { $n }
  }
}
Write-Output ("FAMILY_COUNT=" + @($names).Count)
$names | ForEach-Object { Write-Output ("FAMILY: " + $_) }
