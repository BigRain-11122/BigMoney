# r268 live validation of the ported CwdProbe (read-only, no mutation).
$ErrorActionPreference = 'Continue'
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class CwdProbe {
    [StructLayout(LayoutKind.Sequential)]
    public struct PROCESS_BASIC_INFORMATION {
        public IntPtr Reserved1;
        public IntPtr PebBaseAddress;
        public IntPtr Reserved2_0;
        public IntPtr Reserved2_1;
        public IntPtr UniqueProcessId;
        public IntPtr Reserved3;
    }
    [DllImport("ntdll.dll")]
    public static extern int NtQueryInformationProcess(IntPtr hProcess, int pic, ref PROCESS_BASIC_INFORMATION pbi, int cb, out int pSize);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern IntPtr OpenProcess(int access, bool inherit, int pid);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr baseAddress, byte[] buffer, int size, out IntPtr bytesRead);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool CloseHandle(IntPtr hObject);
    public static string GetCwd(int pid) {
        IntPtr h = OpenProcess(0x0410, false, pid);
        if (h == IntPtr.Zero) return null;
        try {
            PROCESS_BASIC_INFORMATION pbi = new PROCESS_BASIC_INFORMATION();
            int sz;
            int st = NtQueryInformationProcess(h, 0, ref pbi, Marshal.SizeOf(pbi), out sz);
            if (st != 0 || pbi.PebBaseAddress == IntPtr.Zero) return null;
            byte[] buf = new byte[8];
            IntPtr br;
            if (!ReadProcessMemory(h, (IntPtr)((long)pbi.PebBaseAddress + 0x20), buf, 8, out br)) return null;
            long pp = BitConverter.ToInt64(buf, 0);
            if (pp == 0) return null;
            byte[] us = new byte[16];
            if (!ReadProcessMemory(h, (IntPtr)(pp + 0x38), us, 16, out br)) return null;
            int len = BitConverter.ToUInt16(us, 0);
            if (len <= 0 || len > 52000) return null;
            byte[] str = new byte[len];
            long strAddr = BitConverter.ToInt64(us, 8);
            if (strAddr == 0 || !ReadProcessMemory(h, (IntPtr)strAddr, str, len, out br)) return null;
            return Encoding.Unicode.GetString(str, 0, len);
        } finally { CloseHandle(h); }
    }
}
"@
$root = 'C:\Users\sjs20\Desktop\FluxGroup'
$n = 0
foreach ($p in (Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) {
    $cwd = [CwdProbe]::GetCwd([int]$p.ProcessId)
    if ($cwd -and $cwd.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        $n++
        Write-Output ("CWD-HOLDER pid={0} name={1} cwd={2}" -f $p.ProcessId, $p.Name, $cwd)
    }
}
Write-Output "probe done, holders=$n"
