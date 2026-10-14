#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""git-atomic-push.py — 多窗热推期 Data API 原子推送正法（晋升件·2026-10-14 全链条审查批 O-20261014-1705·versioning §4.4 配套）

用法: python Tools/git-atomic-push.py <spec.json>

spec.json:
{
  "message": "commit message（versioning §4.3·≤500 字符）",
  "retry": 5,
  "gate_depth": 10,
  "files": [
    {"mode": "full", "path": "repo/relative/path",
     "local": "C:\\abs\\local\\path", "expect_origin_blob": "<git blob sha1 | NEW>"},
    {"mode": "append", "path": "docs/orders.md", "line": "| 新行 |"}
  ]
}

流程: fetch → 读 origin 现行内容（full=expect 守卫防他窗改写·append=推时取最新尾）
      → 内容级并合 → 本地临时 index 建候选 commit（零触碰工作树/主 index）
      → Tools/git-no-reversal-check.py 反转闸（REVERSAL 行须全部 ∈ 本批程序化 my-dels·否则停推）
      → API: blobs[base64] → trees[base_tree=origin 尾树] → commits[parents=[origin 尾]]
        → PATCH refs/heads/main force:false（422 竞态=重取尾重试）
      → 验证: 回包 sha==新 commit 且 merge-base --is-ancestor 实证。
安全: token=git credential fill（进程内即弃·零落盘零回显）；force 恒 false=非快进必拒·不覆盖他窗产出。
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"K:\Fluxgroup\FluxGroup"
GATE = os.path.join(ROOT, "Tools", "git-no-reversal-check.py")
OWNER_REPO = "BigRain-11122/FluxGroup"
API = "https://api.github.com"
UA = {"Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "fluxgroup-atomic-push"}


def git(*a, **kw):
    kw.setdefault("cwd", ROOT)  # r1010: git 调用固定集团树根（脚本从任意 CWD 跑均可）
    r = subprocess.run([GIT] + list(a), capture_output=True, **kw)
    return r.stdout, r.returncode


def die(msg):
    print("ABORT: " + msg)
    sys.exit(1)


def get_token():
    req_path = os.path.join(os.environ.get("TEMP", os.getcwd()),
                            "credreq-%d.txt" % os.getpid())
    with open(req_path, "w", encoding="ascii", newline="\n") as f:
        f.write("protocol=https\nhost=github.com\n\n")
    env = dict(os.environ)
    env["GCM_INTERACTIVE"] = "never"
    r = subprocess.run(["cmd", "/c", GIT, "credential", "fill", "<", req_path],
                       capture_output=True, env=env)
    try:
        os.remove(req_path)
    except OSError:
        pass
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith("password="):
            tok = line.split("=", 1)[1].strip()
            if tok:
                return tok
    die("git credential fill 未取到 token（GCM 凭据缺失）")


def api(method, endpoint, token, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(API + endpoint, data=data, method=method)
    for k, v in UA.items():
        req.add_header(k, v)
    req.add_header("Authorization", "token " + token)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "replace") or "{}")
        except Exception:
            return e.code, {}


def esc60(s):
    return s.strip()[:60].encode("unicode_escape").decode("ascii")


def my_dels_of(old_text, new_text):
    old = {l.strip() for l in old_text.splitlines() if len(l.strip()) >= 16}
    new = {l.strip() for l in new_text.splitlines() if len(l.strip()) >= 16}
    return {esc60(l) for l in (old - new)}


def run_gate(cand, depth, dels):
    r = subprocess.run([sys.executable, GATE, cand, "origin/main",
                        "--depth", str(depth)], capture_output=True,
                       cwd=ROOT)  # r1010: gate 必须在集团树语境跑（否则拿错 origin/main 出假阳）
    out = r.stdout.decode("utf-8", "replace")
    sys.stdout.write(out)
    if r.returncode == 0:
        return
    flagged = []
    for l in out.splitlines():
        if l.startswith("  REVERSAL") and "::" in l:
            flagged.append(l.split("::", 1)[1].strip())
    dels = {d.strip() for d in dels}  # esc60 截断第 60 字符恰为空格时 flagged 已 strip→比对假阳性（10-14 实锚·BOM 散热行）
    unexpected = [f for f in flagged if f not in dels]
    if unexpected:
        for f in unexpected:
            print("UNEXPECTED-REVERSAL :: " + f)
        die("反转闸抓到计划外丢行——停推·先内容级并合（以 origin 尾为锚重放）")
    print("GATE-PASS: %d 处 REVERSAL 全部 ∈ 本批程序化 my-dels（有意改写）" % len(flagged))


def main():
    if len(sys.argv) < 2:
        die("用法: python Tools/git-atomic-push.py <spec.json>")
    with open(sys.argv[1], encoding="utf-8") as fh:
        spec = json.load(fh)
    depth = int(spec.get("gate_depth", 10))
    token = get_token()
    retries = int(spec.get("retry", 5))

    for attempt in range(1, retries + 1):
        _, rc = git("fetch", "origin")
        if rc != 0:
            die("git fetch origin 失败")
        out, _ = git("rev-parse", "origin/main")
        tip = out.decode("ascii").strip()
        out, _ = git("rev-parse", tip + "^{tree}")
        tip_tree = out.decode("ascii").strip()

        contents = {}
        dels = set()
        for f in spec["files"]:
            path = f["path"]
            out, rc = git("show", "origin/main:" + path)
            old_bytes = out if rc == 0 else None
            out, rc = git("rev-parse", "origin/main:" + path)
            old_blob = out.decode("ascii").strip() if rc == 0 else None
            if f["mode"] == "full":
                if f.get("expect_origin_blob") == "NEW":
                    if old_blob is not None:
                        die("预期新增但 origin 已存在: " + path)
                elif old_blob != f.get("expect_origin_blob"):
                    die("守卫失配（他窗已改 %s·须重读重并合）: origin=%s expect=%s"
                        % (path, old_blob, f.get("expect_origin_blob")))
                with open(f["local"], "rb") as fh:
                    new_bytes = fh.read()
                if old_bytes is not None:
                    dels |= my_dels_of(old_bytes.decode("utf-8-sig", "replace"),
                                       new_bytes.decode("utf-8-sig", "replace"))
            elif f["mode"] == "append":
                if old_bytes is None:
                    die("append 目标在 origin 不存在: " + path)
                new_bytes = old_bytes
                if not new_bytes.endswith(b"\n"):
                    new_bytes += b"\n"
                new_bytes += f["line"].encode("utf-8") + b"\n"
            else:
                die("未知 mode: " + str(f["mode"]))
            contents[path] = new_bytes

        # 本地候选 commit（反转闸用·零触碰工作树与默认 index）
        tmpdir = os.environ.get("TEMP", os.getcwd())
        idx = os.path.join(tmpdir, "atmpush-%d.idx" % os.getpid())
        if os.path.exists(idx):
            os.remove(idx)
        env_idx = dict(os.environ)
        env_idx["GIT_INDEX_FILE"] = idx
        _, rc = git("read-tree", tip_tree, env=env_idx)
        if rc != 0:
            die("read-tree 失败")
        blobfile = os.path.join(tmpdir, "atmpush-%d.blob" % os.getpid())
        for path, data in contents.items():
            with open(blobfile, "wb") as fh:
                fh.write(data)
            out, rc = git("hash-object", "-w", blobfile)
            if rc != 0:
                die("hash-object 失败: " + path)
            blob = out.decode("ascii").strip()
            _, rc = git("update-index", "--add", "--cacheinfo",
                        "100644,%s,%s" % (blob, path), env=env_idx)
            if rc != 0:
                die("update-index 失败: " + path)
        out, rc = git("write-tree", env=env_idx)
        if rc != 0:
            die("write-tree 失败")
        cand_tree = out.decode("ascii").strip()
        out, rc = git("commit-tree", cand_tree, "-p", tip, "-m", "atomic gate candidate")
        if rc != 0:
            die("commit-tree 失败")
        cand = out.decode("ascii").strip()
        run_gate(cand, depth, dels)
        for p in (idx, blobfile):
            if os.path.exists(p):
                os.remove(p)

        # API 原子链: blobs -> tree(base_tree=origin 尾树) -> commit(parents=[origin 尾])
        entries = []
        for path, data in contents.items():
            st, body = api("POST", "/repos/%s/git/blobs" % OWNER_REPO, token,
                           {"content": base64.b64encode(data).decode("ascii"),
                            "encoding": "base64"})
            if st not in (200, 201) or "sha" not in body:
                die("blob 创建失败 %s: HTTP %s %s" % (path, st, body))
            entries.append({"path": path, "mode": "100644", "type": "blob",
                            "sha": body["sha"]})
        st, tbody = api("POST", "/repos/%s/git/trees" % OWNER_REPO, token,
                        {"base_tree": tip_tree, "tree": entries})
        if st not in (200, 201) or "sha" not in tbody:
            die("tree 创建失败: HTTP %s %s" % (st, tbody))
        st, cbody = api("POST", "/repos/%s/git/commits" % OWNER_REPO, token,
                        {"message": spec["message"], "tree": tbody["sha"],
                         "parents": [tip]})
        if st not in (200, 201) or "sha" not in cbody:
            die("commit 创建失败: HTTP %s %s" % (st, cbody))
        new_sha = cbody["sha"]
        st, rbody = api("PATCH", "/repos/%s/git/refs/heads/main" % OWNER_REPO,
                        token, {"sha": new_sha, "force": False})
        if st == 200 and rbody.get("object", {}).get("sha") == new_sha:
            time.sleep(1)
            git("fetch", "origin")
            _, rc = git("merge-base", "--is-ancestor", new_sha, "origin/main")
            if rc == 0:
                print("PUSH-OK %s (attempt %d · origin/main contains new commit)"
                      % (new_sha[:9], attempt))
                return
            die("PATCH 回包 sha 一致但复取不含新 commit（须人工核）")
        print("ATTEMPT %d 竞态（HTTP %s %s）→ 重取尾重试"
              % (attempt, st, rbody.get("message", "")))
        time.sleep(2)
    die("重试耗尽仍竞态——稍后重跑（append 幂等性=重跑前先核尾防重行）")


if __name__ == "__main__":
    main()
