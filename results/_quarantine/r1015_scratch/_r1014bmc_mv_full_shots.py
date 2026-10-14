# -*- coding: utf-8 -*-
# mv_full_shots.py - 爱在西元前 全曲镜头总表 v1（CEO令 10-10 20:5x「赶紧跑成品MV」）
# 窗口=歌绝对时间(whisper 2026-10-10 本机实测·501词)·film=song 对齐·0-234.25
# 权威=30s-立意案-v4-定稿（立意/硬律/因果链/注视链/灯灭字存）+ v4.5 变速律 + v4.4 克制做旧律
# 结构律=重演律：主歌2repeat/副歌3 复用已产镜头（「一切又重演」=同素材重归+微差新镜）
# 人物律=现代她 HER20·刻字者 ID_M_2001_BONE+scribe+厚刘海压眉（眉眼ID块=长版资产此片启用）·女神=巴比伦西亚面孔白裙+盘蛇臂环（全片版专属记忆点）
# 全片唯一叠化=T桥金字（承 30s 正典）·其余全硬切·禁白光转场·零冷色·禁看镜头
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "prompt-writing-spec-v1", "patched-scripts"))
import prompt_lexicon as LX

# ---- 光照块扩展（承 kf_fix2_fleet 正典 + 全曲新场景） ----
LX.LIGHT["torch"] = ("fat bundles of a dozen charcoal-blackened reed stems lashed around short thick cores with corded linen burn in cast bronze sconce bowls on thick bronze brackets, each swollen pitch-soaked wrapped head carrying a broad low fan of pure amber-gold flame with smoky yellow tips, the sooty charred wrapping and individual reed stems clearly readable, chiaroscuro with the far shadows lifted to warm film-base brown")
LX.LIGHT["torch_side"] = ("a thick reed-bundle torch wedged in a cast bronze sconce bowl at the lower frame edge throws raking side-backlight at 2000K across the stone, wedge-cut grooves catching the warm light one band at a time while the rest stays matte black")
LX.LIGHT["torch_off"] = ("unseen torchlight from beyond the frame edge throws raking side-backlight at 2000K across the stone, wedge-cut grooves catching the warm light one band at a time while the rest stays matte black")
LX.LIGHT["case"] = ("the glass display case is lit from within by warm tungsten halogen at 3000K, a golden amber pool in the surrounding darkness, her skin and the stone both kept in warm tones, the shadows tinted warm brown, glass reflections kept in warm gray")
LX.LIGHT["aisle_dim"] = ("warm tungsten case lights at 3000K dim one by one down the aisle, the last golden amber pool clinging to the stone")
LX.LIGHT["glyph"] = ("the wedge marks are self-lit in deep gold, their glow blooming softly through warm haze against black that carries visible 35mm film grain")
LX.LIGHT["hall_night"] = ("a dark museum hall after closing, one glass display case at the far end holding a single warm tungsten pool at 3000K, the long aisle floor catching a faint amber sheen, everything else warm film-base brown fading to black")
LX.LIGHT["row_wake"] = ("a row of glass display cases waking one after another in warm tungsten halogen at 3000K, golden pools marching down the dark hall, dust motes drifting in the lit air")
LX.LIGHT["god_smoke"] = ("a life-size carved goddess figure standing in drifting warm smoke, backlit by torch pools at 2000K, amber light breathing around her white robe, every tone kept warm gold and brown")
LX.LIGHT["crowd_dim"] = ("dim museum evening light, blurred visitor silhouettes in the foreground, a single warm tungsten case light at 3000K isolating her, everything in warm amber and brown")
LX.LIGHT["plain_night"] = ("a dark alluvial plain at night under a low warm amber sky glow near the horizon, faint torchlight pools in the far distance, warm film-base brown darkness")
LX.LIGHT["dying_fire"] = ("a reed-bundle torch burning low in its bronze bowl, the flame shrunken to a small amber tongue, embers pulsing dull orange in the black")
LX.LIGHT["window_flip"] = ("torchlight at 2000K blooming into overexposure at frame center, the amber light flooding out until the museum case lights at 3000K surface through the glare")

STYLE_LEAD = "as a film still from a 2001 Taiwanese music video"
HER20 = ("a young Taiwanese woman of 2001, a softly rounded youthful face with full cheeks, "
         "large dark eyes, a small nose, long straight black hair with a full blunt fringe, "
         "wearing a loose oatmeal chunky-knit wool sweater with a soft round neckline and long "
         "sleeves reaching past her wrists, relaxed low-rise bootcut dark denim jeans, flat "
         "canvas shoes and a simple shoulder bag, un-fitted relaxed 2001 Taipei street style")
HIM = ("a 20-year-old Taiwanese student with heavy-lidded monolid eyes, a thick lower lip, "
       "softly rounded cheeks, a flat round nose tip, a blunt rounded jaw and natural "
       "unretouched skin with visible pores, his thick black fringe lying flat over his "
       "eyebrows, wearing a rough hand-woven undyed linen tunic with a simple rope belt")
BANDS = ("stacked horizontal bands of hand-cut cuneiform wedge marks, each sign a tight cluster "
         "of wedge strokes with clean triangular heads and tapering tails, thin ruled lines "
         "between rows, matte black rock with visible tool marks and fine stone grain")
STELE = ("a tall flat rounded-top slab stele of polished black basalt, straight sides about "
         "three times taller than wide, the top fifth a carved relief band, below it more than "
         "twenty horizontal cuneiform registers stacked to the base")
GODDESS = ("a life-size stone carving of a young Babylonian goddess with deep-set eyes, a high "
           "brow and a straight nose, wearing a flowing white robe and a coiled-snake armband, "
           "her hands folded at her waist")

def kf(shot, angle, subject, light, lens="35", extra=""):
    s = "A %s of %s, %s. %s. Shot on %s, %s, %s, %s." % (
        LX.SHOT_SIZE[shot], subject, LX.CAM_ANGLE[angle],
        LX.LIGHT[light].capitalize(), LX.LENS[lens],
        LX.GRADE["mono"], LX.TEXTURE["film_night"], STYLE_LEAD)
    return s + (" " + extra if extra else "")

I2V_TAIL = ("Warm amber monochrome grade with deep crushed shadows, visible 35mm film grain. "
            "Restrained continuous motion, camera and subject motion only.")

def i2v(size_angle, motion, content):
    return ("Single continuous take at 24fps, 16:9. %s; the camera %s. %s. "
            % (size_angle, motion, content)) + I2V_TAIL

# ================= NEW SHOTS（44 镜） =================
# (id, t0, t1, speed, kf_prompt, i2v_prompt)
NEW = [
    # ---- 前奏 0-17.5（她入馆·世界呼吸）----
    ("INT1_hall_breath", 0.00, 3.50, 0.85,
     kf("med", "eye", "a dark museum hall after closing seen from the entrance, a single glass display case lit warm at the far end of the long aisle", "hall_night", lens="35"),
     i2v("A medium shot at eye level", "holds a static locked-off shot with only the distant case light breathing slowly brighter and dimmer",
         "A dark museum hall after closing, a single warm amber display case far down the aisle, the light breathing, dust motes drifting in the lit air")),
    ("INT2_row_wake", 3.50, 7.50, 0.92,
     kf("wide", "eye", "a row of glass display cases in a dark museum hall waking one after another, warm pools marching into the distance, her small distant silhouette just inside the entrance", "row_wake", lens="35"),
     i2v("A wide shot at eye level", "pushes in with small amplitude at slow speed",
         "A row of museum display cases lighting up one after another down a dark hall, warm amber pools marching into the distance, a small distant silhouette of a young woman standing just inside the entrance")),
    ("INT3_her_walk", 7.50, 11.50, 0.90,
     kf("med", "eye", "%s seen from behind mid-stride walking down the aisle between dim display cases, rain-wet hair ends and a faint damp sheen on her shoulder" % HER20, "row_wake", lens="50"),
     i2v("A medium shot at eye level", "tracks backward with small amplitude at slow speed, matching her pace",
         "A young woman with long black hair and a full blunt fringe seen from behind, walking down a dark museum aisle between dim amber cases, her slow steps carrying her deeper into the hall")),
    ("INT4_first_reflection", 11.50, 14.60, 0.95,
     kf("cu", "eye", "her face reflected faintly on the dark glass of a display case for the first time, the reflection floating over stacked carved cuneiform bands inside, her eyes on the stone", "case", lens="50"),
     i2v("A close-up at eye level", "holds a static shot, only her reflected gaze settling and a faint breath of the case light",
         "The faint reflection of a young woman's face floating on dark museum glass, overlapping carved cuneiform bands lit warm amber inside the case, her reflection slowly steadying onto the stone")),
    ("INT5_approach", 14.60, 17.50, 0.88,
     kf("cu", "eye", "inside the case, a broken slab of polished black basalt carved with %s, the carved bands lit warm, the relief crown just surfacing from the amber pool" % BANDS, "case", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at slow speed",
         "A broken slab of polished black basalt carved with stacked cuneiform bands inside a warm amber display case, the carved marks growing closer and clearer as the light breathes")),

    # ---- 主歌2 47.5-77.34（巴比伦世界展开）----
    ("N01_war_relief", 47.50, 50.52, 1.05,
     kf("cu", "eye", "a carved battle-relief band running along a mud-brick wall: ranks of bowmen with drawn bows and a file of spearmen, wedge-cut stone figures surfacing under raking firelight", "torch_off", lens="50"),
     i2v("A close-up at eye level", "holds locked-off while unseen torchlight rakes slowly across the band",
         "A carved stone battle relief of bowmen and spearmen along a mud-brick wall, amber torchlight crawling across the wedge-cut figures rank by rank, fine dust drifting")),
    ("N02_crowd_her", 50.52, 54.22, 0.92,
     kf("med", "eye", "%s standing still among blurred museum visitors passing in the foreground, her face the only sharp and lit presence, her eyes on a distant case" % HER20, "crowd_dim", lens="85"),
     i2v("A medium shot at eye level", "pushes in with small amplitude at slow speed past the blurred passers-by",
         "A young woman with long black hair and a full blunt fringe standing still in a dim museum crowd, blurred visitors drifting past in the foreground, her calm lit face holding steady between them")),
    ("N03_goddess_pass", 54.22, 58.44, 0.95,
     kf("med", "eye", "%s in a museum alcove, and beside her in frame a second figure: %s, the carved goddess and the living young woman sharing the warm air" % (GODDESS, HER20), "god_smoke", lens="50"),
     i2v("A medium shot at eye level", "tracks laterally with small amplitude at slow speed",
         "A carved stone goddess in a warm amber alcove of drifting smoke, a young woman with long black hair and a full blunt fringe passing slowly before her, the goddess holding still as the smoke breathes")),
    ("N04_river_marks", 58.44, 61.98, 0.85,
     kf("cu", "high", "a wide carved band across the black basalt: a formal river rendered in long wavy wedge-lines, boats as small wedges on the current, the carved water catching a slow run of firelight", "torch_off", lens="50"),
     i2v("A close-up from a high angle", "tilts down with medium amplitude at slow speed",
         "A carved river band of long wavy wedge-lines across black basalt, the amber light running slowly downstream along the carved current, boats as small wedges floating on the lines")),
    ("N05_dead_language", 61.98, 68.86, 0.85,
     kf("cu", "eye", "%s filling the frame edge to edge, dense and unreadable, centuries of registers stacked and interlocking" % BANDS, "torch_off", lens="50"),
     i2v("A close-up at eye level", "drifts laterally with small amplitude at very slow speed along the stacked bands",
         "Dense unreadable cuneiform registers filling the frame, the camera sliding slowly along band after band of carved wedges, amber light pooling in the grooves, dust drifting")),
    ("N06_poem_light", 68.86, 74.60, 0.90,
     kf("med", "low", "%s with the torches behind sinking low in their bronze bowls, the carved registers reading like lines of verse as the amber light gathers into one beam across the middle bands" % STELE, "torch", lens="50"),
     i2v("A medium shot from a low angle", "pulls out with small amplitude at slow speed",
         "A tall black basalt stele in a Babylonian hall, the torches behind burning low, the amber light gathering into a single beam across the carved registers so the rows read like lines of verse, the hall darkening around them")),
    ("N07_fire_breath", 74.60, 77.34, 1.00,
     kf("ecu", "eye", "a reed-bundle torch head burning wide in its bronze bowl, pure amber-gold flame fanning against blackness, soot and embers", "torch", lens="50"),
     i2v("An extreme close-up at eye level", "holds locked-off as the flame breathes and swells",
         "A fat reed-bundle torch burning in a cast bronze bowl, the broad amber flame breathing and swelling until the glow fills the frame, embers drifting up through the heat")),

    # ---- 副歌1 77.34-108.22（爱的证据链）----
    ("C01_carver_face", 77.34, 80.18, 0.90,
     kf("cu", "eye", "%s in profile at his work, a half-cut row of large fresh wedges before him, his heavy-lidded eyes lifting toward something beyond the frame edge, firelight on the linen weave and the fringe over his brows" % HIM, "torch_side", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at very slow speed",
         "A young scribe in a rough linen tunic, his heavy-lidded eyes lifting from his half-cut row of cuneiform wedges toward something beyond the frame, warm torchlight breathing on his face and the black basalt")),
    ("C02_sand_bury", 80.18, 83.56, 0.95,
     kf("med", "eye", "%s half-drowned under drifting wind-blown sand, the upper registers already gone, the fresh low band still catching the last light" % STELE, "torch_off", lens="50"),
     i2v("A medium shot at eye level", "holds locked-off as fine sand drifts steadily across the stone",
         "A tall black basalt stele half-buried under drifting wind-blown sand, the upper carved registers drowning grain by grain while the lowest fresh band holds the last amber light")),
    ("C03_dig_reveal", 83.56, 87.74, 1.00,
     kf("cu", "high", "a soft brush sweeping across a buried carved band, pale dust lifting from the wedge marks, the glyphs surfacing stroke by stroke under a warm work-lamp glow", "torch_off", lens="50"),
     i2v("A close-up from a high angle", "holds locked-off while the brush works across the band",
         "A soft brush sweeping dusty sand off a buried cuneiform band stroke by stroke, pale dust lifting through a warm amber glow, the carved wedges surfacing one by one")),
    ("C04_words_alive", 87.74, 91.06, 0.88,
     kf("cu", "eye", "a single low register of large crisp wedges, the fresh band clean and pale-edged, every stroke legible in the still warm light", "torch_off", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at very slow speed",
         "A single band of large crisp cuneiform wedges on black basalt, every stroke clean and legible in the warm light, the camera easing closer as the glow breathes over the pale cuts")),
    ("C05_flame_gap", 91.06, 92.62, 1.00,
     kf("cu", "eye", "a bronze sconce bowl with a low flame curled inside it, the hall behind in blackness", "torch", lens="85"),
     i2v("A close-up at eye level", "holds locked-off, the small flame shivering",
         "A low flame curled inside a cast bronze bowl, shivering amber-gold against the dark, a thread of smoke rising")),
    ("C06_forever_cut", 92.62, 95.22, 1.05,
     kf("ecu", "eye", "the bronze chisel seated at the head of the last large wedge in the fresh row, the wooden mallet frozen mid-descent, pale stone dust hanging in the firelight", "torch_side", lens="50"),
     i2v("An extreme close-up at eye level", "holds locked-off, the strike landing early in the take",
         "A bronze chisel biting the head of the last large wedge in a fresh row on black basalt, the strike landing early in the take, pale dust leaping from the cut in the torchlight")),
    ("C07_stele_sink", 95.22, 100.14, 0.92,
     kf("wide", "low", "%s alone on a dark alluvial plain, the ground taking it band by band, the sky a low warm amber glow at the horizon" % STELE, "plain_night", lens="35"),
     i2v("A wide shot from a low angle", "pulls out and cranes up with steady amplitude at slow speed",
         "A tall black basalt stele standing alone on a dark plain under a low warm amber horizon glow, the camera retreating and rising as the stone shrinks into the darkness of the land")),
    ("C08_strike_burst", 100.14, 102.88, 1.10,
     kf("ecu", "eye", "the mallet head meeting the bronze chisel, the fresh wedge splitting clean, coarse chips and dust bursting off the cut", "torch_side", lens="50"),
     i2v("An extreme close-up at eye level", "holds locked-off, the strike bursting early in the take",
         "A wooden mallet striking a bronze chisel into black basalt, the blow landing early in the take, coarse stone chips bursting off the fresh cut through the amber torchlight")),
    ("C09_oath_weather", 102.88, 108.22, 0.87,
     kf("cu", "eye", "the carved surface long after: the wedges rounded by centuries of wind, thin cracks running through the registers like dry riverlines, the memory of the strokes still legible" , "torch_off", lens="50"),
     i2v("A close-up at eye level", "drifts laterally with small amplitude at very slow speed",
         "A weathered cuneiform band, the wedges rounded by centuries of wind and crossed by thin cracks like dry riverlines, the amber light sliding slowly across the worn strokes")),

    # ---- 主歌2 重演 110.52-138.56（千年后·微差）----
    ("R01_war_later", 110.52, 114.70, 0.95,
     kf("cu", "eye", "the same carved battle-relief band a thousand years later: the bowmen and spearmen softened and darkened, the wedge figures half-lost in the grain of the stone", "torch_off", lens="50"),
     i2v("A close-up at eye level", "holds locked-off as a weaker light rakes the band",
         "A weathered stone battle relief of bowmen and spearmen, the carved figures softened and darkened by age, a weak amber glow crawling slowly across them and fading again")),
    ("R02_she_turns", 114.70, 118.46, 0.90,
     kf("med", "eye", "%s among the blurred crowd, this time her head turned back over her shoulder toward the display cases behind her, her eyes finding a far stone in the dark" % HER20, "crowd_dim", lens="85"),
     i2v("A medium shot at eye level", "holds a near-static shot as she turns her head slowly back over her shoulder",
         "A young woman with long black hair and a full blunt fringe among blurred museum visitors, her head turning slowly back over her shoulder toward the dark display cases, the warm light holding her face")),
    ("R03_goddess_dim", 118.46, 122.82, 0.90,
     kf("med", "eye", "%s with the smoke thinned to threads and the torch bowls behind burning low, the carved face holding the last of the amber" % GODDESS, "god_smoke", lens="50"),
     i2v("A medium shot at eye level", "pushes in with small amplitude at very slow speed",
         "A carved stone goddess in a thinning drift of warm smoke, the torches behind her burning low, her carved face holding the last amber light as the dark closes in")),
    ("R04_river_dry", 122.82, 126.32, 0.88,
     kf("cu", "high", "the carved river band dried: the wavy wedge-lines cracked and shallow, the little boats beached on the lines, the firelight gone to a faint sheen", "torch_off", lens="50"),
     i2v("A close-up from a high angle", "tilts down with medium amplitude at slow speed",
         "A dried carved river band on black basalt, the wavy wedge-lines cracked and shallow with little wedge boats beached on them, a faint amber sheen passing over the dead current")),
    ("R05_gold_threads", 126.32, 131.72, 0.85,
     kf("cu", "eye", "the buried registers in darkness, only the thin edges of the wedges catching thin gold lines of light, the rest sunk in warm black", "glyph", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at very slow speed",
         "Cuneiform registers sunk in warm darkness, only the thin edges of the carved wedges catching fine gold lines of light, the glow breathing slowly along the strokes")),
    ("R06_museum_verse", 131.72, 138.56, 0.92,
     kf("med", "eye", "the same carved registers now inside a museum case, the warm tungsten light laying the rows out like lines of verse, her faint reflection resting at the glass edge", "case", lens="50"),
     i2v("A medium shot at eye level", "pulls out with small amplitude at slow speed",
         "Carved cuneiform registers inside a warmly lit museum case, the rows laid out like lines of verse in the amber light, a faint young woman's reflection resting at the glass edge as the view eases back")),

    # ---- 副歌2 141.76-172.50（注视链高潮·古今叠印）----
    ("D01_carver_words", 141.76, 144.56, 0.90,
     kf("cu", "ots", "from over his shoulder, the half-finished fresh row of large wedges and his weathered hand resting on the chisel, %s at the frame edge in profile" % HIM, "torch_side", lens="50"),
     i2v("A close-up over the shoulder", "holds locked-off, his hand easing the chisel forward",
         "Over a young scribe's shoulder: his weathered hand resting a bronze chisel at the next large wedge in a fresh row on black basalt, the torchlight breathing on his linen sleeve and fringe")),
    ("D02_she_reads", 144.56, 147.84, 0.88,
     kf("cu", "eye", "her face close to the glass reading the low register intently, the warm case glow on her profile, the carved words blurred just beyond her reflection", "case", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at slow speed",
         "A young woman's face close to museum glass, reading a low carved register intently, the warm amber case glow on her profile, her faint reflection resting over the blurred words")),
    ("D03_two_worlds", 147.84, 152.14, 0.85,
     kf("med", "eye", "the display case glass carrying both worlds at once: her dark reflected profile in the foreground, and behind the glass the same carved slab wrapped in drifting Babylonian firelight and smoke, the two lights breathing against each other", "case", lens="50"),
     i2v("A medium shot at eye level", "pushes in with small amplitude at very slow speed",
         "A museum display case glass holding two worlds: a young woman's dark reflected profile in the foreground, and behind the glass the carved slab wrapped in drifting amber firelight and smoke, the two lights slowly breathing toward each other")),
    ("D04_her_brush", 152.14, 155.40, 0.95,
     kf("cu", "high", "her hand with the modern sleeve guiding a soft brush across a carved band, dust lifting in the warm lamplight, the wedge marks surfacing under her fingers", "torch_off", lens="50"),
     i2v("A close-up from a high angle", "holds locked-off as the brush sweeps once across the band",
         "A young woman's hand with a modern knit sleeve guiding a soft brush across a carved cuneiform band, pale dust lifting through warm lamplight, the wedges surfacing under her fingers")),
    ("D05_words_warm", 155.40, 159.66, 0.87,
     kf("cu", "eye", "the low register of large wedges inside the case, crisp and complete now, the warm light laying every stroke open", "case", lens="50"),
     i2v("A close-up at eye level", "holds a static shot, the case light breathing",
         "A complete low register of large crisp cuneiform wedges inside a warm museum case, the amber light breathing slowly over every stroke, dust motes drifting")),
    ("D06_chisel_fingertip", 159.66, 163.04, 0.90,
     kf("cu", "eye", "a double exposure in one frame: the ancient bronze chisel head at the left edge biting a wedge, and her fingertip resting on the glass at the right edge over the same carved line, both lit in the same warm amber", "torch_off", lens="50"),
     i2v("A close-up at eye level", "holds locked-off, the two touches breathing in the same light",
         "Two touches in one warm frame: an ancient bronze chisel biting a wedge at the left edge, and a young woman's fingertip resting on dark museum glass over the same carved line at the right, the light breathing on both")),
    ("D07_oath_river", 163.04, 167.22, 0.92,
     kf("cu", "eye", "the weathered registers crossed by a long crack running down the stone like a dry river, the crack catching a thin gold seam of light", "glyph", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at slow speed along the crack",
         "A weathered cuneiform wall crossed by a long crack running down like a dry river, a thin gold seam of light sliding slowly along the crack through the carved rows")),
    ("D08_world_flip", 167.22, 172.50, 0.95,
     kf("med", "eye", "the carved slab wrapped in swelling torch overexposure, and inside the amber glare the faint geometry of the modern museum case surfacing, two rooms bleeding into one", "window_flip", lens="50"),
     i2v("A medium shot at eye level", "holds locked-off as the amber light swells into overexposure and settles",
         "A carved stone slab wrapped in amber torchlight that swells into overexposure, and inside the glare the straight lines of a modern museum case slowly surfacing, the two rooms bleeding into one warm light")),

    # ---- Bridge 172.5-187.26（他的疲倦）----
    ("B01_weary", 172.50, 177.00, 0.85,
     kf("cu", "eye", "%s sunk onto his stool before the unfinished row, the mallet and chisel down at his side, his heavy-lidded eyes low, the torch burning thin", "torch_side", lens="50"),
     i2v("A close-up at eye level", "holds locked-off as his shoulders settle lower and the flame thins",
         "A young scribe sunk onto his stool before an unfinished row of cuneiform wedges, his tools down at his side, his heavy-lidded eyes low, the thin torch flame slowly failing in its bronze bowl")),
    ("B02_far_home", 177.00, 181.50, 0.90,
     kf("wide", "eye", "%s standing at a mud-brick doorway looking out at a dark sleeping land, distant fires small on the horizon, the night air moving his fringe", "plain_night", lens="35"),
     i2v("A wide shot at eye level", "pulls out with small amplitude at slow speed",
         "A young man in a rough linen tunic standing in a mud-brick doorway looking out over a dark sleeping plain, small distant fires on the warm horizon, the night air moving his hair as the view eases back")),
    ("B03_last_look", 181.50, 184.08, 0.88,
     kf("cu", "eye", "his hand resting flat on the unfinished row of wedges, the half-cut sign under his palm, the torch low behind him", "torch_side", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at very slow speed",
         "A young man's weathered hand resting flat on an unfinished row of cuneiform wedges, a half-cut sign under his palm, the low torch behind him breathing its last light over the stone")),
    ("B04_embers", 184.08, 187.26, 1.00,
     kf("ecu", "eye", "the torch bowl with the flame gone, only embers pulsing dull orange in the soot, thin smoke standing", "dying_fire", lens="50"),
     i2v("An extreme close-up at eye level", "holds locked-off as the embers pulse and dim",
         "A cast bronze torch bowl with the flame gone, dull orange embers pulsing fainter in the soot, a thin thread of smoke standing over them")),

    # ---- 副歌3 终峰（2 新镜）----
    ("E03_gaze_meet", 197.52, 200.80, 0.85,
     kf("cu", "eye", "the dark glass carrying her profile in the foreground and behind it a faint male silhouette in linen surfacing in the amber firelight, his heavy-lidded gaze finding hers across the glass, two edges of one reflection", "case", lens="50"),
     i2v("A close-up at eye level", "holds a near-static shot as the two reflections slowly settle toward each other",
         "Dark museum glass carrying a young woman's warm-lit profile in the foreground, and behind it a faint male silhouette in rough linen surfacing in the amber firelight, his gaze finding hers across the glass, both reflections breathing toward each other")),
    ("E04_replay_faces", 212.66, 219.84, 0.87,
     kf("med", "eye", "the carved slab centered in blackness, and over its surface a slow double silhouette: her modern profile dissolving into the outline of a Babylonian woman with a coiled-snake armband, one shape easing into the other in the gold haze", "glyph", lens="50"),
     i2v("A medium shot at eye level", "holds locked-off while the two silhouettes slowly exchange through each other",
         "A carved stone slab centered in warm blackness, a modern young woman's profile dissolving slowly into the outline of a Babylonian woman with a coiled-snake armband, one silhouette easing into the other through the gold haze, everything still and slow")),

    # ---- 尾声 219.84-234.25（灯灭字存定格收）----
    ("Z01_words_alone", 219.84, 224.00, 0.85,
     kf("cu", "eye", "the empty museum hall in darkness, the unattended case still holding the carved band in a faint deep-gold glow, the wedges self-lit and breathing softly", "glyph", lens="50"),
     i2v("A close-up at eye level", "holds a static shot, the carved marks lit faintly and breathing",
         "An empty dark museum hall with one unattended case, the carved cuneiform band inside lit faint deep gold on its own, the wedge strokes breathing slowly in the blackness, dust motes drifting")),
    ("Z03_lights_out", 227.50, 230.50, 0.90,
     kf("wide", "eye", "the long aisle of the hall with the case lights going out one after another down the row, the last amber pool around the carved slab holding on", "aisle_dim", lens="35"),
     i2v("A wide shot at eye level", "holds locked-off as the row of case lights dims one by one down the hall",
         "A dark museum aisle with warm case lights going out one after another down the row, each amber pool shrinking in turn, the last pool holding around a broken carved slab at the far end")),
    ("Z04_glyph_remains", 230.50, 234.25, 0.96,
     kf("cu", "eye", "the last light gone, only the carved wedge band remaining as a faint gold etching on the darkness, the strokes still legible, everything else black", "glyph", lens="50"),
     i2v("A close-up at eye level", "pushes in with small amplitude at very slow speed until the gold strokes hold still",
         "A carved cuneiform band remaining as a faint deep-gold etching on pure darkness, the wedge strokes still legible, the glow settling slowly until the marks hold still in the black")),
]

# ================= REUSE（已产/复用件·src=cloud-v4 源文件名） =================
REUSE = [
    # 30s 正典段（17.5-47.5·v4.5 速度原样）
    ("S1_fire_wake",  17.50, 21.90, 0.85, "KF1_fire_wake"),
    ("S2_sweep",      21.90, 25.90, 0.95, "KF2_sweep"),
    ("S3_stele",      25.90, 29.40, 1.06, "KF3_stele"),
    ("S4_crown",      29.40, 31.14, 1.16, "KF4_crown"),
    ("S5_columns",    31.14, 34.74, 1.00, "KF5_columns"),
    ("S6_chisel",     34.74, 36.92, 1.05, "KF6_chisel"),   # 段内burst=装配脚本按S6_SEGS处理
    ("S7_hall",       36.92, 38.82, 0.82, "KF7_hall"),
    ("T_glyphs",      38.82, 40.22, 0.90, "KFT_glyphs"),   # 全片唯一叠化桥
    ("S8_case",       40.22, 42.22, 0.92, "KF8_case"),
    ("S9_profile",    42.22, 45.22, 0.87, "KF9_profile"),  # 金字层窗=词起42.78
    ("S10_walk",      45.22, 47.50, 0.96, "KF10_walkaway"), # 全片版此段=走·不冻结
    # 副歌3 重演（C 系复用）
    ("E01a_carver",   187.26, 190.00, 0.90, "C01_carver_face"),
    ("E01b_sand",     190.00, 193.12, 0.95, "C02_sand_bury"),
    ("E02a_dig",      193.12, 197.52, 1.00, "C03_dig_reveal"),
    ("E04a_words_warm",200.80, 205.10, 0.88, "D05_words_warm"),
    ("E05_stele_sink",205.10, 208.08, 0.92, "C07_stele_sink"),
    ("E06_strike",    208.08, 212.66, 0.92, "C08_strike_burst"),
    # 间奏复用火光帧
    ("R07_flame",     138.56, 141.76, 1.00, "C05_flame_gap"),
    ("C09b_flame",    108.22, 110.52, 1.00, "C05_flame_gap"),
    # 尾声走远=重演（S10 源复用·取后半段行进）
    ("Z02_walkaway",  224.00, 227.50, 0.92, "KF10_walkaway"),
]

# S9 金字层（全片版歌绝对窗·承 30s 正典词起字起词尽字散）
TXT_IN_ST, TXT_IN_D = 42.78, 0.50
TXT_OUT_ST, TXT_OUT_D = 44.62, 0.45
S6_SEGS = [(0.0, 0.90, 1.05), (0.945, 1.28, 1.38)]   # 段内burst（承 v4.5）
XF_T1, XF_T2 = 38.42, 40.22   # T 桥两处叠化点（歌绝对）
FILM_END = 234.25

if __name__ == "__main__":
    ok = True
    for row in NEW:
        sid, t0, t1, v, k, iv = row
        for label, p, mode in (("kf", k, "t2i"), ("i2v", iv, "video")):
            hits = LX.lint(p, mode=mode)
            if hits:
                ok = False
                print("LINT-FAIL", sid, label, hits)
    ids = [r[0] for r in NEW] + [r[0] for r in REUSE]
    assert len(ids) == len(set(ids)), "DUP SHOT ID"
    # 窗口连续性校验（NEW+REUSE 按 t 排序须铺满 0-234.25 无缝无叠）
    allw = sorted([(r[1], r[2], r[0]) for r in NEW] + [(r[1], r[2], r[0]) for r in REUSE])
    gaps = [(a, b) for (a, b) in zip(allw, allw[1:]) if abs(a[1] - b[0]) > 0.011]
    if allw and (abs(allw[0][0]) > 0.011 or abs(allw[-1][1] - FILM_END) > 0.011 or gaps):
        print("WINDOW GAPS:", gaps[:5], "head", allw[0][:2], "tail", allw[-1][:2]); ok = False
    print("SHOTS=%d NEW=%d REUSE=%d LINT+%s" % (len(ids), len(NEW), len(REUSE), "OK" if ok else "FAIL"))
