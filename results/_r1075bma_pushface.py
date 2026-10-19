import json, datetime

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
tip = "43cfd0008e6e3c7eaebf5febf9a977791ab6e841"

pv = {
    "ts": ts,
    "origin_tip": tip,
    "behind": 0,
    "ahead": 0,
    "note": "r1075 delivery first-try clean: rebase --autostash S0 absorbed bm-c r1111/r1112 (W276 closeout + W277 seat); pop-UU watermark_red newer-wins single-shot (theirs 08:19:04); push 6e5410654f..43cfd0008e main->main no race; post-push fetch ls-tree behind-0 ahead-0",
}

sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["push_verified"] = pv
st["sync"] = dict(pv)
st["last_delivery_verified_at"] = ts
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("push_verified face written at", ts)
