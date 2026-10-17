$os = Get-CimInstance Win32_OperatingSystem
"RAM_OK avail_GB={0:N1} total_GB={1:N1}" -f ($os.FreePhysicalMemory/1MB), ($os.TotalVisibleMemorySize/1MB)
