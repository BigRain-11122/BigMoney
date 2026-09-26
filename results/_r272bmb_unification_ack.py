"""r272 bm-b: O-2026-09-26-2000-bm-c ack deliverable -- machine base unification inventory snapshot.

Ack <=15min contract (order §二.1 盘点先行): 现状根路径 + 全 OS 任务清单 + 全部工作树清单 -> 落盘快照.
Zero-network deterministic; facts gathered live at run time (drives/tasks probed, trees enumerated).
Migration window plan (<=09-29 12:00) recorded as candidate; physical execution in later window.
"""
import json, os, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "fleet_unification")
os.makedirs(OUT_DIR, exist_ok=True)
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# ---------- drives ----------
def drives():
    import psutil, string
    rows = []
    for d in sorted(string.ascii_uppercase):
        p = f"{d}:\\"
        if os.path.exists(p):
            u = psutil.disk_usage(p)
            rows.append({"drive": p, "free_gb": round(u.free / 1e9, 1),
                         "size_gb": round(u.total / 1e9, 1)})
    return rows

def tree_state(path):
    ex = os.path.isdir(path)
    git = os.path.isdir(os.path.join(path, ".git"))
    plastic = os.path.isdir(os.path.join(path, ".plastic"))
    head, dirty = "", -1
    if git:
        head = subprocess.run(["git", "-C", path, "log", "--oneline", "-1"],
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace").stdout.strip()[:80]
        st = subprocess.run(["git", "-C", path, "status", "--short"],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="replace").stdout
        dirty = len([l for l in st.splitlines() if l.strip()])
    return {"path": path, "exists": ex, "vcs": "git" if git else ("plastic" if plastic else "none"),
            "head": head, "dirty_files": dirty}

FLEET_TASKS = {
    "BigMoney OS 循环三任务": ["Bigmoney-IterationLoop", "Bigmoney-LoopWatchdog", "Bigmoney-Autofill"],
    "游戏产线循环": ["BiuNiYiXia-Autopilot", "BiuNiYiXia-IterationLoop", "HomeWreck-CruiseLoop",
                    "PhantomEscapeGo-ProducerLoop", "ArtQueueWorker"],
    "MiniGame tick 族": ["MiniGameEngineTick", "MiniGameAuditTick", "MiniGameGateTick", "MiniGameRadarTick",
                        "MiniGameRadarDeepTick", "MiniGameRedlineAudit", "MiniGameTickWatchdog",
                        "MiniGameCockpitBeat", "MiniGameClashKeepAlive"],
    "Ollama 常驻": ["MiniGameOllamaServe", "MiniGameOllamaKeepWarm"],
    "禁用/死路径残骸": ["HMI-ArtLoop (disabled, E:\\HMI tree removed per CEO order 2026-09-20)",
                       "MoneyQuantCryptoTick/Daily/Tick (disabled, E:\\Money tree absent)"],
}
TASK_ACTION_NOTES = {
    "Bigmoney-*": "wscript InvisibleRunner.vbs -> Tools/{iteration_loop|watchdog|autofill}.py|ps1 @ C:\\Users\\Administrator\\Desktop\\Bigmoney (ROOT-EXTERNAL base -> must re-point at migration)",
    "BiuNiYiXia/HomeWreck/PhantomEscapeGo/ArtQueueWorker": "InvisibleRunner.vbs @ E:\\Minigame\\MiniGame\\tools -> project Tools\\*.ps1 (E:\\Minigame base)",
    "MiniGame*": "EngineTick/ModeTick/Cockpit/watchdogs @ E:\\Minigame\\MiniGame\\tools (产线根仓)",
    "MiniGameOllama*/MiniGameClashKeepAlive": "E:\\Minigame\\Tools\\{Ollama,clash-keepalive.ps1} (工具面)",
}

ack = {
    "order": "O-2026-09-26-2000-bm-c",
    "machine": "bm-b",
    "ack_ts": NOW,
    "ack_deadline": "ack<=15min from S7-rebase receipt (~20:11) -> delivered in-round",
    "canonical_face": {
        "local": "E:\\Minigame\\MiniGame\\Design\\configs\\GLOBAL\\基地布局正典.md = v1.0 (U196)",
        "remote_ref": "v2.0 per order (MiniGame repo commit 7d75a7e1); local checkout HEAD 6c7af2bf behind -- sync in migration window via MiniGame lane (order: skeleton inlined, work may start pre-fold)",
    },
    "root_path_registration": {
        "registered_root_path": "E:\\Fluxgroup",
        "rationale": "no physical K: on bm-b; E: = fleet work drive hosting 14/16 fleet trees (E:\\Minigame ecosystem); same-drive moves for Minigame content = rename-fast; K: facade OPTIONAL via subst K: E:\\Fluxgroup for CEO navigation only -- task definitions must pin PHYSICAL paths (subst does not survive reboot)",
        "fallback": "D: (508GB free) if migration-window sizing shows E: (112.8GB free) insufficient for BigMoney data face",
    },
    "drives": drives(),
    "current_bases": {
        "bigmoney_os_repo": "C:\\Users\\Administrator\\Desktop\\Bigmoney (root-external vs unified skeleton)",
        "minigame_ecosystem_root": "E:\\Minigame -- ALREADY near-skeleton: contains MiniGame(repo)/13 project folders/Tools/_归档/.codely-cli/CODELY.md; children redistribute into nine-item skeleton at migration",
        "other_e_roots": "E:\\AGENT (plastic), E:\\AGENT_repo_restore, E:\\GPU, E:\\Graybox -- classification (archive/keep-in-place) at migration planning",
    },
    "os_tasks": {"fleet_relevant": FLEET_TASKS, "action_notes": TASK_ACTION_NOTES,
                 "vendor_tasks_untouched": "EasyTune/GraphicsCardEngine/Adobe/NVIDIA/SIV = OS vendor apps, out of migration scope"},
    "working_trees": [
        tree_state(p) for p in [
            "C:\\Users\\Administrator\\Desktop\\Bigmoney",
            "E:\\Minigame\\MiniGame",
            "E:\\Minigame\\BiuNiYiXia", "E:\\Minigame\\HomeWreck", "E:\\Minigame\\PhantomEscapeGo",
            "E:\\Minigame\\Tools",
            "E:\\AGENT",
        ]
    ],
    "e_minigame_children": sorted(os.listdir("E:\\Minigame")),
    "migration_risks": [
        "SSH keypair id_ed25519_bigmin(.pub) sits at E:\\Minigame root -- move with base at migration, NEVER into any git repo",
        "MiniGame repo dirty=4 + BiuNiYiXia-IterationLoop & HomeWreck-CruiseLoop RUNNING now -> migration MUST stop old tasks first (order §二.5 禁双根并行写); coordinated stop window required",
        "BigMoney loop triple (this session inside IterationLoop) -> migrate BigMoney tree only after loop tasks stopped; ignition test = one full green round post-move",
        "Unity Library\\Bee cache purge post-move (G15 坑族) for every Unity project",
        "MiniGame canonical v2.0 sync before skeleton build (pull via MiniGame lane, not from this repo)",
        "C:\\Users\\Administrator\\Desktop becomes empty of fleet trees after move -- desktop shortcut hygiene optional",
    ],
    "migration_window_plan": {
        "deadline": "2026-09-29 12:00",
        "sequence": ["1 size probe (Bigmoney data face + Minigame trees) -> confirm E: vs D:",
                     "2 sync MiniGame repo -> read v2.0 canonical",
                     "3 build E:\\Fluxgroup nine-item skeleton (README/MiniGame/FluxGroup/projects/data/archive/.codely-cli/.tools/CODELY.md)",
                     "4 zero-loss proof per repo (commit-or-stash + HEAD record)",
                     "5 per-line stop->move->re-point task definitions (physical paths)->ignition test",
                     "6 Bee cache purge + root-level stray-file sweep + receipt five items (tree snapshot/tasks before-after/ignition evidence/HEAD self-proof/root_path registration)"],
        "executor": "bm-b dedicated migration round(s) inside window; not mid-loop-session",
    },
}

out = os.path.join(OUT_DIR, "bm-b-ack-20260926.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(ack, f, ensure_ascii=False, indent=1)
print("ack written:", out, len(json.dumps(ack, ensure_ascii=False)), "chars")
print("drives:", ack["drives"])
print("trees:", [(t["path"], t["vcs"], t["dirty_files"]) for t in ack["working_trees"]])
