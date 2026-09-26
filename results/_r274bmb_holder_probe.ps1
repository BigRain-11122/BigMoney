# r274 holder probe (read-only): root-cause the 20:48 MG-move 3x failure.
# Three faces invisible to the executor's CommandLine quiesce scan:
#  (1) process CWD inside E:\Minigame (PEB CurrentDirectory, NtQueryInformationProcess)
#  (2) explorer folder windows parked under E:\Minigame (ShellWindows COM)
#  (3) running process image paths under E:\Minigame (HandleMasks)
# ASCII-only source (PS5.1 ANSI decode law). Output JSON to stdout.
$ErrorActionPreference = 'SilentlyContinue'
$TargetRoot = 'E:\Minigame'

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
        IntPtr h = OpenProcess(0x0410, false, pid); // QUERY_INFORMATION | VM_READ
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
            byte[] us = new byte[16]; // UNICODE_STRING at params+0x38: len(2) max(2) pad(4) buffer(8)
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

$faces = @{ ts = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'); target = $TargetRoot; cwd_holders = @(); explorer_windows = @(); image_holders = @() }

# Face 1: process CWD inside target root
foreach ($p in (Get-CimInstance Win32_Process)) {
    $cwd = [CwdProbe]::GetCwd([int]$p.ProcessId)
    if ($cwd -and ($cwd -like "$TargetRoot*")) {
        $faces.cwd_holders += @{ pid = $p.ProcessId; name = $p.Name; cwd = $cwd; cmdline = [string]$p.CommandLine }
    }
}

# Face 2: explorer folder windows under target root (rename killer invisible to CommandLine scan)
$shell = New-Object -ComObject Shell.Application
foreach ($w in $shell.Windows()) {
    $loc = [string]$w.LocationURL
    if ($loc -like 'file:///' + ($TargetRoot -replace '\\','/') + '*') {
        $faces.explorer_windows += @{ hwnd = $w.HWND; path = $loc }
    }
}

# Face 3: running images under target root
foreach ($proc in (Get-Process)) {
    if ($proc.Path -and ($proc.Path -like "$TargetRoot*")) {
        $faces.image_holders += @{ pid = $proc.Id; name = $proc.ProcessName; path = $proc.Path }
    }
}

$faces | ConvertTo-Json -Depth 4
