param(
  [Parameter(Mandatory=$true)][string]$Exe,
  [Parameter(Mandatory=$true)][string]$ArgString,
  [string]$Cwd = "",
  [switch]$StdoutOnly,
  [switch]$IncludeStderr
)
# Invoke-SilentExe.ps1 -- run a native console exe with ZERO desktop flash.
# Law: CEO silence orders (automation zero-popup O-67fbec7 + 2026-10-01 11:2x
# desktop-flash reprimand) + U060 zero-window rule. Native console exes
# (schtasks/git/python) spawned from a WINDOWLESS session host allocate one
# visible desktop console per launch; scheduled-task contexts (hidden
# console via InvisibleRunner.vbs) never flash. This helper makes the call
# safe in ANY host context (defense-in-depth for interactive GM sessions).
# Mechanism: ProcessStartInfo.CreateNoWindow=true + stream redirection --
# same proven pattern as the GM-session silent-git.ps1 wrapper (2026-10-01).
# Output contract (D-20261005-08 default flip, r723):
#   DEFAULT      stdout always; stderr appended ONLY when rc != 0
#                (rc=0 consumers = porcelain/counts/hashes never see
#                CRLF-warning pollution -- four-incident family
#                r511/r513/r706/r534; rc!=0 keeps failure diagnostics
#                that the old contract silently dropped).
#   -StdoutOnly  pure stdout at ANY rc, stderr silently dropped
#                (existence checks: empty-output == not-found, R49 canon).
#   -IncludeStderr  stderr appended at any rc (legacy merge face; use
#                only when the caller explicitly wants merged text).
# Exit code: child's exit code propagates ($LASTEXITCODE after the & call).
# Pure ASCII, path-agnostic, repo-distributed (single source for all
# session-invoked tools; r303 single-source law).
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $Exe
$psi.Arguments = $ArgString
if ($Cwd -ne "") { $psi.WorkingDirectory = $Cwd } else { $psi.WorkingDirectory = (Get-Location).Path }
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$p = [System.Diagnostics.Process]::Start($psi)
$outTask = $p.StandardOutput.ReadToEndAsync()
$err = $p.StandardError.ReadToEnd()
$out = $outTask.Result
$p.WaitForExit()
if ($out) { Write-Output $out.TrimEnd() }
if ($StdoutOnly) { exit $p.ExitCode }
if ($IncludeStderr -and $err) { Write-Output $err.TrimEnd() }
elseif (-not $IncludeStderr -and $p.ExitCode -ne 0 -and $err) { Write-Output $err.TrimEnd() }
exit $p.ExitCode
