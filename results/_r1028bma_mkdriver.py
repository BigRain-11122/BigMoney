import io
c = io.open('_r1027bma_s6chain.ps1', encoding='utf-8-sig').read()
c = c.replace('results/_r1027bma_s6chain_rc.log', 'results/_r1028bma_s6chain_rc.log')
old = '"$name rc=$rc" | Out-File $log -Append -Encoding utf8'
new = '"$name rc=$rc" | Out-File $log -Append -Encoding utf8\n  Write-Host "$name rc=$rc"'
assert old in c, 'anchor missing'
c = c.replace(old, new)
io.open('_r1028bma_s6chain.ps1', 'w', encoding='utf-8').write(c)
print('driver written OK')
