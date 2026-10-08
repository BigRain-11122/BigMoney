# -*- coding: utf-8 -*-
"""MV-0001 S1 剧本/分镜生成腿（Ollama qwen2.5:14b·本地）
CEO 第六追加令：方向贴合歌曲本意禁跳脱——主线=泥板誓言的考古一生（刻→埋→风化→出土→橱窗凝视→一切又重演）。
消费三证：导演转译表（R-…-directors-01）+粉丝波（R-…-fandemand-01）+爆款痛点波（R-…-hits-painpoints-01）。"""
import json, urllib.request, pathlib, sys, time

HERE = pathlib.Path(__file__).parent
API = "http://127.0.0.1:11434/api/generate"

SECTIONS = [
    # (id, 段名, 起秒, 终秒, 风格段, 叙事任务)
    ("INTRO",  "前奏",       0,  14, "A", "氛围定场：博物馆暗场·一束灯照向橱窗泥板（与尾奏回环呼应）"),
    ("V1",     "主歌一",     14, 34,  "A", "西元前：恋人以楔形文字在泥板刻下誓言（刻字手特写/汉谟拉比法典黑色玄武岩背景）"),
    ("PRE1",   "预副歌一",   34, 44,  "A", "祭司·神殿·征战·弓箭：誓言的见证场景（庄重非暴力·剪影化）"),
    ("C1",     "副歌一",     44, 68,  "B", "『我给你的爱写在西元前·深埋在美索不达米亚平原』：泥板被黄沙深埋·底格里斯河水漫延"),
    ("INTER",  "间奏",       68, 80,  "B", "千年风化：沙层堆积·王朝更迭剪影带（浮雕横移）·誓言仍在泥板里"),
    ("V2",     "主歌二",     80, 100, "B", "『橱窗前凝视碑文』现代线开场：考古现场出土瞬间（毛刷拂沙·泥板文字重见天日）"),
    ("PRE2",   "预副歌二",   100, 110, "C", "苏美女神意象：誓言的神性见证（金与青·许愿手势剪影）"),
    ("C2",     "副歌二",     110, 134, "C", "『出土发现·字迹依然清晰』：博物馆修复室·灯光下文字清晰·考古学家凝视"),
    ("BRIDGE", "说唱段",     134, 168, "C", "古巴比伦王颁布汉谟拉比法典：知识点蒙太奇（玄武岩法典/楔形文字/两河地图/征战浮雕——考证保真·庄重呈现）"),
    ("C3",     "尾副歌",     168, 192, "C", "『我给你的爱写在西元前』情感峰值：橱窗前双人剪影（你凝视碑文·我在旁凝视你=歌词原生场景）"),
    ("OUTRO",  "尾奏",       192, 256, "C", "『一切又重演』回环：镜头拉远·橱窗倒影里映出西元前刻字场景=首尾闭环·灯暗"),
]

STYLE_BRIEF = {
    "A": "邝盛式玄武岩黑金单色戏剧场：ancient Mesopotamian bas-relief art, obsidian black background with warm gold accents, dramatic chiaroscuro, stylized flat relief figures, cuneiform carvings, museum-grade artifact aesthetic, non-photorealistic illustration",
    "B": "美索不达米亚沙金×青金石蓝：Mesopotamian fresco frieze, sand-gold and lapis-lazuli blue split-tone, ziggurat silhouettes, Tigris river delta, wind-carved clay tablets, epic stylized landscape, painterly relief texture, non-photorealistic",
    "C": "博物馆冷岩青×暖金：modern museum hall with ancient artifact, cool slate-teal ambience with warm golden display lighting, vitrine glass reflections, archaeologist silhouettes, Y2K film grain, cinematic stylized illustration, non-photorealistic",
}
NEG = "photorealistic, photo, realistic human face, 3D render, blurry, low quality, watermark, text errors, deformed hands, uncanny face"

def gen_section(sec):
    sid, name, t0, t1, style, task = sec
    dur = t1 - t0
    n = max(2, min(5, round(dur / 7)))
    prompt = f"""你是 BigStream 的 MV 分镜师。为《爱在西元前》改编 MV 生成 {name} 段（{t0}-{t1} 秒·约{dur}秒）的分镜 {n} 镜。
叙事任务（必贴合）：{task}
风格段 {style} 提示词基底：{STYLE_BRIEF[style]}
硬约束：①每镜锚定歌词原生意象·禁跳脱禁加无出处设定②非写实无写实人脸③拟情镜头（眼神/凝视/手部动作传达情感）④构图讲完（黄中平式定格或邝盛式动势）。
只输出 JSON 数组 {n} 项，每项：{{"shot": "{sid}1..{n}", "t_start": 估算秒, "t_end": 估算秒, "lyric_anchor": "锚定的歌词短语(≤12字)", "desc": "画面中文描述(≤40字)", "camera": "镜头动作(中文≤15字)", "sdxl_prompt": "英文出图提示词(≤60词·含风格基底关键词)", "motion": "后期动效(推/拉/摇/横移/慢放·中文)"}}。不要输出其他文字。"""
    req = urllib.request.Request(API, data=json.dumps(
        {"model": "qwen2.5:14b", "prompt": prompt, "stream": False,
         "options": {"temperature": 0.65}}).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=420) as r:
        text = json.loads(r.read().decode("utf-8"))["response"]
    s, e = text.find("["), text.rfind("]")
    if s < 0:
        raise RuntimeError(f"{sid} NO_JSON: {text[:200]}")
    shots = json.loads(text[s:e+1])
    for sh in shots:
        sh["section"], sh["style"] = sid, style
    return shots

def main():
    all_shots, fails = [], []
    for sec in SECTIONS:
        try:
            shots = gen_section(sec)
            all_shots.extend(shots)
            print("OK", sec[0], len(shots), "shots")
        except Exception as ex:
            fails.append((sec[0], str(ex)[:160]))
            print("FAIL", sec[0], str(ex)[:160])
        time.sleep(1)
    (HERE / "storyboard.json").write_text(
        json.dumps({"neg": NEG, "styles": STYLE_BRIEF, "shots": all_shots},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    # 歌词锚自检（痛点规避①闸）：锚字段缺失计数
    no_anchor = sum(1 for s in all_shots if not s.get("lyric_anchor"))
    print(f"DONE shots={len(all_shots)} fails={len(fails)} no_anchor={no_anchor}")

if __name__ == "__main__":
    main()
