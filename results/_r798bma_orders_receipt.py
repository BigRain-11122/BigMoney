# _r798bma_orders_receipt.py -- fill bm-a receipt sections for O-20261006-2110 / O-20261006-2250
# Multi-writer shared files: fresh-read-modify-write per r774 law, targeted blocks only.
import io, json, datetime

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

R2110 = r"fleet\orders\O-20261006-2110-bm-c.md"
R2250 = r"fleet\orders\O-20261006-2250-bm-c.md"
TS = now()

# ---------- O-20261006-2110 bm-a receipt ----------
s = io.open(R2110, encoding="utf-8").read()
old = """### 回执（bm-a）
- [ ] ack 行（≤15min）
- [ ] 套件部署位（路径一行）
- [ ] 本地化三处清单（GPU 任务名自报清单+大模型档位+保活任务名）
- [ ] pause 实测输出（含进程面复验行）
- [ ] status 输出
- [ ] 触发词记忆已写入（路径一行）"""
new = """### 回执（bm-a）
- [x] ack 行（≤15min）：ack {ts} r798（bm-a 收令即开工·本回执=部署+实测全量落地）
- [x] 套件部署位（路径一行）：`C:\\Users\\sjs20\\Desktop\\FluxGroup\\.codely-cli\\machine-state.ps1` + `gamewin_cron_suspend.py`（本机集团根=repo 本体·origin/main blob 直取零树触碰）
- [x] 本地化三处清单：
  - $tasks=BigCompute-OSLoop / BigCompute-OSLoop-PM / BigCompute-GPU-IdleWatch / BigCompute-CleanWindowProbe / BigCompute-OrderSentinel / BigCompute-ResidentQA / MiniGameOllamaKeepWarm / MiniGameOllamaServe（GPU 生产管线 6 件+LLM respawn 双任务；Bigmoney 值守族/EngineTick 照律保留未列入）
  - $ollamaExe=`C:\\Users\\sjs20\\AppData\\Local\\Programs\\Ollama\\ollama.exe`；$pinModel=`qwen3-8b-ud:q4_k_xl`（令面 bm-a=qwen3-8b·装机实名 face；部署时在驻=legacy qwen2.5:7b-instruct 如实披露——resume 时将按令面钉 qwen3-8b face）
  - $keepAliveTask=$null（本机无 ComfyUI/保活任务·如实声明）
- [x] pause 实测输出（含进程面复验行）：首跑 v1 揭实弹坑——llama-server 清 VRAM 6748→~1072MB 但 ollama 父进程 23:10:18 被托盘 app（`ollama app.exe`）自愈 respawn=kit 盲区；本机 v1.1 补丁（kill 面加「ollama app」×3 处）复跑=**[pause] OK production-clean (vramUsedMB=1089 = CEO desktop/gaming face, none ours)** exit 0；8 任务 disabled·cron RESULT suspended_jobs=3（幂等复跑=already_suspended backup_jobs=3）·进程面复验 ollama/ollama app/llama-server 计数=0
- [x] status 输出：`STATE: vramUsedMB=1083 ollama=False comfy=False tasks[BigCompute-CleanWindowProbe=Disabled BigCompute-GPU-IdleWatch=Disabled BigCompute-OrderSentinel=Disabled BigCompute-OSLoop=Disabled BigCompute-OSLoop-PM=Disabled BigCompute-ResidentQA=Running MiniGameOllamaKeepWarm=Disabled MiniGameOllamaServe=Disabled]` / `CRON: RESULT suspended=3` / `MODE=pause`（诚实注：BigCompute-ResidentQA 旧在飞实例仍 Running=disable 不杀存量·VRAM 面净·kit 自判 MODE=pause）
- [x] 触发词记忆已写入（路径一行）：`C:\\Users\\sjs20\\.codely-cli\\CODELY.md` Feedback 节（用户级=全工作区会话可见）+ 本令回执指针
- 备注（bm-a 实弹发现·供委员会）：①「ollama app」托盘自愈 respawn=kit 模板盲区（bm-c v2 若未覆盖建议回流上游模板）；②本机 cron 班组=集团根 store 3 件（全 stale one-shot）——quant 子工作区 store（14 件·GM 哨兵 2 常设）不在 kit 作用域=子工作区会话 REPL 闲置时仍可自触发，如实披露待裁；③resume 命令已固化（`-Mode resume`+pin qwen3-8b-ud:q4_k_xl），照令未实跑
""".replace("{ts}", TS)
assert old in s, "2110 receipt anchor missing"
s = s.replace(old, new)
io.open(R2110, "w", encoding="utf-8", newline="").write(s)

# ---------- O-20261006-2250 bm-a receipt ----------
s = io.open(R2250, encoding="utf-8").read()
old = """### 回执（bm-a）
- [ ] ack 行（≤15min）
- [ ] 双路闸值读回两行（须均 0）
- [ ] 任务运行器自审结论（自建任务全隐藏确认行+第三方列报）
- [ ] 零窗律记忆写入路径一行"""
new = """### 回执（bm-a）
- [x] ack 行（≤15min）：ack {ts} r798（与 O-20261006-2110 同窗合并执行）
- [x] 双路闸值读回两行（须均 0）：`HKCU:\\...\\Push\\Settings` → **0**；`HKCU:\\...\\Notifications\\Settings` → **0**（Set-ItemProperty 后立即 Get-ItemProperty 读回·非首设盲写）
- [x] 任务运行器自审结论：**自建任务全隐藏确认**——审计 57 项非微软任务：自建族原已隐藏 44 项（wscript //B //nologo InvisibleRunner 链）+本轮转换 13 项（CarGZH×8〔python.exe 直跑→group runner〕/FluxGroup-QuantOversightDigest〔pwsh 直跑→group runner〕/GimmeAll-AutoSentinel〔powershell 直跑→MiniGame runner〕/MoneyAutoGuardian〔powershell -WindowStyle Hidden 仍闪→group runner〕/FluxBoardAuto+BigCompute-ResidentQA〔pythonw 无闪但照律归链〕），转换=schtasks XML 换 Command/Arguments 原样重注册·逐件读回验证 wscript.exe=13/13 零败；**第三方只列报不代禁**：Adobe Acrobat Update / AdobeGCInvoker×2 / AMDInstallLauncher / ASUS AsusDriverHub / DoubaoIme ApplyUpdate / NVIDIA App SelfUpdate / OneDrive×3（闸值已覆盖其通知面）
- [x] 零窗律记忆写入路径一行：`C:\\Users\\sjs20\\.codely-cli\\CODELY.md` Feedback 节（含 13 任务转换清单+闸值 0/0 证据·10-13 回访判据面）
""".replace("{ts}", TS)
assert old in s, "2250 receipt anchor missing"
s = s.replace(old, new)
io.open(R2250, "w", encoding="utf-8", newline="").write(s)

# ---------- heartbeat orders_ack ----------
HP = r"fleet\machines\bm-a.json"
h = json.load(io.open(HP, encoding="utf-8"))
ack = h.setdefault("orders_ack", [])
for tok in ["O-20261006-2110-bm-c.md", "O-20261006-2250-bm-c.md"]:
    if tok not in ack:
        ack.append(tok)
io.open(HP, "w", encoding="utf-8", newline="").write(json.dumps(h, ensure_ascii=False, indent=1))
print("receipts written; ack count:", len(ack))
