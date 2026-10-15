# -*- coding: utf-8 -*-
"""
prompt_lexicon.py - BigStream 专业提示词词表机制 v1.1
CEO 三令（O-20261009-1815/1830）：①零否定词（官方改写器规则8背书）②专业参数化③机制化禁散文手写
v1.1 变更（提示词工程专家审查落地）：
- 组装器改官方顺序单段散文：身份→服装→面部→姿态→环境光→镜头风格收尾
- 槽位句法模板化（固定动词框架，分句自动变散文）
- lint 三名单+词边界正则+撇号归一+缩写捕捉+长度闸+FIX_MAP 否定自动改写
- ID 块逐字复用纪律（同一人禁止多写法=文本身份漂移）
- VIDEO_DISCIPLINE 修复机制自杀（去掉 no cuts）
来源：QwenLM/Qwen-Image 官方 prompt_utils（规则8/结构公式）+ krea-ai/krea-2 prompting.md
     + ComfyUI 官方模板活样例 + 提示词工程专家审查（2026-10-09）
"""
import re

# ================= 1. 专业词表 =================

SHOT_SIZE = {
    "ecu":  "extreme close-up", "cu": "close-up", "hs": "head-and-shoulders framing",
    "med":  "medium shot", "mw": "medium-wide framing", "wide": "wide shot",
    "ext":  "extreme wide establishing shot",
}
CAM_ANGLE = {
    "eye": "at eye level", "low": "from a low angle", "high": "from a high angle",
    "top": "top-down", "ots": "over the shoulder", "dutch": "with a subtle dutch tilt",
}
CAM_MOVE = {  # v1.2：H3 官方三维公式 Motion type + Amplitude + Speed（幅度/速度中档可省）
    "static":  "the camera holds a perfectly static shot",
    "pushin":  "the camera pushes in with small amplitude at slow speed",
    "pullout": "the camera pulls out with small amplitude at slow speed",
    "panl":    "the camera pans to the left with small amplitude at slow speed",
    "panr":    "the camera pans to the right with small amplitude at slow speed",
    "tiltup":  "the camera tilts up with small amplitude at slow speed",
    "cranedn": "the camera cranes down with small amplitude at slow speed",
    "track":   "the camera tracks alongside with small amplitude at steady speed",
    "stead":   "a steadicam follows with fluid motion at walking pace",
    "hand":    "a light handheld follow with natural sway",
    # MV 节奏专用（摄影指导补全·短镜头高风险区专用）
    "orbit":     "the camera arcs slowly around the seated subject, the background sweeping past",
    "crashzoom": "a fast crash zoom into the subject's face",
    "whippan":   "a whip pan from the tablet to the scribe with motion blur across frame",
    "macroslide": "an extreme close-up slides laterally across carved cuneiform marks with shallow focus",
    "dollyzoom": "the camera dollies in while zooming out, the background compressing behind the frozen subject",
    "craneup":   "the camera cranes up from the face to reveal the full hall",
    "tiltdown":  "the camera tilts down from the carved stone face to the working hands",
    "pushthru":  "a steadicam pushes through a torch-lit corridor, the subject revealed at the end",
}
LENS = {  # v1.2 摄影指导审查：2001 年代无变宽无奶油焦外——球面 1.85/4:3、35-50mm 深焦为主
    "24": "24mm wide-angle lens", "35": "35mm lens at f/2.8 with honest depth of field",
    "50": "50mm lens at f/2.8", "85": "85mm portrait lens at f/2.8, gentle falloff softened by diffusion filter",
}
LIGHT = {  # v1.2：色温修正+年代灯型（钠灯/荧光/穿烟逆光）+光型措辞专业化
    "tung_left": "a tungsten practical lamp at 3200K lights the face from frame left, a warm amber pool with deep falloff into shadow",
    "tung_right": "a tungsten practical lamp at 3200K lights the face from frame right",
    "window": "soft north-window daylight at 5600K wraps the subject gently",
    "golden": "golden-hour sun at 3500K rakes through the leaves, casting long warm shadows",
    "dusk": "blue-hour dusk ambience at 8000K with low-pressure sodium streetlamp pools at 2200K, deep orange against ink-blue asphalt",
    "lamp_desk": "a motivated desk-lamp key at 2900K throws a warm circle of light on the desk",
    "flame": "a single oil-lamp flame at 2000K is the only light source, chiaroscuro with the far side in soft shadow",
    "halo": "strong warm tungsten backlight at 3200K blooms through the hair into thick haze, a halo around the head, 1/2 Black Pro-Mist diffusion",
    "godray": "hard top-light shafts cut through thick temple dust and incense smoke, visible beams with drifting dust motes",
    "sodium": "night street under low-pressure sodium lamps, deep-orange pools at 2200K against ink-blue dusk, 2001 Taiwan street",
    "fluor": "greenish fluorescent classroom tubes overhead at 4300K mixing with pale window daylight, faded chalk-green blackboard",
    "onelamp": "low-key single-source lighting, a small light triangle on the shadow-side cheek under the eye, lamp at 45 degrees front and 45 degrees high",
    "butterfly": "butterfly beauty key at 3200K high in front, symmetric shadow under the nose",
    "rim": "a warm tungsten rim light through haze separates the figure from the dark background",
    "split": "split lighting, one half of the face lit and the other in full shadow",
}
GRADE = {  # v1.2：删 teal-leaning（2010s DI 套路）与 2383（印片模拟），换 2001 telecine 语法
    "tw2001": "2001 telecine grade, warm skin tones, milky lifted blacks, blooming practical highlights, slight color bleed",
    "mono": "warm amber monochrome grade with deep crushed shadows",
    "bluefire": "blue-night and orange-fire duotone grade, ink-blue shadows against amber torch pools",
    "nost": "muted nostalgic palette of ochre highlights, slate-gray midtones and desaturated greens",
}
TEXTURE = {  # v1.2 摄影指导审查（最重）：Vision3 5219/5207=2007/2009 年型号·年代错位——
    # 2001 当班=Kodak Vision 代：夜戏 500T 5279、日戏 250D 5246；gate weave 只留视频端
    "film_night": "shot on 35mm Kodak Vision 500T 5279, visible grain, halation on practical lights",
    "film_day": "shot on 35mm Kodak Vision 250D 5246, fine visible grain",
    "mist": "shot through a 1/2 Black Pro-Mist diffusion filter with heavy highlight bloom through haze",
    "soft": "slightly soft edge focus with 2001-era lens character",
}
WARDROBE_M = {
    "uniform": "a loose white short-sleeve school-uniform shirt with dark collar trim and straight-cut dark school trousers",
    "pe": "a plain grey cotton t-shirt, slightly worn, with dark school trousers",
    "home": "a plain dark cotton jacket over a white undershirt",
    "scribe": "a rough hand-woven undyed linen tunic with a simple rope belt, weathered dusty fabric",
}
WARDROBE_F = {
    "campus": "a simple plain knit top in natural slightly worn fabric and a long dark denim skirt",
    "gown": "a flowing plain white gown with simple seams",
}
# 场景/微动作词典（姿态槽只从词典生长——模糊词无从混入）
SCENE = {
    "corridor": "an open third-floor corridor window with wind moving the curtains",
    "classroom": "a sunlit classroom after class with chalk dust drifting in the light",
    "library": "a tall bookshelf aisle of an old campus library with warm tungsten desk lamps",
    "rooftop": "a rooftop edge after school with a worn canvas backpack and the old Taipei skyline in haze",
    "street": "a rain-wet campus path at night under a transparent umbrella with streetlamp reflections",
    "court": "an outdoor basketball court at dusk with a dented basketball",
    "desk": "a plain dormitory desk with a worn textbook and a tin pencil case",
    "tablet": "a clay tablet and a reed stylus on rough wooden scribe's desk in a Babylonian scriptorium",
    "hall": "an ancient Babylonian hall of mud-brick columns fading into torchlit darkness",
}
POSE_M = {
    "window_lean": "leaning at the window, gazing out at the campus field",
    "read": "browsing a worn hardcover book, head bent",
    "sit_desk": "sitting by the desk, gazing quietly downward",
    "walk_rain": "walking away down the rain-wet path",
    "bike": "riding an old steel-frame bicycle with a wire basket",
    "scribe": "pressing a reed stylus into a wet clay tablet, cuneiform marks forming",
}
# ID 块（逐字复用纪律：同一人所有镜头必须引用同一常量，禁止改写）
ID_M_2001 = ("a 20-year-old Taiwanese student with heavy-lidded monolid eyes, "
             "a thick lower lip, softly rounded cheeks and a thick black fringe "
             "lying flat over his eyebrows")
FACE_M_2001 = ("his bare face has natural matte skin with visible pores, "
               "his black hair plain and slightly messy")

VIDEO_DISCIPLINE = "Single continuous take at 24fps. "  # v1.1: 移除 no cuts（机制自杀修复）

# ================= 2. 三名单 lint（词边界正则） =================

_NEG = r"\b(not|no|don'?t|without|avoid|never|non-?)\b"
VAGUE_BANNED = [
    "beautiful", "gorgeous", "stunning", "aesthetic", "masterpiece", "best quality",
    "amazing", "atmospheric", "dreamy", "dreamlike", "charming", "nostalgic feel",
    "premium", "high quality", "8k", "hyperdetailed", "highly detailed", "intricate",
    "ethereal", "whimsical", "cozy", "surreal", "artistic", "stylish", "elegant",
    "cute", "pretty", "timeless", "vibes?", "moody", "dramatic", "intimate",
    "evocative", "captivating", "vibrant", "epic", "glowing", "flawless",
    "smooth skin", "airbrushed", "porcelain skin", "glass skin",
    "ultra realistic", "photorealistic", "award-winning", "hyperrealistic",
]
CONCEPT_BANNED = [  # 概念注入词（写进条件=注入该概念，无论肯定否定）
    "korean", "k-?pop", "kpop", "idol", "k-?drama", "ulzzang", "salon",
    "eyebrow styling", "watermark", "typography", "logo", "makeup", "beautification",
]
CINEMATIC_OK_FIRST_SENTENCE = "cinematic"  # 灰名单：仅允许首句出现 1 次
EDIT_WHITELIST = {"remove", "replace", "change", "restore", "the first image",
                  "the second image", "picture 1", "picture 2", "picture 3"}  # Edit 管线合法动词（供人工复核参考）

# 否定/病灶短语自动改写器（PROMPT-SPEC §二 对照表代码化）
FIX_MAP = [
    (r"not a korean idol,?\s*", ""), (r"no k-?pop styling,?\s*", ""),
    (r"no k-?pop makeup,?\s*", ""), (r"no makeup,?\s*", ""),
    (r"no glossy grooming,?\s*", ""), (r"no glossy hair,?\s*", ""),
    (r"no slim trendy fashion,?\s*", ""), (r"no glossy glass-skin makeup,?\s*", ""),
    (r"no modern korean styling\.?\s*", ""), (r"no korean drama styling,?\s*", ""),
    (r"no modern polish,?\s*", ""), (r"no styling( product look)?,?\s*", ""),
    (r"no see-through feathery fringe,?\s*", ""), (r"no curtain bangs,?\s*", ""),
    (r"no beautification,?\s*", ""), (r"no smoothing,?\s*", ""),
    (r"no face slimming,?\s*", ""), (r"no double eyelids,?\s*", ""),
    (r"absolutely no readable modern text[^.]*\.\s*", ""),
    (r"no typography,?\s*", ""), (r"no letters,?\s*", ""), (r"no logos,?\s*", ""),
    (r"no watermark[,.]?\s*", ""), (r"pure imagery only,?\s*", ""),
]

def _norm(s):
    return " " + s.replace("\u2019", "'").lower() + " "

def lint(prompt, mode="t2i"):
    """三名单自检闸。返回命中列表（带类别），空=过闸。mode: t2i|video|edit"""
    p = _norm(prompt)
    hits = []
    if re.search(_NEG, p):
        for m in re.finditer(_NEG, p):
            hits.append("[NEG]" + m.group(0))
    for w in VAGUE_BANNED:
        if re.search(r"\b" + w + r"\b", p):
            hits.append("[VAGUE]" + w)
    for w in CONCEPT_BANNED:
        if re.search(r"\b" + w + r"\b", p):
            hits.append("[CONCEPT]" + w)
    # cinematic 灰名单：首句 1 次合法
    n_cin = len(re.findall(r"\bcinematic\b", p))
    if n_cin > 1:
        hits.append("[VAGUE]cinematic x%d (>1)" % n_cin)
    # 长度闸（词数）
    wc = len(prompt.split())
    if wc > 200:
        hits.append("[LEN]%d words (>200)" % wc)
    if wc < 15:
        hits.append("[LEN]%d words (<15, too thin)" % wc)
    return hits

def autofix(prompt):
    """否定/病灶短语自动改写为正面等价（机械替换+复检）。"""
    s = prompt
    for pat, rep in FIX_MAP:
        s = re.sub(pat, rep, s, flags=re.I)
    s = re.sub(r"\s{2,}", " ", s).strip()
    s = re.sub(r"\s+([.,;])", r"\1", s)
    return s

# ================= 3. 组装器（官方顺序单段散文） =================
# 官方公式：身份→服装→面部/皮肤→姿态→环境+光照→镜头与风格收尾
# 槽位句法模板：固定动词框架让分句自动变散文。

def build_shot(shot, id_block, wardrobe, face, pose, scene, lens, light,
               grade, texture, angle="eye", style_lead="as a film still from a Taiwanese campus music video filmed in 2001", extra=""):
    """t2i 组装 v2：官方顺序、单段散文、风格收尾。
    id_block: ID_M_2001 等常量（逐字复用）；wardrobe/face: 词表键或常量；pose: POSE_M 键；scene: SCENE 键。
    """
    wrd = WARDROBE_M.get(wardrobe, wardrobe)
    pse = POSE_M.get(pose, pose)
    scn = SCENE.get(scene, scene)
    parts = [
        "A %s of %s, %s." % (SHOT_SIZE[shot], id_block, CAM_ANGLE[angle]),
        "He wears %s." % wrd,
        "%s." % face.capitalize() if face else "",
        "He is %s, in %s." % (pse, scn),
        "%s." % LIGHT[light].capitalize(),
        "Shot on %s, %s, %s, %s." % (LENS[lens], GRADE[grade], TEXTURE[texture], style_lead),
    ]
    s = " ".join(x for x in parts if x)
    if extra:
        s += " " + extra
    return s

def build_video(shot, angle, move, id_block, action, scene, light, grade, texture,
                seconds=5, aspect="16:9"):
    """[已废弃为薄封装] 保留兼容旧脚本；新代码用 build_h3_i2va / build_seedance。"""
    return build_h3_i2va(shot, angle, move, id_block, action, scene, light, grade,
                         texture, seconds, aspect)

# ---- v1.2 双轨视频组装（官方口径分家·H3 本地 vs Seedance 云端）----
# 根因（H3 官方 README 原话）："H3-Context-IR is critical to the quality of the final output"
# —— Context-IR 未开源，本地直跑必须自己写官方结构化长文（自担预处理职责）。

H3_ALIGN_LINE = ("For the target video, at 0.00 seconds into the target video, "
                 "<Picture 1> (from [Shot 1]) is fully referenced.")

def build_h3_i2va(shot, angle, move, id_block, action, scene, light, grade, texture,
                  seconds=6, aspect="16:9", soundscape="", music="N/A (song laid in post)"):
    """本地 MiniMax-H3 I2VA 官方三字段结构：
    首行对齐指令 → integrated_multimodal_description（首帧锚定→action onset→development→reaction）
    → overall_soundscape → non_diegetic_music（MV 后期贴歌写 N/A 防音轨打架）。"""
    desc = ("%s, %s. %s. %s. %s, %s." % (SHOT_SIZE[shot], CAM_ANGLE[angle],
             CAM_MOVE[move], action[0].upper() + action[1:], SCENE.get(scene, scene),
             LIGHT[light].capitalize()))
    desc += " %s, %s. Character identity, clothing, colors, key objects and spatial relationships remain consistent." % (GRADE[grade], TEXTURE[texture])
    return (H3_ALIGN_LINE + " integrated_multimodal_description: " + desc
            + " overall_soundscape: " + (soundscape or "quiet room tone with faint air and fabric movement")
            + " non_diegetic_music: " + music
            + (" About %.1f seconds, %s aspect." % (float(seconds), aspect)))

# Seedance 官方约束句（火山官方原文口径——lint 对 seedance 模式放行官方否定形）
SEEDANCE_GUARD = ("\u5168\u5c40\u7ea6\u675f\uff1a\u4eba\u7269\u9762\u90e8\u7a33\u5b9a\u4e0d\u53d8\u5f62\uff0c"
                  "\u52a8\u4f5c\u81ea\u7136\u6d41\u7545\uff0c\u65e0\u5361\u987f\u65e0\u95ea\u70c1\uff1b"
                  "\u4fdd\u6301\u65e0\u5b57\u5e55\uff0c\u4e0d\u8981\u751f\u6210Logo\u6c34\u5370\u3002")

def build_seedance(shot_cn, move_cn, subject_tag, action_cn, scene_cn, light_cn, style_cn, quality_cn="4K\u9ad8\u6e05\u753b\u8d28"):
    """云端 Seedance（generate_video seedance2）官方八要素中文公式：
    精准主体+动作细节+场景环境+光影色调+镜头运镜+视觉风格+画质+约束条件。
    单镜单运镜红线；禁精确秒数时间戳（与 H3 相反）；低缓连续小动作优先。"""
    body = ("%s\u3002%s\u3002%s %s\u3002%s\u3002%s\u3002%s\u3002%s\u3002%s"
            % (shot_cn, move_cn, subject_tag, action_cn, scene_cn,
               light_cn, style_cn, quality_cn, SEEDANCE_GUARD))
    return body

def build_edit(change, keep, style_after=""):
    """Qwen-Edit 三段式（官方口径）：一句直接具体改动+保持项（正面列举）。
    change 例: "Change only the hairstyle to the heavy straight fringe shown in picture 2."
    keep  例: "Keep identical face shape and head angle, identical eyes and gaze, identical nose, mouth and jawline, identical skin with natural 35mm film grain and pores."
    """
    s = change + " " + keep
    if style_after:
        s += " " + style_after
    return s

# ================= 4. 自检 =================
if __name__ == "__main__":
    demo = build_shot(
        shot="hs", id_block=ID_M_2001, wardrobe="uniform", face=FACE_M_2001,
        pose="window_lean", scene="corridor", lens="85", light="window",
        grade="nost", texture="film_day", angle="eye",
    )
    print("[v1.1 official-order demo]")
    print(demo)
    print("words:", len(demo.split()))
    print("lint:", lint(demo))
    demo_v = build_video(shot="cu", angle="low", move="pushin", id_block=ID_M_2001,
                         action="pressing a reed stylus into a wet clay tablet",
                         scene="tablet", light="flame", grade="mono", texture="film_night")
    print("\n[video demo]")
    print(demo_v)
    print("lint:", lint(demo_v, mode="video"))
    old = ("The same young man in every image: NOT a Korean idol, no K-pop styling, no makeup, "
           "no glossy grooming, no slim trendy fashion. Absolutely no readable modern text, no typography.")
    print("\n[autofix demo] ->", autofix(old))
