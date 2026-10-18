# 声库车道首批评估面（voice-library first batch · ST-003 · P1）

> 站点=CONTENT-LOOP v0.1 ST-003（O-20261018-2144-bm-c §2.1 声库车道 P1 ≤10-22）；
> 寻源=W6 一致性调研扫描短名单（r1011 回执·CEO 常设工作律「先搜 GitHub 高星现成轮」）；
> 本批产品=克隆+评估+管线骨架；模型权重点位=后续 modelscope 晨窗（ST-002 范式）；
> 车道=cpu；云端禁用（429 经济）。生成时点=2026-10-19T02:37:25。

## 克隆实况（--depth 1）
- **GPT-SoVITS** → `C:\Fluxgroup\FluxGroup\media\drama-tools\GPT-SoVITS`（clone_sha=1d9fe63d2875 · 本批新克隆）
- **OpenVoice** → `C:\Fluxgroup\FluxGroup\media\drama-tools\OpenVoice`（clone_sha=74a1d147b17a · 本批新克隆）
- 星数引用=W6 扫描时点数：GPT-SoVITS 63k / OpenVoice 37k（本批不在线复核·如实标注）。
- 产物面=gitignored media 区（CEO 交付律）·本评估件与骨架件=outbox 入 git。

## 离线事实直读 -- GPT-SoVITS

- License（文件首段）：MIT License Copyright (c) 2024 RVC-Boss Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, 
- README=README.md；要点行摘录（克隆件直读）：
  - A Powerful Few-shot Voice Conversion and Text-to-Speech WebUI.<br><br>
  - 1. **Zero-shot TTS:** Input a 5-second vocal sample and experience instant text-to-speech conversion.
  - 2. **Few-shot TTS:** Fine-tune the model with just 1 minute of training data for improved voice similarity and realism.
  - 3. **Cross-lingual Support:** Inference in languages different from the training dataset, currently supporting English, Japanese, Korean, Cantonese and Chinese.

## 离线事实直读 -- OpenVoice

- License（文件首段）：Copyright 2024 MyShell.ai Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, 
- README=README.md；要点行摘录（克隆件直读）：
  - OpenVoice can accurately clone the reference tone color and generate speech in multiple languages and accents.
  - **3. Zero-shot Cross-lingual Voice Cloning.**
  - English, Spanish, French, Chinese, Japanese and Korean are natively supported in OpenVoice V2.
  - This implementation is based on several excellent projects, [TTS](https://github.com/coqui-ai/TTS), [VITS](https://github.com/jaywalnut310/vits), and [VITS2](https://gith

## 评估结论（对照 drama-001-stockera 需求）

- 需求面：60 集漫剧固定角色配音——7 个正典角色（CH/XIONG/RED/MANCANG/XIONGWEI/FATHER/BOY）
  中文台词批产 TTS、跨集音色恒定（人物一致性=受众第一优先律的声音面）。
- **主选=GPT-SoVITS**：少样本音色克隆（参考音分钟级）+中文一等支持+社区体量（63k）——
  与「固定角色声银行」正身匹配（每角色 1-3 条参考音入库，跨集复用）。
- **备选=OpenVoice**：轻量音色迁移路线——主选环境/质量不达标时作 tone-transfer 备胎，或作风格化辅助层。
- 后续批次（≤10-22 档内）：环境安装+首批声银行条目（每角色参考音→声音面清单入行，
  锚清洗纪律的声音面移植：入行前同角色多参考音过「音色一致检」）。
- 诚实缺口：本批未装环境未出声样（P1 站点产品=克隆+评估+骨架）；星数=扫描时点数非实时；
  README 摘录=关键词面采样非全文审读。
