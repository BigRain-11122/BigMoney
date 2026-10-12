# r954b: extract D03_two_worlds frames (landed 04:12 after main batch) -> sheet3
import importlib.util
spec = importlib.util.spec_from_file_location("q", r"results\_r954bmc_qc_extract.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
paths = [m.extract("D03_two_worlds", t) for t in [0.5, 1.3, 2.1, 2.9, 3.7, 4.5]]
m.sheet("_r954bmc_qc_sheet3.png", [("D03_two_worlds", paths)])
print("D03 frames done")
