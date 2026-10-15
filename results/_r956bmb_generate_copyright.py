# -*- coding: utf-8 -*-
"""
Universal software copyright application material generator (fleet-portable).
Generates: source code PDF (60 pages, 50 lines/page), design document PDF, form guide PDF.
Usage: python generate_copyright.py [key1 key2 ...]   (no args = all keys)

Fleet rules (CEO order O-20261010-1330):
- Output always lands in <this script's folder>/<out_dir>, committed via git -> synced fleet-wide.
- src resolution: src_rel is tried against every candidate repo/project root (bm-a / bm-c / K-machine layouts).
- Projects whose source is not on the current machine: source steps are skipped with a notice,
  but design doc + form guide PDFs still render if their .md files exist.
- 源程序量 in 申请表填写指南.md is auto-updated from the real measurement whenever source is collected.
"""
import os, sys, glob, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)

# Candidate roots for src_rel resolution (bm-a / bm-c / K-machine layouts all covered)
SRC_ROOTS = [
    os.path.join(REPO, 'gaming', 'MiniGame'),
    os.path.join(REPO, 'gaming'),
    os.path.join(REPO, 'projects'),
    os.path.normpath(os.path.join(REPO, '..', 'projects')),
    REPO,
    r'K:\Fluxgroup\MiniGame',
    r'K:\Fluxgroup\projects',
    r'K:\Fluxgroup\FluxGroup\gaming\MiniGame',
    r'C:\Fluxgroup\FluxGroup\gaming\MiniGame',
]

# Register fonts
pdfmetrics.registerFont(TTFont('SimSun', r'C:\Windows\Fonts\simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimHei', r'C:\Windows\Fonts\simhei.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', r'C:\Windows\Fonts\consola.ttf'))

# Project configurations.
# Fields: name_cn(软件全称) / name_short / name_en / version / src_rel(相对任意候选根) /
#         out_dir(可选,缺省={key}_{name_en}) / name_pending(可选,True=中文定名未定工作稿) / owner(归属军团机)
PROJECTS = {
    # ---------- A机=团结牛马军团 (bm-a) ----------
    "G09": {  # 吸嘟嘟 (G01 ledger 号; CEO 位标号 G09)
        "name_cn": "吸嘟嘟游戏软件", "name_short": "吸嘟嘟", "name_en": "GimmeAll", "version": "V1.0",
        "src_rel": "09_吸嘟嘟GimmeAll/GimmeAll/Assets", "owner": "A机",
    },
    "G11": {
        "name_cn": "摸鱼也升职游戏软件", "name_short": "摸鱼也升职", "name_en": "CrazyWorker", "version": "V1.0",
        "src_rel": "projects/G11_CrazyWorker/Assets/_Game", "owner": "A机",
    },
    "G15": {
        "name_cn": "萌宠开店啦游戏软件", "name_short": "萌宠开店啦", "name_en": "PetWorkCrew", "version": "V1.0",
        "src_rel": "projects/G15_PetWorkCrew/Assets/_Game", "owner": "A机",
    },
    "G16": {
        "name_cn": "我有一栋楼游戏软件", "name_short": "我有一栋楼", "name_en": "CrazyEstate", "version": "V1.0",
        "src_rel": "projects/G16_CrazyEstate/Assets/_Game", "owner": "A机",
    },
    "G19": {
        "name_cn": "我的小花园游戏软件", "name_short": "我的小花园", "name_en": "BloomHaven", "version": "V1.0",
        "src_rel": "projects/G19_BloomHaven/Assets/_Game", "owner": "A机",
    },
    "FluxVerse": {
        "name_cn": "超体宇宙城游戏软件", "name_short": "超体宇宙城", "name_en": "FluxVerse", "version": "V1.0",
        "src_rel": "FluxVerse/City/Assets", "owner": "A机",
    },
    "P01": {
        "name_cn": "提灯斩鬼游戏软件", "name_short": "提灯斩鬼", "name_en": "LanternSlayer", "version": "V1.0",
        "src_rel": "projects/P01_LanternReaper/Assets/_Game", "owner": "A机",
    },
    "P02": {
        "name_cn": "异界行者游戏软件", "name_short": "异界行者", "name_en": "FateGate", "version": "V1.0",
        "src_rel": "projects/P02_FateGate/Assets/_Game", "owner": "A机",
    },
    "P03": {
        "name_cn": "军师救我游戏软件", "name_short": "军师救我", "name_en": "StrategistDefense", "version": "V1.0",
        "src_rel": "projects/P03_CataclysmKeep/Assets/_Game", "owner": "A机",
    },
    "P04": {
        "name_cn": "这妖我收了游戏软件", "name_short": "这妖我收了", "name_en": "DemonTamer", "version": "V1.0",
        "src_rel": "projects/P04_ShanhaiSaga/Assets/_Game", "owner": "A机",
    },
    "P05": {
        "name_cn": "守夜人游戏软件", "name_short": "守夜人", "name_en": "NightWatch", "version": "V1.0",
        "src_rel": "projects/P05_FrozenDynasty/Assets/_Game", "owner": "A机",
    },
    "P06": {
        "name_cn": "调香师游戏软件", "name_short": "调香师", "name_en": "SongOfScents", "version": "V1.0",
        "src_rel": "projects/P06_SongOfScents/Assets/_Game", "owner": "A机",
    },
    "P07": {
        "name_cn": "捞个宝游戏软件", "name_short": "捞个宝", "name_en": "TreasureDive", "version": "V1.0",
        "src_rel": "projects/P07_SunkenMuseum/Assets/_Game", "owner": "A机",
    },
    "P08": {
        "name_cn": "奈何桥游戏软件", "name_short": "奈何桥", "name_en": "GhostMarshal", "version": "V1.0",
        "src_rel": "projects/P08_GhostMarshal/Assets/_Game", "owner": "A机",
    },
    # ---------- B机=银河牛马军团 (bm-c) ----------
    "G04": {
        "name_cn": "螺丝仙人游戏软件", "name_short": "螺丝仙人", "name_en": "ScrewOut", "version": "V1.0",
        "src_rel": "G04_ScrewOut/Assets/_Game", "owner": "B机",
    },
    "G05": {
        "name_cn": "爆护游戏软件", "name_short": "爆护", "name_en": "ReelRiot", "version": "V1.0",
        "src_rel": "G05_ReelRiot/Assets/_Game", "owner": "B机",
    },
    "G07": {
        "name_cn": "人从众游戏软件", "name_short": "人从众", "name_en": "MobTide", "version": "V1.0",
        "src_rel": "G07_MobTide/Assets/_Game", "owner": "B机",
    },
    "G08": {
        "name_cn": "开学啦游戏软件", "name_short": "开学啦", "name_en": "CrazyCampus", "version": "V1.0",
        "src_rel": "G08_CrazyCampus/Assets/_Game", "owner": "B机",
    },
    "G13": {
        "name_cn": "我想有个农场游戏软件", "name_short": "我想有个农场", "name_en": "CrazyFarm", "version": "V1.0",
        "src_rel": "G13_CrazyFarm/Assets/_Game", "out_dir": "G13_我想有个农场", "owner": "B机",
    },
    "G14": {
        "name_cn": "大不了开饭馆游戏软件", "name_short": "大不了开饭馆", "name_en": "CrazyRestaurant", "version": "V1.0",
        "src_rel": "G14_CrazyRestaurant/Assets/_Game", "out_dir": "G14_大不了开饭馆", "owner": "B机",
    },
    "G20": {
        "name_cn": "夜聊斋游戏软件", "name_short": "夜聊斋", "name_en": "MonsterInn", "version": "V1.0",
        "src_rel": "G20_MonsterInn/Assets/_Game", "owner": "B机",
    },
    "G26": {
        "name_cn": "归园田居游戏软件", "name_short": "归园田居", "name_en": "ExileFarm", "version": "V1.0",
        "src_rel": "G26_ExileFarm/Assets/_Game", "owner": "B机",
    },
    # ---------- C机=御湖湾牛马军团 (bm-b/K机) ----------
    "G02": {
        "name_cn": "旧物诊所游戏软件", "name_short": "旧物诊所", "name_en": "TimeRepairShop", "version": "V1.0",
        "src_rel": "TimeRepairShop/Assets/_Game", "out_dir": "G02_TimeRepairShop", "owner": "C机",
    },
    "G09Y": {
        "name_cn": "医院大当家游戏软件", "name_short": "医院大当家", "name_en": "CrazyHospital", "version": "V1.0",
        "src_rel": ["G09_CrazyHospital/Assets/_Game", "CrazyHospital/Assets/_Game"], "out_dir": "G09_医院大当家", "owner": "C机",
    },
    "G10": {
        "name_cn": "涨停板游戏软件", "name_short": "涨停板", "name_en": "CrazyTrade", "version": "V1.0",
        "src_rel": ["G10_CrazyTrade/Assets/_Game", "CrazyStocks/Assets/_Game"], "out_dir": "G10_涨停板", "owner": "C机",
    },
    "G12": {
        "name_cn": "就差这一笔游戏软件", "name_short": "就差这一笔", "name_en": "LineRescue", "version": "V1.0",
        "src_rel": "LineRescue/Assets/_Game", "out_dir": "G12_LineRescue", "owner": "C机",
    },
    # ---------- 定名收口区（2026-10-10 委员会 C-20261010-03 代决定名·全组合 32 款定名毕——软著名=平台名一致性红线） ----------
    "G03": {
        "name_cn": "合出个大的游戏软件", "name_short": "合出个大的", "name_en": "MergeMania", "version": "V1.0",
        "src_rel": "MergeMania/Assets/_Game", "owner": "C机", "name_pending": False,
    },
    "G06": {
        "name_cn": "一箭脱身游戏软件", "name_short": "一箭脱身", "name_en": "ArrowRush", "version": "V1.0",
        "src_rel": "ArrowRush/Assets/_Game", "owner": "C机", "name_pending": False,
    },
    "G17": {
        "name_cn": "拆箱上头游戏软件", "name_short": "拆箱上头", "name_en": "UnboxIt", "version": "V1.0",
        "src_rel": "UnboxIt/Assets/_Game", "owner": "C机", "name_pending": False,
    },
    "G18": {
        "name_cn": "今晚偷皇宫游戏软件", "name_short": "今晚偷皇宫", "name_en": "PalacePlunder", "version": "V1.0",
        "src_rel": "PalacePlunder/Assets/_Game", "owner": "C机", "name_pending": False,
    },
    "G23": {
        "name_cn": "这张牌有诈游戏软件", "name_short": "这张牌有诈", "name_en": "CardRogue", "version": "V1.0",
        "src_rel": "G23_CardRogue/Assets/_Game", "owner": "B机", "name_pending": False,
    },
    "G28": {
        "name_cn": "这一箭稳了游戏软件", "name_short": "这一箭稳了", "name_en": "ArrowOut", "version": "V1.0",
        "src_rel": "G28_ArrowOut/Assets/_Game", "owner": "B机", "name_pending": False,
    },
}


def resolve_src(cfg):
    """Resolve src_rel (str or list of candidates) against every candidate root; returns existing dir or None."""
    rels = cfg.get('src_rel')
    if isinstance(rels, str):
        rels = [rels]
    if cfg.get('src_abs') and os.path.isdir(cfg['src_abs']):
        return cfg['src_abs']
    for rel in rels:
        parts = rel.split('/')
        for root in SRC_ROOTS:
            if not os.path.isdir(root):
                continue
            cand = os.path.normpath(os.path.join(root, *parts))
            if os.path.isdir(cand):
                return cand
    return None


def collect_source_files(src_dir):
    """Collect .cs files, entry-point files first, then alphabetical."""
    all_files = []
    for root, dirs, filenames in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in ('Editor', 'ThirdParty', 'Plugins', 'lib')]
        for fn in filenames:
            if fn.endswith('.cs') and not fn.endswith('.meta'):
                all_files.append(os.path.join(root, fn))
    def sort_key(f):
        bn = os.path.basename(f).lower()
        priority = 0
        if bn.startswith(('boot', 'entry', 'main', 'app', 'game')):
            priority = -1
        return (priority, f)
    all_files.sort(key=sort_key)
    return all_files


def read_all_lines(files):
    """Read all non-empty lines from all files, natural file boundaries."""
    all_lines = []
    for fpath in files:
        bn = os.path.basename(fpath)
        all_lines.append(f"// {bn}")
        try:
            with open(fpath, 'r', encoding='utf-8-sig', errors='replace') as f:
                for line in f:
                    line = line.rstrip('\n').rstrip('\r')
                    if line.strip() == '':
                        continue
                    all_lines.append(line)
        except:
            pass
    return all_lines


def sync_guide_linecount(out_dir, total_lines, file_count, total_pages, software_name, version):
    """Auto-update 源程序量 row + 鉴别材料 source-page line in 申请表填写指南.md with real measurement."""
    guide = os.path.join(out_dir, '申请表填写指南.md')
    if not os.path.exists(guide):
        return
    try:
        with open(guide, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        new_row = f"| 源程序量 | {total_lines}行（{file_count}个.cs文件） |"
        content2 = re.sub(r'\| 源程序量 \|[^\n]*\|', new_row, content, count=1)
        if total_pages < 60:
            small_line = (f"源程序：程序总量不足60页，全部{total_pages}页提交，每页不少于50行，"
                         f"页眉「{software_name} {version} 源程序」，最后一页结束在程序末尾。")
            content2 = re.sub(r'源程序：前后各连续30页共60页[^\n]*', small_line, content2, count=1)
            content2 = re.sub(r'第60页结束在程序末尾', '最后一页结束在程序末尾', content2)
        with open(guide, 'w', encoding='utf-8-sig') as f:
            f.write(content2)
        if content2 != content:
            print(f"  Guide synced: 源程序量 -> {total_lines}行/{file_count}文件/{total_pages}页")
    except Exception as e:
        print(f"  Guide sync skipped: {e}")


def build_source_txt(lines, out_path, software_name, version):
    """Build 60 pages: first 30 from program start, last 30 ending at program end."""
    LINES_PER_PAGE = 50
    TOTAL_PAGES = 60
    half = LINES_PER_PAGE * 30  # 1500

    total = len(lines)
    if total < 3000:
        mid = total // 2
        first_half = lines[:mid]
        second_half = lines[mid:]
    else:
        first_half = lines[:half]
        # Last 30 pages MUST end with the actual last line of the program
        second_half = lines[-half:]

    all_page_lines = first_half + second_half
    actual_pages = min(TOTAL_PAGES, (len(all_page_lines) + LINES_PER_PAGE - 1) // LINES_PER_PAGE)

    with open(out_path, 'w', encoding='utf-8-sig') as f:
        page_num = 0
        for i in range(0, len(all_page_lines), LINES_PER_PAGE):
            page_num += 1
            if page_num > TOTAL_PAGES:
                break
            chunk = all_page_lines[i:i+LINES_PER_PAGE]
            while len(chunk) < LINES_PER_PAGE:
                chunk.append('')
            f.write(f"{software_name} {version} 源程序  第 {page_num} 页 共 {actual_pages} 页\n")
            f.write("=" * 80 + "\n")
            for line in chunk:
                f.write(line + "\n")
            f.write("=" * 80 + "\n")
            f.write(f"第 {page_num} 页结束\n\n")

    real_last = lines[-1].strip()
    doc_last = all_page_lines[-1].strip() if all_page_lines else ''
    end_ok = real_last == doc_last
    print(f"  Source txt: {page_num} pages, {len(all_page_lines)} lines")
    print(f"  Last line is program end: {end_ok} ('{doc_last[:50]}')")
    return page_num


def build_source_pdf(txt_path, out_path, software_name, version):
    """Build source code PDF from the structured txt."""
    with open(txt_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    pages = []
    current_code = []
    in_code = False

    for line in lines:
        line = line.rstrip('\n').rstrip('\r')
        if '源程序' in line and '第' in line and '页' in line and '共' in line:
            if current_code:
                pages.append(current_code[:])
            current_code = []
            in_code = False
            continue
        if '页结束' in line:
            in_code = False
            continue
        if set(line.strip()) == {'='}:
            continue
        if line.strip() == '':
            continue
        if software_name in line and '源程序' in line:
            continue
        current_code.append(line)

    if current_code:
        pages.append(current_code[:])

    total_pages = len(pages)
    print(f"  Parsed {total_pages} pages for PDF")

    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    left_margin = 20 * mm
    right_margin = 20 * mm
    top_margin = 20 * mm
    bottom_margin = 20 * mm
    header_height = 12 * mm
    footer_height = 8 * mm
    code_area_height = height - top_margin - bottom_margin - header_height - footer_height
    font_size = 7.5
    leading = code_area_height / 50.0

    for idx, code_lines in enumerate(pages):
        pn = idx + 1
        # Header
        c.setFont('SimHei', 9)
        c.setFillColor(HexColor('#333333'))
        c.drawString(left_margin, height - top_margin + 2*mm, f"{software_name} {version} 源程序")
        c.drawRightString(width - right_margin, height - top_margin + 2*mm, f"第 {pn} 页 共 {total_pages} 页")
        c.setStrokeColor(HexColor('#999999'))
        c.setLineWidth(0.5)
        c.line(left_margin, height - top_margin - 1*mm, width - right_margin, height - top_margin - 1*mm)

        # Code
        c.setFont('Consolas', font_size)
        c.setFillColor(black)
        y = height - top_margin - header_height
        for i, cl in enumerate(code_lines[:50]):
            safe = cl.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if len(safe) > 120:
                safe = safe[:120]
            c.drawString(left_margin, y, safe)
            y -= leading

        # Footer
        c.setStrokeColor(HexColor('#999999'))
        c.line(left_margin, bottom_margin + 3*mm, width - right_margin, bottom_margin + 3*mm)
        c.setFont('SimSun', 8)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(width/2, bottom_margin, f"{software_name} {version}  源程序交存  第 {pn} 页 / 共 {total_pages} 页")
        c.showPage()

    c.save()
    print(f"  Source PDF saved: {out_path}")


def build_design_pdf(md_path, out_path, software_name, version):
    """Build design document PDF from markdown."""
    with open(md_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    lines = content.split('\n')
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('CT', parent=styles['Title'], fontName='SimHei', fontSize=24, leading=34, alignment=TA_CENTER, spaceAfter=8, textColor=black)
    subtitle_style = ParagraphStyle('CS', parent=styles['Normal'], fontName='SimSun', fontSize=15, leading=22, alignment=TA_CENTER, spaceAfter=6, textColor=HexColor('#333333'))
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontName='SimHei', fontSize=15, leading=21, spaceBefore=8, spaceAfter=5, textColor=black)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName='SimHei', fontSize=12.5, leading=18, spaceBefore=6, spaceAfter=3, textColor=HexColor('#1a1a1a'))
    h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontName='SimHei', fontSize=11, leading=16, spaceBefore=4, spaceAfter=2, textColor=HexColor('#333333'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='SimSun', fontSize=10, leading=17, alignment=TA_JUSTIFY, spaceAfter=4, firstLineIndent=20)
    code_style = ParagraphStyle('Code', parent=styles['Normal'], fontName='Consolas', fontSize=8, leading=12.5, alignment=TA_LEFT, spaceAfter=2, leftIndent=10, backColor=HexColor('#f5f5f5'))

    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=25*mm, rightMargin=25*mm, topMargin=28*mm, bottomMargin=26*mm)
    story = []
    in_code = False
    code_buf = []
    usable_w = A4[0] - 50*mm

    def flush_code():
        nonlocal code_buf
        if code_buf:
            for cl in code_buf:
                safe = cl.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(safe if safe.strip() else '&nbsp;', code_style))
            code_buf = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if set(line.strip()) == {'='} and len(line.strip()) > 10:
            flush_code()
            i += 1
            continue

        if line.startswith('```'):
            if in_code: flush_code(); in_code = False
            else: flush_code(); in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip() == '':
            flush_code()
            story.append(Spacer(1, 2*mm))
            i += 1
            continue

        # Title page
        if i < 10 and software_name in line and '软件设计说明书' in line:
            story.append(Spacer(1, 40*mm))
            story.append(Paragraph(software_name, title_style))
            story.append(Paragraph('软件设计说明书', title_style))
            story.append(Spacer(1, 10*mm))
            story.append(Paragraph(f'版本号：{version}', subtitle_style))
            i += 1
            continue

        if line.startswith('# '):
            flush_code()
            story.append(Paragraph(line[2:].strip(), h1_style))
        elif line.startswith('## '):
            flush_code()
            story.append(Paragraph(line[3:].strip(), h2_style))
        elif line.startswith('### '):
            flush_code()
            story.append(Paragraph(line[4:].strip(), h3_style))
        elif line.startswith('#### '):
            flush_code()
            story.append(Paragraph(line[5:].strip(), h3_style))
        elif line.startswith('|') and '|' in line[1:]:
            flush_code()
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if all(set(c.strip()) <= set('-: ') for c in cells):
                i += 1
                continue
            safe_cells = [c.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') for c in cells]
            para_cells = [Paragraph(c, ParagraphStyle('tc', fontName='SimSun', fontSize=8, leading=11)) for c in safe_cells]
            t = Table([para_cells], colWidths=[usable_w/len(cells)]*len(cells))
            t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,HexColor('#ccc')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),1.5),('BOTTOMPADDING',(0,0),(-1,-1),1.5)]))
            story.append(t)
            story.append(Spacer(1, 1*mm))
        elif line.strip().startswith(('- ', '* ', '• ')):
            flush_code()
            text = line.strip()[2:].strip()
            safe = text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
            story.append(Paragraph('• ' + safe, ParagraphStyle('li', parent=body_style, leftIndent=16, firstLineIndent=0)))
        else:
            flush_code()
            safe = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
            story.append(Paragraph(safe, body_style))

        i += 1

    flush_code()

    def add_pn(canvas, doc):
        canvas.saveState()
        canvas.setFont('SimSun', 8)
        canvas.setFillColor(HexColor('#666'))
        canvas.drawCentredString(A4[0]/2, 15*mm, f"{software_name} {version} 软件设计说明书  第 {doc.page} 页")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_pn, onLaterPages=add_pn)
    print(f"  Design PDF saved: {out_path}")


def build_md_pdf(md_path, out_path, header_text):
    """Generic markdown to PDF."""
    with open(md_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    lines = content.split('\n')
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName='SimHei', fontSize=15, leading=20, spaceBefore=14, spaceAfter=6)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='SimHei', fontSize=12, leading=17, spaceBefore=10, spaceAfter=4)
    h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontName='SimHei', fontSize=11, leading=15, spaceBefore=8, spaceAfter=3)
    body = ParagraphStyle('B', parent=styles['Normal'], fontName='SimSun', fontSize=10, leading=16, alignment=TA_JUSTIFY, spaceAfter=3, firstLineIndent=20)
    code = ParagraphStyle('C', parent=styles['Normal'], fontName='Consolas', fontSize=8, leading=11, alignment=TA_LEFT, spaceAfter=1, leftIndent=10, backColor=HexColor('#f5f5f5'))

    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=25*mm, rightMargin=25*mm, topMargin=25*mm, bottomMargin=25*mm)
    story = []
    in_code = False
    buf = []
    usable_w = A4[0] - 50*mm

    def flush():
        nonlocal buf
        if buf:
            for cl in buf:
                s = cl.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                story.append(Paragraph(s if s.strip() else '&nbsp;', code))
            buf = []

    for line in lines:
        line = line.rstrip()
        if line.startswith('```'):
            if in_code: flush(); in_code = False
            else: flush(); in_code = True
            continue
        if in_code: buf.append(line); continue
        if line.strip() == '': flush(); story.append(Spacer(1,2*mm)); continue
        if line.startswith('# '): flush(); story.append(Paragraph(line[2:].strip(), h1))
        elif line.startswith('## '): flush(); story.append(Paragraph(line[3:].strip(), h2))
        elif line.startswith('### '): flush(); story.append(Paragraph(line[4:].strip(), h3))
        elif line.startswith('|') and '|' in line[1:]:
            flush()
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if all(set(c.strip()) <= set('-: ') for c in cells): continue
            sc = [c.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') for c in cells]
            pc = [Paragraph(c, ParagraphStyle('tc', fontName='SimSun', fontSize=8, leading=11)) for c in sc]
            t = Table([pc], colWidths=[usable_w/len(cells)]*len(cells))
            t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,HexColor('#ccc')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
            story.append(t)
        elif line.strip().startswith(('- ','* ')):
            flush()
            t = line.strip()[2:].strip()
            s = t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
            story.append(Paragraph('• '+s, ParagraphStyle('li', parent=body, leftIndent=15, firstLineIndent=0)))
        else:
            flush()
            s = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
            story.append(Paragraph(s, body))
    flush()

    def pn(canvas, doc):
        canvas.saveState()
        canvas.setFont('SimSun', 8)
        canvas.setFillColor(HexColor('#666'))
        canvas.drawCentredString(A4[0]/2, 15*mm, f"{header_text}  第 {doc.page} 页")
        canvas.restoreState()
    doc.build(story, onFirstPage=pn, onLaterPages=pn)
    print(f"  PDF saved: {out_path}")


def process_project(key):
    cfg = PROJECTS[key]
    out_dir = os.path.join(BASE, cfg.get('out_dir', f"{key}_{cfg['name_en']}"))
    os.makedirs(out_dir, exist_ok=True)

    name_cn = cfg['name_cn']
    ver = cfg['version']

    print(f"\n{'='*60}")
    print(f"Processing: {name_cn} ({key}) [owner={cfg.get('owner','')}]")
    if cfg.get('name_pending'):
        print("  NOTE: name_pending=True — 中文定名未定，本位为工作稿，定名后须重渲染。")
    print(f"{'='*60}")

    src_dir = resolve_src(cfg)
    total_lines = 0
    file_count = 0

    # 1-2. Source pipeline (only when source exists on this machine)
    if src_dir:
        print(f"\n[1/4] Collecting source files from: {src_dir}")
        files = collect_source_files(src_dir)
        print(f"  Found {len(files)} .cs files")
        all_lines = read_all_lines(files)
        total_lines = len(all_lines)
        file_count = len(files)
        print(f"  Total non-empty lines: {total_lines}")

        print("\n[2/4] Building source code documents...")
        txt_path = os.path.join(out_dir, f"{cfg['name_en']}_{ver}_源程序.txt")
        pages_built = build_source_txt(all_lines, txt_path, name_cn, ver)
        pdf_path = os.path.join(out_dir, f"{cfg['name_en']}_{ver}_源程序.pdf")
        build_source_pdf(txt_path, pdf_path, name_cn, ver)
        sync_guide_linecount(out_dir, total_lines, file_count, pages_built, name_cn, ver)
    else:
        print(f"\n[1/4] Source NOT on this machine (src_rel='{cfg['src_rel']}') — source steps skipped.")
        print("      Owner machine should run this generator to produce 源程序 materials.")
        print("[2/4] Skipped.")

    # 3. Design doc PDF (md must exist)
    print("\n[3/4] Building design document...")
    md_path = os.path.join(out_dir, f"{cfg['name_en']}_{ver}_软件设计说明书.md")
    if os.path.exists(md_path):
        design_pdf = os.path.join(out_dir, f"{cfg['name_en']}_{ver}_软件设计说明书.pdf")
        build_design_pdf(md_path, design_pdf, name_cn, ver)
    else:
        print(f"  WARNING: {md_path} not found, skipping design PDF")

    # 4. Form guide PDF
    print("\n[4/4] Building form guide...")
    guide_md = os.path.join(out_dir, "申请表填写指南.md")
    if os.path.exists(guide_md):
        guide_pdf = os.path.join(out_dir, "申请表填写指南.pdf")
        build_md_pdf(guide_md, guide_pdf, f"{name_cn} {ver} 申请表填写指南")
    else:
        print(f"  WARNING: {guide_md} not found, skipping")

    print(f"\nDone! Output: {out_dir}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        keys = sys.argv[1:]
    else:
        keys = list(PROJECTS.keys())

    for k in keys:
        if k in PROJECTS:
            process_project(k)
        else:
            print(f"Unknown project: {k}")
