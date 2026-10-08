"""r771 bm-c png-fix: byte-surgical replace of the facts-extraction regex
miss ('png ?B' -> 'png 66,152B', from _r771bmc_qa_runner.out verified line)
across state/heartbeat/report-row faces written by _r771bmc_close.py;
BOM/EOL preserving, json.loads validation on both JSONs after rewrite."""
import json

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OLD = "png ?B"
NEW = "png 66,152B"
PATHS = [
    r"state-bm-c.json",
    r"fleet\machines\bm-c.json",
    r"round_reports-bm-c.md",
]


def main():
    for rel in PATHS:
        p = REPO + "\\" + rel.replace("/", "\\")
        with open(p, "rb") as fh:
            data = fh.read()
        bom = data.startswith(b"\xef\xbb\xbf")
        body = data[3:] if bom else data
        text = body.decode("utf-8")
        n = text.count(OLD)
        if n:
            text = text.replace(OLD, NEW)
            out = text.encode("utf-8")
            if bom:
                out = b"\xef\xbb\xbf" + out
            with open(p, "wb") as fh:
                fh.write(out)
        print("%s: replaced=%d bom=%s" % (rel, n, bom))
    for rel in (r"state-bm-c.json", r"fleet\machines\bm-c.json"):
        p = REPO + "\\" + rel
        j = json.loads(open(p, "rb").read().decode("utf-8-sig"))
        assert isinstance(j["heartbeat_epoch_utc"], int)
        assert j["round_no"] == 772
    print("PNGFIX_OK json_valid epoch_int round772")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
