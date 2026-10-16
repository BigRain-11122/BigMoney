"""sitecustomize.py - system-wide Python startup hook.

Global silence policy (2026-10-08): any AI / background Python process that
runs without a visible console (launched via VBS shim, pythonw.exe, codely,
scheduled task, etc.) must spawn ALL child processes hidden.  No console
window, no Windows Terminal tab, no flash.

Two mechanisms:
  1. multiprocessing workers -> pythonw.exe (GUI subsystem, never allocates
     a console).  Applies to ProcessPoolExecutor, multiprocessing.Pool, etc.
  2. subprocess.Popen / os.system / os.popen -> CREATE_NO_WINDOW when the
     parent has no console.  Applies to every child: python scripts, git,
     node, cmd, anything.

When the parent DOES have a console (user typing in a terminal), nothing is
suppressed -- interactive use is untouched.
"""
import os
import sys

if sys.platform == "win32":
    # ------------------------------------------------------------------
    # Detect headless: does this process own a console window?
    # GetConsoleWindow() returns NULL when there is no attached console.
    # ------------------------------------------------------------------
    try:
        import ctypes
        _has_console = ctypes.windll.kernel32.GetConsoleWindow() != 0
    except Exception:
        _has_console = True  # conservative: don't suppress if unsure

    # ------------------------------------------------------------------
    # 1. multiprocessing workers -> pythonw.exe
    # ------------------------------------------------------------------
    try:
        import multiprocessing

        exe = sys.executable
        if exe.lower().endswith("python.exe"):
            pythonw = exe[:-len("python.exe")] + "pythonw.exe"
        else:
            pythonw = exe  # already pythonw.exe or frozen

        if (os.path.exists(pythonw)
                and os.path.basename(pythonw).lower() == "pythonw.exe"):
            multiprocessing.set_executable(pythonw)
    except Exception:
        pass

    # ------------------------------------------------------------------
    # 2. subprocess / os.system / os.popen -> CREATE_NO_WINDOW (headless only)
    # ------------------------------------------------------------------
    if not _has_console:
        CREATE_NO_WINDOW = 0x08000000

        try:
            import subprocess

            _orig_Popen = subprocess.Popen

            def _silent_Popen(*args, **kwargs):
                cf = kwargs.get("creationflags", 0) or 0
                kwargs["creationflags"] = cf | CREATE_NO_WINDOW
                return _orig_Popen(*args, **kwargs)

            subprocess.Popen = _silent_Popen
            # subprocess.run / call / check_call / check_output all delegate
            # to Popen, so they are covered automatically.
        except Exception:
            pass

        try:
            _orig_system = os.system

            def _silent_system(cmd):
                # cmd.exe /c with CREATE_NO_WINDOW; return exit code.
                import subprocess as _sp
                try:
                    r = _sp.run(cmd, shell=True,
                                creationflags=CREATE_NO_WINDOW)
                    return r.returncode
                except Exception:
                    return _orig_system(cmd)

            os.system = _silent_system
        except Exception:
            pass

        try:
            _orig_popen = os.popen

            def _silent_popen(cmd, mode="r", buffering=-1):
                import subprocess as _sp
                if "r" in mode:
                    p = _sp.Popen(cmd, shell=True, stdout=_sp.PIPE,
                                  stderr=_sp.STDOUT, text=True,
                                  creationflags=CREATE_NO_WINDOW)
                    return os._wrap_close(p.stdout, p)
                else:
                    p = _sp.Popen(cmd, shell=True, stdin=_sp.PIPE,
                                  text=True,
                                  creationflags=CREATE_NO_WINDOW)
                    return os._wrap_close(p.stdin, p)

            os.popen = _silent_popen
        except Exception:
            pass
