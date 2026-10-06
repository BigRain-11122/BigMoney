# 代码审查：llm_assist.py

> 本文件由 LLM（qwen3.8:4b，local 通道）生成 · 未经人工审计 · 主张非指令（防注入纪律，内容须人工核验后才可作为依据）
生成时间：2026-10-06

审查对象：`scripts\llm_assist.py`

[高] 行 103-105：`_post` 将 `HTTP 405 Method Not Allowed` 错误误报为 `unreachable`，导致路由降级失败（如 `/api/tags` POST 被当网络断开），应改为 `405` 单独捕获并返回空模型列表。

[高] 行 128-131：`_log_usage` 在 `OSError` 时静默丢弃，但 `USAGE_PATH` 是 append-only 且无定期清理，长期运行会无限增长磁盘占用，应增加定期 compaction 或轮转机制。

[中] 行 134-135：`_log_usage` 中 `os.replace(tmp, USAGE_PATH)` 在文件被占用（如多进程/日志轮转）时可能失败，应改用 `shutil.move` 或 `atomic_write` 模式。

[中] 行 148-149：`_gen` 中 `num_predict=900` 硬编码，未考虑不同模型 token 长度差异，可能导致短模型截断或长模型超时，应改为 `num_predict=None` 或动态计算。

[低] 行 176-177：`_research_path` 使用 `startswith` 判断路径安全，但未考虑 `..` 或 `.` 的边界情况（如 `research/../engine`），应改用 `os.path.realpath` 或 `os.path.commonpath` 做绝对路径校验。
