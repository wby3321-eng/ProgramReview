"""生成「字符串算法 / 经典算法题」各主题的原理演示图。

渲染约定：
  - 全局 2 倍超采样（S=2），保证文字与线条清晰
  - 图内不再重复大标题（小节标题已在 markdown 中），仅保留底部图例
  - 表格优先：用 _table 统一对齐，避免手工拼叠造成错位
"""

import math

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
BASE = '/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/'

S = 2          # 超采样倍数
CW, CH, CG = 44, 34, 6
PAD = 16

STYLES = {
    'plain':  ('#dfe7ff', '#1d3557'),
    'gold':   ('#ffedb8', '#7a5200'),
    'orange': ('#ff9944', 'white'),
    'green':  ('#7ec8a0', '#0b3d2e'),
    'purple': ('#c9bde8', '#3b2a66'),
    'off':    ('#eef1f6', '#aab4c8'),
    'on':     ('#a9c6f5', '#12325c'),
    'red':    ('#f2a9a3', '#7a1f1a'),
    'pair1':  ('#d5c4f2', '#432a75'),
    'pair2':  ('#b9e2dc', '#0d4b45'),
    'gray':   ('#f2f4f8', '#9aa5b8'),
}

_fonts = {}


def _s(v):
    return int(round(v * S))


def _f(size):
    key = int(size * S)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_PATH, key)
    return _fonts[key]


_probe = ImageDraw.Draw(Image.new('RGB', (1, 1)))


def _tw(text, size):
    return int(_probe.textlength(str(text), font=_f(size)))


def _txt(text, size=12, color='#444444'):
    w = max(_tw(text, size) + _s(4), 2)
    im = Image.new('RGB', (w, _s(size + 10)), 'white')
    ImageDraw.Draw(im).text((_s(2), _s(5)), str(text), font=_f(size), fill=color)
    return im


def _cells(items, indices=None, cw=CW, ch=CH, gap=CG, size=16, radius=6):
    """一行圆角格子。items: [(文本, 样式名)] 或 [文本]"""
    if not items:
        return Image.new('RGB', (2, 2), 'white')
    show = indices is not False
    n = len(items)
    cw, ch, gap = _s(cw), _s(ch), _s(gap)
    w = n * cw + (n - 1) * gap
    h = ch + (_s(18) if show else 0)
    im = Image.new('RGB', (w, h), 'white')
    d = ImageDraw.Draw(im)
    for i, it in enumerate(items):
        txt, key = (it[0], it[1]) if isinstance(it, tuple) else (it, 'plain')
        bg, fg = STYLES[key]
        x = i * (cw + gap)
        d.rounded_rectangle([x, 0, x + cw - 1, ch - 1], radius=_s(radius),
                            fill=bg, outline='#8fa4c9')
        d.text((x + cw / 2, ch / 2), str(txt), font=_f(size), fill=fg, anchor='mm')
        if show:
            lab = str(i) if indices is None else str(indices[i])
            d.text((x + cw / 2, ch + _s(4)), lab, font=_f(9), fill='#999999', anchor='ma')
    return im


def _bits(value, nbits=4, hit=-1, labels=False, **kw):
    cells = []
    for pos in range(nbits - 1, -1, -1):
        b = (value >> pos) & 1
        cells.append((str(b), 'orange' if pos == hit else ('on' if b else 'off')))
    idx = [f'b{i}' for i in range(nbits - 1, -1, -1)] if labels else False
    return _cells(cells, indices=idx, **kw)


def _bstr(v, nbits):
    """'0100' → '0 1 0 0'，便于表格中逐位对照。"""
    return ' '.join(f'{v:0{nbits}b}')


def _hstack(imgs, gap=10, align='center'):
    imgs = [i for i in imgs if i is not None]
    if not imgs:
        return Image.new('RGB', (2, 2), 'white')
    gap = _s(gap)
    w = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    h = max(i.height for i in imgs)
    canvas = Image.new('RGB', (w, h), 'white')
    x = 0
    for im in imgs:
        y = 0 if align == 'top' else (h - im.height) // 2
        canvas.paste(im, (x, y))
        x += im.width + gap
    return canvas


def _vstack(imgs, gap=8):
    imgs = [i for i in imgs if i is not None]
    if not imgs:
        return Image.new('RGB', (2, 2), 'white')
    gap = _s(gap)
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    canvas = Image.new('RGB', (w, h), 'white')
    y = 0
    for im in imgs:
        canvas.paste(im, ((w - im.width) // 2, y))
        y += im.height + gap
    return canvas


def _vstack_left(imgs, gap=8):
    imgs = [i for i in imgs if i is not None]
    if not imgs:
        return Image.new('RGB', (2, 2), 'white')
    gap = _s(gap)
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    canvas = Image.new('RGB', (w, h), 'white')
    y = 0
    for im in imgs:
        canvas.paste(im, (0, y))
        y += im.height + gap
    return canvas


def _fill_px(img, width_px, bg='white', align='center'):
    """把图片补白到指定像素宽度（内容居中或靠左），用于让多张卡片等宽铺满。"""
    if img.width >= width_px:
        return img
    out = Image.new('RGB', (width_px, img.height), bg)
    x = 0 if align == 'left' else (width_px - img.width) // 2
    out.paste(img, (x, 0))
    return out


def _lrow(label, img, lw=110, size=12, color='#5a6577'):
    """左侧定宽标签 + 右侧内容，保证多行左端对齐。"""
    w = _s(lw) + img.width
    h = max(img.height, _s(size + 10))
    out = Image.new('RGB', (w, h), 'white')
    d = ImageDraw.Draw(out)
    d.text((_s(lw) - _s(10), h / 2), label, font=_f(size), fill=color, anchor='rm')
    out.paste(img, (_s(lw), (h - img.height) // 2))
    return out


def _table(headers, rows, size=13, header_size=12, col_pad=16, row_pad=9,
           header_bg='#e9eff9', border='#d5deeb', zebra='#fbfcfe',
           width=None, min_col_w=None, align=None):
    """通用表格。单元格可为 str 或 (str, 样式名)。

    width: 目标总宽（逻辑像素）；不足时按列宽比例分配剩余空间，让表格铺满。
    min_col_w: 每列最小宽度列表（逻辑像素），None 表示不限制。
    align: 每列对齐方式（'left' / 'center'），None 表示全部居中。
    """
    ncol = len(headers)

    def text_of(c):
        return c[0] if isinstance(c, tuple) else str(c)

    def style_of(c):
        return STYLES.get(c[1], ('white', '#1d3557')) if isinstance(c, tuple) else ('white', '#1d3557')

    col_w = []
    for j in range(ncol):
        wmax = _tw(headers[j], header_size)
        for r in rows:
            wmax = max(wmax, _tw(text_of(r[j]), size))
        wj = wmax + _s(col_pad) * 2
        if min_col_w and min_col_w[j]:
            wj = max(wj, _s(min_col_w[j]))
        col_w.append(wj)

    if width is not None:
        target = _s(width)
        extra = target - sum(col_w)
        if extra > 0:
            tot = sum(col_w)
            add = [int(extra * c / tot) for c in col_w]
            add[col_w.index(max(col_w))] += extra - sum(add)
            col_w = [c + a for c, a in zip(col_w, add)]

    row_h = _s(size + row_pad * 2)
    head_h = _s(header_size + row_pad * 2)
    m = _s(4)
    W = sum(col_w) + m * 2
    H = head_h + row_h * len(rows) + m * 2
    im = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=_s(8), outline=border, fill='white')
    d.rectangle([m, m, W - m, m + head_h], fill=header_bg)

    x = m
    for j, htxt in enumerate(headers):
        if align and align[j] == 'left':
            d.text((x + _s(col_pad), m + head_h / 2), str(htxt),
                   font=_f(header_size), fill='#3a4a63', anchor='lm')
        else:
            d.text((x + col_w[j] / 2, m + head_h / 2), str(htxt),
                   font=_f(header_size), fill='#3a4a63', anchor='mm')
        x += col_w[j]

    y = m + head_h
    for i, r in enumerate(rows):
        if i % 2 == 1:
            d.rectangle([m, y, W - m, y + row_h], fill=zebra)
        x = m
        for j, c in enumerate(r):
            bg, fg = style_of(c)
            if bg != 'white':
                d.rounded_rectangle([x + _s(4), y + _s(3), x + col_w[j] - _s(4), y + row_h - _s(3)],
                                    radius=_s(5), fill=bg)
            if align and align[j] == 'left':
                d.text((x + _s(col_pad), y + row_h / 2), text_of(c),
                       font=_f(size), fill=fg, anchor='lm')
            else:
                d.text((x + col_w[j] / 2, y + row_h / 2), text_of(c),
                       font=_f(size), fill=fg, anchor='mm')
            x += col_w[j]
        y += row_h
    return im


def _section(title, body, color='#2a9d8f'):
    t = _txt(title, 15, color)
    head = Image.new('RGB', (t.width + _s(14), t.height), 'white')
    hd = ImageDraw.Draw(head)
    hd.rounded_rectangle([0, _s(3), _s(4), t.height - _s(4)], radius=_s(2), fill=color)
    head.paste(t, (_s(14), 0))

    bw, bh = body.width + _s(PAD) * 2, body.height + _s(PAD) * 2
    plate = Image.new('RGB', (bw, bh), 'white')
    pd = ImageDraw.Draw(plate)
    pd.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=_s(10),
                         outline='#dfe6f0', fill='#fafcff')
    plate.paste(body, (_s(PAD), _s(PAD)))
    return _vstack([head, plate], gap=6)


def _footer(img, legend):
    t = _txt(legend, 12, '#5a6577')
    w = max(img.width, t.width) + _s(30)
    canvas = Image.new('RGB', (w, img.height + t.height + _s(16)), 'white')
    canvas.paste(img, ((w - img.width) // 2, _s(8)))
    canvas.paste(t, ((w - t.width) // 2, img.height + _s(14)))
    return canvas


def _down():
    return _txt('↓', 13, '#9aa5b8')


# =====================================================================
# 1. 最大公约数
# =====================================================================

def build_gcd_plot():
    div = _table(
        ['步骤', 'a', 'b', 'a % b', '说明'],
        [
            ['1', '48', '18', '12', '余数不为 0，继续'],
            ['2', '18', '12', '6', '余数不为 0，继续'],
            ['3', '12', '6', ('0', 'green'), ('余数为 0 → gcd = 6', 'green')],
        ],
    )
    sub = _table(
        ['步骤', 'a', 'b', 'a − b', '说明'],
        [
            ['1', '48', '18', '30', '把大数换成差值'],
            ['2', '30', '18', '12', '继续'],
            ['3', '18', '12', '6', '继续'],
            ['4', '12', '6', '6', '继续'],
            ['5', '6', '6', ('0', 'green'), ('a = b → gcd = 6', 'green')],
        ],
    )

    left = _vstack([_txt('辗转相除法：gcd(a, b) = gcd(b, a % b)', 13, '#1f6f7f'), div], gap=8)
    right = _vstack([_txt('辗转相减法：gcd(a, b) = gcd(a−b, b)', 13, '#6a4c93'), sub], gap=8)
    body = _hstack([left, right], gap=40, align='top')

    final = _footer(body,
                    '两种方法都在把 (a, b) 逐步缩小，直到出现 0（或 a = b）；'
                    '剩下的非 0 数就是最大公约数，本题结果都是 6')
    final.save(BASE + 'max_gcd.png')
    print('已生成 max_gcd.png')


# =====================================================================
# 2. 是否是 2 的整数次幂（横向表格）
# =====================================================================

def build_power_of_two_plot():
    bits = 5
    cases = [1, 2, 8, 16, 6, 10, 12]
    rows = []
    for n in cases:
        ok = (n & (n - 1)) == 0
        rows.append([
            str(n),
            _bstr(n, bits),
            _bstr(n - 1, bits),
            (_bstr(n & (n - 1), bits), 'green' if ok else 'red'),
            ('是' if ok else '否', 'green' if ok else 'red'),
        ])

    table = _table(
        ['十进制数', f'二进制数（{bits} 位）', '原数值 − 1', 'n & (n−1)', '是否为 2 的整数次幂'],
        rows,
        size=14, header_size=13, col_pad=18, row_pad=10,
    )
    tip = _txt('只有 1 个 1 的行：n−1 会把那唯一的 1 抹掉，相与必为 0；有多个 1 的行，最高位的 1 依然留下', 12, '#5a6577')
    body = _vstack([table, tip], gap=12)

    final = _footer(body,
                    'n & (n−1) = 0 当且仅当 二进制中只有一个 1，也就当且仅当 n 是 2 的整数次幂；'
                    '相与的作用就是把最低位的 1 消掉，看还剩不剩 1')
    final.save(BASE + 'power_of_two.png')
    print('已生成 power_of_two.png')


# =====================================================================
# 3. 最大相邻差（左：计数排序思路 / 右：鸽巢分桶思路）
# =====================================================================

def _count_chart(arr, cw=46, ch=34, gap=8, lw=86):
    """计数排序的辅助数组：下标 / 值 / 是否出现 三行，并在 0 段下方标注跨度。"""
    lo, hi = min(arr), max(arr)
    n = hi - lo + 1
    present = set(arr)
    flags = [1 if (lo + i) in present else 0 for i in range(n)]

    row_gap = 8
    base_y = 3 * ch + 2 * row_gap
    W = lw + n * cw + (n - 1) * gap
    H = base_y + 74
    im = Image.new('RGB', (_s(W), _s(H)), 'white')
    d = ImageDraw.Draw(im)

    rows = [
        ('下标 i', [str(i) for i in range(n)],
         [('#eef2fa', '#5a6577')] * n, 12),
        ('值 = i + 3', [str(lo + i) for i in range(n)],
         [STYLES['plain']] * n, 15),
        ('是否出现', ['1' if f else '0' for f in flags],
         [STYLES['on'] if f else STYLES['off'] for f in flags], 13),
    ]
    for r, (label, texts, css, fs) in enumerate(rows):
        y = _s(r * (ch + row_gap))
        d.text((_s(lw) - _s(10), y + _s(ch) / 2), label,
               font=_f(12), fill='#5a6577', anchor='rm')
        for i, (t, (bg, fg)) in enumerate(zip(texts, css)):
            x = _s(lw) + _s(i * (cw + gap))
            d.rounded_rectangle([x, y, x + _s(cw) - 1, y + _s(ch) - 1],
                                radius=_s(5), fill=bg, outline='#8fa4c9')
            d.text((x + _s(cw) / 2, y + _s(ch) / 2), t,
                   font=_f(fs), fill=fg, anchor='mm')

    # 找连续的 0 段：两端非零下标之差 = 0 的个数 + 1，也就是这一段的相邻差
    runs, i = [], 0
    while i < n:
        if flags[i] == 0:
            j = i
            while j + 1 < n and flags[j + 1] == 0:
                j += 1
            runs.append((i, j))
            i = j + 1
        else:
            i += 1

    if runs:
        maxrun = max(j - i + 1 for i, j in runs)
        lw1 = max(1, _s(1))
        for idx, (i, j) in enumerate(runs):
            zeros = j - i + 1
            x1 = _s(lw) + _s((i - 1) * (cw + gap)) + _s(cw) / 2
            x2 = _s(lw) + _s((j + 1) * (cw + gap)) + _s(cw) / 2
            y = _s(base_y + 24 + idx * 30)
            best = zeros == maxrun
            color = '#0b7a5a' if best else '#7b8398'
            d.line([(x1, y), (x2, y)], fill=color, width=lw1)
            for xx in (x1, x2):
                d.line([(xx, y - _s(4)), (xx, y + _s(2))], fill=color, width=lw1)
            label = f'{zeros} 个 0 → 差 {zeros + 1}' + ('（最大）' if best else '')
            d.text(((x1 + x2) / 2, y - _s(4)), label, font=_f(10), fill=color, anchor='mb')
    return im


def _bucket_card(bi, lo_i, hi_i, vals, cwd=108, chh=172):
    """单个桶：桶号 / 区间 / 元素码 / min~max；空桶用灰色。"""
    im = Image.new('RGB', (_s(cwd), _s(chh)), 'white')
    d = ImageDraw.Draw(im)
    empty = not vals
    fill = '#f2f4f8' if empty else '#f7f4fd'
    line = '#dbe0e9' if empty else '#c8bce6'
    ink = '#9aa3b3' if empty else '#5b4b96'
    lw1 = max(1, _s(1))

    d.rounded_rectangle([_s(1), _s(1), _s(cwd) - _s(1), _s(chh) - _s(1)],
                        radius=_s(9), fill=fill, outline=line, width=lw1)
    d.text((_s(cwd) / 2, _s(20)), f'桶{bi}', font=_f(13), fill=ink, anchor='mm')
    d.text((_s(cwd) / 2, _s(40)), f'[{lo_i}, {hi_i})', font=_f(10), fill='#7b8398', anchor='mm')
    d.line([(_s(12), _s(52)), (_s(cwd) - _s(12), _s(52))], fill=line, width=lw1)

    if vals:
        y = _s(62)
        for v in sorted(vals):
            cw2, ch2 = 44, 26
            x = (_s(cwd) - _s(cw2)) / 2
            d.rounded_rectangle([x, y, x + _s(cw2), y + _s(ch2)], radius=_s(5),
                                fill='#d5c4f2', outline='#b3a0dd')
            d.text((x + _s(cw2) / 2, y + _s(ch2) / 2), str(v),
                   font=_f(13), fill='#432a75', anchor='mm')
            y += _s(ch2 + 8)
    else:
        d.text((_s(cwd) / 2, _s(92)), '空', font=_f(16), fill='#aab4c8', anchor='mm')
        d.text((_s(cwd) / 2, _s(112)), '无元素', font=_f(9), fill='#b8c0cd', anchor='mm')

    d.line([(_s(12), _s(chh) - _s(32)), (_s(cwd) - _s(12), _s(chh) - _s(32))],
           fill=line, width=lw1)
    d.text((_s(cwd) / 2, _s(chh) - _s(16)),
           f'{min(vals)} ~ {max(vals)}' if vals else '—',
           font=_f(10), fill='#5a6577', anchor='mm')
    return im


def _bucket_strip(buckets, lo, w):
    """一排桶卡片，下方用双向箭头连接相邻非空桶并标出差值。"""
    cwd, chh, gapc = 108, 172, 12
    k = len(buckets)
    W = k * cwd + (k - 1) * gapc
    im = Image.new('RGB', (_s(W), _s(chh + 54)), 'white')
    d = ImageDraw.Draw(im)
    lw1 = max(1, _s(1))

    for i, vals in enumerate(buckets):
        card = _bucket_card(i, lo + i * w, lo + (i + 1) * w, vals, cwd, chh)
        im.paste(card, (_s(i * (cwd + gapc)), 0))

    nonempty = [(i, min(v), max(v)) for i, v in enumerate(buckets) if v]
    gaps = [b_min - a_max for (_, _, a_max), (__, b_min, ___) in zip(nonempty, nonempty[1:])]
    maxgap = max(gaps)
    y = _s(chh + 28)
    hs = _s(5)
    for (i1, _, mx1), (i2, mn2, _) in zip(nonempty, nonempty[1:]):
        x1 = _s(i1 * (cwd + gapc)) + _s(cwd) / 2
        x2 = _s(i2 * (cwd + gapc)) + _s(cwd) / 2
        g = mn2 - mx1
        color = '#0b7a5a' if g == maxgap else '#9aa3b3'
        d.line([(x1, y), (x2, y)], fill=color, width=lw1)
        d.polygon([(x1, y), (x1 + hs, y - hs * 0.6), (x1 + hs, y + hs * 0.6)], fill=color)
        d.polygon([(x2, y), (x2 - hs, y - hs * 0.6), (x2 - hs, y + hs * 0.6)], fill=color)
        label = f'差 {g}' + ('（最大）' if g == maxgap else '')
        d.text(((x1 + x2) / 2, y - _s(6)), label, font=_f(10), fill=color, anchor='mb')
    return im


def build_max_adjacent_diff_plot():
    arr = [3, 7, 4, 5, 8, 12, 11]
    lo, hi = min(arr), max(arr)
    srt = sorted(arr)
    diffs = [b - a for a, b in zip(srt, srt[1:])]
    mx = max(diffs)

    # ---------------- 左：计数排序 ----------------
    chart = _count_chart(arr)

    present = set(arr)
    flags = [1 if (lo + i) in present else 0 for i in range(hi - lo + 1)]
    runs, i = [], 0
    while i < len(flags):
        if flags[i] == 0:
            j = i
            while j + 1 < len(flags) and flags[j + 1] == 0:
                j += 1
            runs.append((i, j))
            i = j + 1
        else:
            i += 1

    gap_rows = [
        [f'{a - 1} → {b + 1}', str(b - a + 1),
         (str(b - a + 2), 'gold' if b - a + 2 == mx else 'plain')]
        for a, b in runs
    ]
    gap_table = _table(['相邻非零下标', '中间 0 的个数', '下标差 = 相邻差'], gap_rows,
                       size=12, header_size=11, col_pad=14, row_pad=8)

    left = _vstack_left([
        _txt('① 计数排序：把「值」当作「下标」（O(n + 值域)）', 13, '#1f6f7f'),
        _lrow('原数组', _cells([(str(v), 'plain') for v in arr], cw=46, gap=8,
                              size=15, indices=False), lw=86),
        chart,
        gap_table,
        _txt('下标 = 值 − 3（例：7 − 3 = 4，7 落在下标 4）；'
             '下标差 = 中间 0 的个数 + 1，也正是排序后这一段的相邻差', 11, '#8a93a5'),
    ], gap=9)

    # ---------------- 右：鸽巢 / 分桶 ----------------
    n = len(arr)
    span = hi - lo
    avg = span / (n - 1)          # 1.5
    w = math.ceil(avg)            # 2
    k = span // w + 1             # 5
    buckets = [[] for _ in range(k)]
    for v in arr:
        buckets[(v - lo) // w].append(v)

    nonempty = [(min(b), max(b)) for b in buckets if b]
    gaps = [b_min - a_max for (_, a_max), (b_min, __) in zip(nonempty, nonempty[1:])]
    gap_txt = '，'.join(f'{g}' for g in gaps)

    right = _vstack_left([
        _txt('② 鸽巢思想：分桶后只比相邻非空桶（O(n)）', 13, '#6a4c93'),
        _txt(f'平均间隔 = span/(n−1) = (12−3)/(7−1) = {avg:g}', 12, '#5a6577'),
        _txt(f'取桶宽 w = ceil({avg:g}) = {w}；M ≥ {avg:g} 且 M 为整数，则 M ≥ {math.ceil(avg)} = w', 12, '#5a6577'),
        _txt(f'桶数 k = floor(span/w) + 1 = floor(9/{w}) + 1 = {k}', 12, '#5a6577'),
        _txt(f'桶内任意两数差 < w = {w} ≤ M，所以最大差只能跨桶出现', 12, '#5a6577'),
        _bucket_strip(buckets, lo, w),
        _txt(f'相邻非空桶的差：{gap_txt}  →  最大 {mx}', 12, '#0b7a5a'),
        _txt('桶 3 为空，被 8（桶2）与 11（桶4）直接跨过；空桶只是让差距更显眼，不是算法成立的前提',
             11, '#8a93a5'),
    ], gap=8)

    cols = _hstack([left, right], gap=46, align='top')

    verify = _table(
        ['排序后（用来对答案）', '相邻差', '最大相邻差'],
        [['  '.join(str(v) for v in srt), '  '.join(str(d) for d in diffs), (str(mx), 'gold')]],
        size=13, header_size=12, col_pad=18, row_pad=9,
    )

    body = _vstack([cols, verify], gap=18)

    final = _footer(body,
                    '左：下标 = 值 − offset，连续 0 的段越长两端的下标差越大（0 的个数 + 1）    '
                    '右：桶宽 w ≤ M 时最大差必跨桶，每桶只记 min/max，扫一遍相邻非空桶即可')
    final.save(BASE + 'max_adjacent_diff.png')
    print('已生成 max_adjacent_diff.png')


# =====================================================================
# 4. 全排列的下一个数
# =====================================================================

def build_next_permutation_plot():
    W = 1080

    # ---------- ① 以 12354 → 12435 走一遍 ----------
    main = _table(
        ['步骤', '第1位', '第2位', '第3位', '第4位', '第5位', '说明'],
        [
            ['初始', '1', '2', '3', '5', '4', '从右往左比较相邻两位'],
            ['① 找边界', '1', '2', ('3', 'orange'), ('5', 'purple'), ('4', 'purple'),
             '5 > 4 是降序，继续；3 < 5 停下 → 边界 = 3（第 3 位）'],
            ['② 交换', '1', '2', ('4', 'gold'), ('5', 'purple'), ('3', 'orange'),
             '右侧降序区 {5,4} 中，从右往左第一个 > 3 的是 4 → 3 与 4 交换'],
            ['③ 反转', '1', '2', '4', ('3', 'green'), ('5', 'green'),
             '边界右侧 53 反转成 35 → 12435（仅大于原数）'],
        ],
        size=14, header_size=13, col_pad=16, row_pad=10,
        width=W, min_col_w=[92, 66, 66, 66, 66, 66, 0],
        align=['center'] * 6 + ['left'],
    )

    # ---------- ② 三步各自在做什么 ----------
    rules = _table(
        ['步骤', '做什么', '为什么这样做'],
        [
            ['① 找边界', '从右往左找第一个 a[i] < a[i+1] 的位置',
             '右边若是降序，说明这段已经是最大；i 是能让数变大、又改动最低的位置'],
            ['② 交换', '在 i 右侧从右往左找第一个 > a[i] 的数，与 a[i] 交换',
             '降序区里从右往左第一个更大的，正是「比它大的最小值」，增量最小'],
            ['③ 反转', '把 i 右侧整段反转',
             '交换后右侧仍是降序，降序反转即升序，得到最小的后缀'],
        ],
        size=14, header_size=13, col_pad=16, row_pad=10,
        width=W, min_col_w=[92, 340, 0], align=['center', 'left', 'left'],
    )

    # ---------- ③ 多例验证 ----------
    more = _table(
        ['输入', '边界 i', '交换', '反转的区段', '输出'],
        [
            ['12345', '4', '4 与 5 互换', '—', ('12354', 'green')],
            ['12354', '3', '3 与 4 互换', '53 → 35', ('12435', 'green')],
            ['12435', '3', '3 与 5 互换', '—', ('12453', 'green')],
            ['115', '第 2 个 1', '1 与 5 互换', '51 → 15', ('151', 'green')],
            ['1221', '首位 1', '1 与 2 互换', '221 → 122', ('2112', 'green')],
            ['4321', '不存在', '—', '—', ('已是最大，无下一个', 'red')],
        ],
        size=14, header_size=13, col_pad=16, row_pad=10,
        width=W, min_col_w=[120, 110, 300, 220, 140],
    )

    body = _vstack([
        _section('① 以 12354 → 12435 走一遍：找边界 → 交换 → 反转', main, '#2a9d8f'),
        _section('② 三步各自在做什么、为什么成立', rules, '#1f6f7f'),
        _section('③ 多验证几个例子（含重复数字）', more, '#6a4c93'),
    ], gap=16)

    final = _footer(body,
                    '边界：从右往左第一个 a[i] < a[i+1]；交换：右侧从右往左第一个 > a[i] 的数；'
                    '反转：降序后缀反转即升序。含重复数字时要用 < 和 >（相等不算），否则边界会找错')
    final.save(BASE + 'next_permutation.png')
    print('已生成 next_permutation.png')


# =====================================================================
# 5. 删除 K 个数字后的最小值
# =====================================================================

def build_remove_k_digits_plot():
    digits = [1, 5, 9, 3, 2, 1, 2]
    k = 3
    st, rows, used = [], [], 0

    rows.append(['—', ('初始，栈为空', 'gray'), ('空', 'gray')])
    for d in digits:
        popped = []
        while st and used < k and st[-1] > d:
            popped.append(st.pop())
            used += 1
        st.append(d)
        if popped:
            act = f'弹出 {"、".join(str(p) for p in popped)}（都比 {d} 大）'
            dcell = (str(d), 'orange')
        else:
            act = '入栈' if len(st) == 1 else '入栈（栈顶更小，不弹）'
            dcell = str(d)
        rows.append([dcell, act, '  '.join(str(v) for v in st)])

    body_table = _table(['读入', '操作', '栈（左 = 栈底，右 = 栈顶）'], rows,
                        size=13, header_size=12, col_pad=16, row_pad=9)

    result = ''.join(str(v) for v in st)
    tail = _hstack([
        _txt(f'共弹出 {used} 次 = k，栈内剩余 ', 12, '#5a6577'),
        _cells([(str(v), 'green') for v in st], size=15, indices=False),
        _txt('  →  ', 13, '#999'),
        _cells([(result, 'gold')], cw=_tw(result, 17) + 24, ch=32, size=17, indices=False),
    ], gap=8)

    body = _vstack([
        body_table,
        tail,
        _txt('若遍历结束还没删够 k 位（如 1234 删 2 位），就从末尾继续删', 11, '#8a93a5'),
    ], gap=12)

    final = _footer(_section('单调栈：新数字更小就把栈顶弹掉，弹一次算删一位', body),
                    '栈保证留下来的高位尽量小且保持升序，删掉的位数正好是 k；'
                    '用栈而不是逐位扫描，是因为弹掉一个数字后它前后的数字还能继续比较')
    final.save(BASE + 'remove_k_digits.png')
    print('已生成 remove_k_digits.png')


# =====================================================================
# 6. 寻找缺失的数字
# =====================================================================

def build_missing_number_plot():
    # ---------- ① 求和法 ----------
    full = [1, 2, 3, 4, 5]
    given = [1, 2, 4, 5]
    p1 = _vstack_left([
        _lrow('完整 1~5', _cells([(str(v), 'gold' if v == 3 else 'plain') for v in full],
                                 indices=False, size=15)),
        _lrow('给定数组', _cells([(str(v), 'plain') for v in given], indices=False, size=15)),
        _hstack([
            _txt('完整和 = (1+5)×5/2 = 15', 12, '#5a6577'),
            _txt('        给定和 = 12', 12, '#5a6577'),
            _txt('        15 − 12 = ', 12, '#5a6577'),
            _cells([('3', 'green')], cw=34, ch=28, size=14, indices=False),
        ], gap=6),
    ], gap=10)

    # ---------- ② 只有一个奇数次：成对抵消 ----------
    arr2 = [4, 1, 2, 1, 2]
    key_of = {4: 'gold'}
    seen = {}
    cells2 = []
    for v in arr2:
        if v == 4:
            cells2.append(('4', 'gold'))
            continue
        seen[v] = seen.get(v, 0) + 1
        cells2.append((str(v), 'pair1' if v == 1 else 'pair2'))

    xors = []
    acc = 0
    for v in arr2:
        acc ^= v
        xors.append(str(acc))

    p2 = _vstack_left([
        _hstack([_txt('原数组', 12, '#5a6577'),
                 _cells(cells2, indices=False, size=15)], gap=12),
        _hstack([
            _txt('相同颜色的两个数异或为 0：', 12, '#5a6577'),
            _cells([('1', 'pair1'), ('^', 'gray'), ('1', 'pair1'), ('=', 'gray'), ('0', 'off')],
                   indices=False, ch=28, size=13),
            _txt('   ', 10),
            _cells([('2', 'pair2'), ('^', 'gray'), ('2', 'pair2'), ('=', 'gray'), ('0', 'off')],
                   indices=False, ch=28, size=13),
        ], gap=6),
        _hstack([
            _txt('所以 4 ^ 1 ^ 2 ^ 1 ^ 2  =  4 ^ (1^1) ^ (2^2)  =  4 ^ 0 ^ 0  =  ', 12, '#5a6577'),
            _cells([('4', 'green')], cw=34, ch=28, size=14, indices=False),
        ], gap=6),
        _txt('说明：把 0^4=4、4^1=5、5^2=7、7^1=6、6^2=4 这类中间值当作计算过程即可，'
             '真正起作用的是「成对的数互相抵消」', 11, '#8a93a5'),
    ], gap=9)

    # ---------- ③ 两个奇数次：全异或 + 探针 + 分组 ----------
    arr3 = [2, 3, 5, 3, 5, 6]
    xor = 0
    for v in arr3:
        xor ^= v

    probe_rows = []
    mask, hit = 1, -1
    for r in range(4):
        res = xor & mask
        if res:
            hit = mask.bit_length() - 1
            judge = (f'≠ 0，命中 bit{hit}', 'green')
        else:
            judge = ('= 0，mask 左移一位', 'gray')
        probe_rows.append([str(r + 1), _bstr(mask, 4), _bstr(res, 4), judge])
        if res:
            break
        mask <<= 1

    probe_table = _table(['轮次', 'mask', 'mask & xor', '判定'], probe_rows,
                         size=13, header_size=12, col_pad=16, row_pad=9)

    g1 = [v for v in arr3 if (v >> hit) & 1]
    g0 = [v for v in arr3 if not (v >> hit) & 1]
    r1, r0 = 0, 0
    for v in g1:
        r1 ^= v
    for v in g0:
        r0 ^= v

    group_table = _table(
        ['分组依据', '元素', '组内异或'],
        [
            [f'bit{hit} = 1', '  '.join(str(v) for v in g1), (str(r1), 'green')],
            [f'bit{hit} = 0', '  '.join(str(v) for v in g0), (str(r0), 'green')],
        ],
        size=13, header_size=12, col_pad=18, row_pad=9,
    )

    probe_block = _vstack_left([
        _txt('第 ② 步：探针从 bit0 往上找「为 1 的位」', 12, '#5a6577'),
        probe_table,
    ], gap=6)

    group_block = _vstack_left([
        _txt(f'第 ③ 步：按 bit{hit} 分组，两组各自异或', 12, '#5a6577'),
        group_table,
    ], gap=6)

    # 两张表左右并排，压低 ③ 的高度，让三段卡片上下更协调
    tables_row = _hstack([probe_block, _txt('→', 18, '#9aa5b8'), group_block],
                         gap=16, align='top')

    p3 = _vstack_left([
        _lrow('原数组', _cells([(str(v), 'gold' if v in (2, 6) else 'plain') for v in arr3],
                               indices=False, size=15)),
        _lrow('全部异或', _cells([(str(xor), 'orange')], cw=36, ch=30, size=15, indices=False)),
        _txt(f'xor = 2^3^5^3^5^6 = {xor} = 二进制 {_bstr(xor, 4)}；'
             f'两个出现奇数次的数在 bit{hit} 上一定不同', 12, '#5a6577'),
        tables_row,
        _hstack([
            _txt('结论：两个出现奇数次的数分别是 ', 13, '#0b7a5a'),
            _cells([(str(r1), 'green'), (str(r0), 'green')], ch=30, size=15, indices=False),
        ], gap=8),
    ], gap=10)

    # 三张卡片统一宽度，避免右边缘参差，整张图铺满
    target = max(p1.width, p2.width, p3.width)
    p1, p2, p3 = (_fill_px(x, target, align='left') for x in (p1, p2, p3))

    body = _vstack([
        _section('① 解法1：完整和 − 给定和 = 缺失数', p1, '#1f6f7f'),
        _section('② 扩展1：只有 1 个数出现奇数次 → 全部异或，成对的自动抵消', p2, '#6a4c93'),
        _section('③ 扩展2：2 个数出现奇数次 → 全异或 + 探针找不同位 + 分组异或', p3, '#c0504d'),
    ], gap=18)

    final = _footer(body,
                    '金色 = 缺失或出现奇数次的数   橙色 = 当前重点   绿色 = 结果    '
                    '两个数异或后为 1 的那一位，正是它们的差异位，天然能把两者分到不同组')
    final.save(BASE + 'missing_number.png')
    print('已生成 missing_number.png')


if __name__ == '__main__':
    build_gcd_plot()
    build_power_of_two_plot()
    build_max_adjacent_diff_plot()
    build_next_permutation_plot()
    build_remove_k_digits_plot()
    build_missing_number_plot()
