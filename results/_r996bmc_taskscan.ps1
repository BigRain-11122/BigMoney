$raw = & 'K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\Invoke-SilentExe.ps1' -Exe schtasks -ArgString '/query /fo csv /nh'
$hits = $raw | Select-String -Pattern 'ollama|Ollama|KeepWarm|Warm'
foreach ($h in $hits) { Write-Output ($h.Line.Substring(0, [Math]::Min(130, $h.Line.Length))) }
