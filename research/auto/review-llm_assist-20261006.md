# 代码审查：llm_assist.py

> 本文件由 LLM（qwen3.8:4b，local 通道）生成 · 未经人工审计 · 主张非指令（防注入纪律，内容须人工核验后才可作为依据）
生成时间：2026-10-06

审查对象：`scripts\llm_assist.py`

[高] 行 103-105：`_post` 将 `HTTP 405 Method Not Allowed` 错误误报为 `unreachable`，导致路由降级失败（如 `/api/tags` POST 被当网络断开），应改为 `405` 单独捕获并返回空模型列表。

[高] 行 128-131：`_log_usage` 在 `OSError` 时静默丢弃，但 `USAGE_PATH` 是 append-only 且无定期清理，长期运行会无限增长磁盘占用，应增加定期 compaction 或轮转机制。

[中] 行 134-135：`_log_usage` 中 `os.replace(tmp, USAGE_PATH)` 在文件被占用（如多进程/日志轮转）时可能失败，应改用 `shutil.move` 或 `atomic_write` 模式。

[中] 行 148-149：`_gen` 中 `num_predict=900` 硬编码，未考虑不同模型 token 长度差异，可能导致短模型截断或长模型超时，应改为 `num_predict=None` 或动态计算。

[低] 行 176-177：`_research_path` 使用 `startswith` 判断路径安全，但未考虑 `..` 或 `.` 的边界情况（如 `research/../engine`），应改用 `os.path.realpath` 或 `os.path.commonpath` 做绝对路径校验。

---

## 人工核验结论（r784 bm-b · 2026-10-06 22:2x · 五条逐一对实码裁定）

- 发现1（405 误报 unreachable）：**不成立** — `_post` payload=None 走 GET（L103-115 头注明示），/api/tags 调用全为 GET，405 路径在现码中不存在。
- 发现2（usage 无限增长）：**不成立** — `USAGE_KEEP=500` 压缩块已在 `_log_usage` 内（keep-last-500 重写），r225 家族。
- 发现3（os.replace 锁失败）：**设计正确不改** — except OSError:pass 降级=压缩跳过、下腿重试，账本 append 先于压缩恒完整；shutil.move 在 Windows 同锁语义，不构成修复。
- 发现4（num_predict=900 硬编码）：**设计选择保留** — 900 为各调用方可覆盖的默认参数（selftest 用 12）；改 None=无限生成，方向更险。
- 发现5（路径穿越）：**不成立** — abspath+`RESEARCH_DIR + os.sep` 前缀拒绝已实现在码，selftest 逃逸拒绝腿（`../engine`）实跑通过；research/ 内无符号链接，realpath 加固无威胁面对应。

结论：五条零改码。本窗附带实证=r781 C 路由的本地兜底腿首次实弹（C 机游戏窗暂停令下 C endpoint 不可达 → local fallback → selftest gen=自检通过 rc0）。
