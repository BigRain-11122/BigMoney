"""_r430bmc_pit_append.py -- S4: append r430 driver-generation-selection pit
to research/pit-ps.md (r429 family upstream face). Byte-accounted append with
verbatim-in-place assert + appended-core md5 (CRLF worktree face)."""
import hashlib

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-ps.md"
LINE = ("- [2026-10-03 21:3x r430 bm-c] S6 驱动代际误选坑（r429 三件套正确执行前提下仍犯的上游面·"
        "当场抓回零实伤·黄金周 no-op 日零数据面影响）：results/ 内多代 _rNNNbmc s6 旧驱动与正典并存时，"
        "轮内点火按「件名轮号新」直觉取件=取到 r427 掉腿旧版（r428 已定谳其静默掉 4 腿："
        "update_fund_premium+live_paper/t35_open_fill_verify/t24_prospect_paper 新 bar 探测面）——"
        "33 腿跑绿看似全绿实为维护面盲跑（交易日新 bar 到达时该面永不触发）。当场自愈=正典 "
        "Tools/_r428bmc_s6.py 37 腿复跑+_r430bmc_s6_log.txt 重立证据名（NON-ZERO LEGS: none·"
        "dualrun streak 31）+r429 三件套全程（count==2 断言替换 LOG 双点→跑→还原）且还原步增补 "
        "r372 EOL 双空间正法：git show HEAD blob=LF 面、工作树正典态=CRLF 面，还原必须 LF→CRLF "
        "转换后写盘，sha 才与预改工作树恒等（4ee7773ee8bee2de 实证）+git 清洁态双验。"
        "How to apply：S6 链点火一律取 Tools/_r428bmc_s6.py 正典件（results/ 旧代 s6_chain 禁再调用）；"
        "正典件被三件套临时改动后必须同轮还原 HEAD 态（CRLF 空间）；「掉腿跑绿」比「腿红」更险——"
        "绿面零报警，缺腿只能靠驱动代际纪律防（每轮点火前核对腿数=37）。\r\n").encode("utf-8")

b = open(P, "rb").read()
assert b.count(b"r430 bm-c] S6") == 0, "already appended"
assert b.endswith(b"\r\n"), "unexpected tail"
open(P, "ab").write(LINE)
t = open(P, "rb").read()
assert t == b + LINE, "append not byte-exact"
assert t.count(LINE) == 1 and LINE in t, "verbatim-in-place FAIL"
core = hashlib.md5(LINE.replace(b"\r\n", b"\n")).hexdigest()
print("PIT_APPEND_OK +%dB CRLF-face (LF-blob md5=%s) size=%dB" % (len(LINE), core, len(t)))
