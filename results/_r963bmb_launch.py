import py_compile, subprocess
py_compile.compile(r'results\_r963bmb_closeout.py', doraise=True)
subprocess.Popen(['pythonw', r'results\_r963bmb_closeout.py'], creationflags=0x08000000)
print('COMPILE_OK LAUNCHED r963 closeout (detached pythonw)')
