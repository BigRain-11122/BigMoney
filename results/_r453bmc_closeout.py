"""r453 bm-c final closeout: round-report S7-supplement line + CODELY pit line
(push-race 3-iteration saga + union-concat dedup lesson). Programmatic appends."""
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

supplement = (
    ts + "｜r453 bm-c S7-supplement｜closeout push-race 三次竞速窗收口（r450 同型·全 receipts in-repo）："
    "round commit 95c240b41 首推被拒（bm-b r655 wave 在途·non-FF）→r437 absorb 净路（b782234a4 satengine daemon 面）"
    "+merge 5 UU（CODELY append-union+attrition/lhb regen take-ours〔ours 08:00-02>theirs 07:42〕"
    "+compute_audit union 201+207→208+token_usage per-m union·109e1fff3）→二推被拒（bm-b r656 dead-estate "
    "adoption wave 在途）→二轮 absorb（4ed1bc2d6·4 daemon 面）+merge 15 UU（12 regen take-THEIRS"
    "〔survey results/_r453bmc_uu2_survey.py 实证 theirs 08:04-06 新于 ours 08:00-02·同 evidence cutoff "
    "2026-09-30 零信息损失·r656 bm-b fullmatch 律同窗互证〕+compute_audit union 208+201→209+CODELY "
    "chronological union·499b293f4 DELIVERED）→自检抓 CODELY union-concat 双侧携带 r655 对=2 条精确重复"
    "→同窗治愈（bd2cad365·keep-first 零丢失·r453/r656/r655 计数断言）→DELIVERED bd2cad365 终态"
    "（tip==remote·ahead=0·behind=0）｜本地未达 origin commit 数=0（push_verify 三证×3·r436 单源律）"
)

pitline = (
    "- [" + now.strftime("%Y-%m-%d %H:%M") + "x r453 bm-c] CODELY/append-only 面 merge-union 手术 dedup 律"
    "（2nd-iter union 实弹自检抓回）：跨机多轮 push-race 下第一次 merge 的 union 产物（他机条目）会随本机 "
    "commit 进入下一轮 merge 的两侧——第二次 CODELY suffix-union 裸 concat 即产出精确重复条目（本窗 r655 bm-b "
    "两条×2）；正法=append-only 记忆面 union 一律 exact-line dedup（keep-first）+关键 marker 计数断言"
    "（本窗 r453=1/r656=1/r655=2）后才许 add；marker 自检用行首判定勿用子串（pit 正文合法内嵌 '<<<<<<<' 字面量·"
    "r657 L68 例）。How to apply：多轮 race 收口窗 CODELY/台账 union 后必跑 dedup 探针（范式 "
    "results/_r453bmc_codely_dedup.py）。"
)

def append_entry(path, entry):
    with open(path, "rb") as f:
        f.seek(-1, 2)
        last = f.read(1)
    with open(path, "a", encoding="utf-8", newline="") as f:
        if last not in (b"\n", b"\r"):
            f.write("\r\n")
        f.write("\r\n" + entry)

append_entry(ROOT + r"\round_reports-bm-c.md", supplement)
append_entry(ROOT + r"\CODELY.md", pitline)
print("SUPPLEMENT_APPENDED ts=" + ts)
print("PITLINE_APPENDED len=" + str(len(pitline)))
