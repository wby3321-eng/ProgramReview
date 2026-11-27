"""生成快慢指针判环、入环点和 LRU 的演示图；不生成环长图。"""

import math

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
BASE = '/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/'

S = 2
FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
N = 8
NODE_W, NODE_H, GAP = 44, 34, 24
CARD_PAD = 16
LIST_W = N * NODE_W + (N - 1) * GAP
CARD_W = LIST_W + CARD_PAD * 2
ARC = 38

STYLES = {
    'plain': ('#dfe7ff', '#1d3557'),
    'orange': ('#ff9944', 'white'),
    'purple': ('#c9bde8', '#3b2a66'),
    'green': ('#7ec8a0', '#0b3d2e'),
    'gold': ('#ffedb8', '#7a5200'),
    'red': ('#f2a9a3', '#7a1f1a'),
    'gray': ('#f2f4f8', '#9aa5b8'),
}

_fonts = {}


def _s(v):
    return int(round(v * S))


def _f(size):
    key = _s(size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_PATH, key)
    return _fonts[key]


_probe = ImageDraw.Draw(Image.new('RGB', (1, 1)))


def _tw(text, size):
    return int(_probe.textlength(str(text), font=_f(size)))


def _cx(k):
    return CARD_PAD + (k - 1) * (NODE_W + GAP) + NODE_W / 2


def _head(d, p1, p2, color, size=7):
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    size = _s(size)
    d.polygon([
        p2,
        (p2[0] - size * math.cos(ang - 0.42), p2[1] - size * math.sin(ang - 0.42)),
        (p2[0] - size * math.cos(ang + 0.42), p2[1] - size * math.sin(ang + 0.42)),
    ], fill=color)


def _arrow(d, pts, color='#3f4b60', width=2, head=7, both=False):
    d.line(pts, fill=color, width=_s(width), joint='curve')
    _head(d, pts[-2], pts[-1], color, head)
    if both:
        _head(d, pts[1], pts[0], color, head)


def _dash(d, p1, p2, color, width=2, dash=8, gap=6):
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    if not length:
        return
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    t = 0.0
    while t < length:
        end = min(t + _s(dash), length)
        d.line([(x1 + ux * t, y1 + uy * t), (x1 + ux * end, y1 + uy * end)],
               fill=color, width=_s(width))
        t = end + _s(gap)


def _dim(d, x1, x2, y, text, color):
    d.line([(_s(x1), _s(y)), (_s(x2), _s(y))], fill=color, width=_s(1))
    for x in (x1, x2):
        d.line([(_s(x), _s(y - 4)), (_s(x), _s(y + 4))], fill=color, width=_s(1))
    d.text((_s((x1 + x2) / 2), _s(y - 5)), text,
           font=_f(10), fill=color, anchor='mb')


def _list_card(caption, marks=None, pointers=None, entry_gold=False, dims=False):
    """横向链表卡片。pointers: [(节点号, 标签, 颜色)]。"""
    marks = marks or {}
    pointers = pointers or []
    top = 88 if dims else 60
    h = top + NODE_H + ARC + (25 if dims else 12)
    im = Image.new('RGB', (_s(CARD_W), _s(h)), 'white')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, _s(CARD_W) - 1, _s(h) - 1],
                        radius=_s(10), fill='#fafcff', outline='#dfe6f0', width=_s(1))
    d.text((_s(13), _s(7)), caption, font=_f(12), fill='#303b4d')

    bot = top + NODE_H
    arc_y = bot + ARC
    d.rounded_rectangle(
        [_s(_cx(4) - NODE_W / 2 - 11), _s(top - 5),
         _s(_cx(8) + NODE_W / 2 + 11), _s(arc_y + 6)],
        radius=_s(8), fill='#f0f5ff',
    )

    ymid = top + NODE_H / 2
    for a in range(1, 8):
        p1 = (_s(_cx(a) + NODE_W / 2), _s(ymid))
        p2 = (_s(_cx(a + 1) - NODE_W / 2), _s(ymid))
        if dims and a in (6, 7):
            _dash(d, p1, p2, '#d4a017')
            _head(d, p1, p2, '#d4a017')
        else:
            _arrow(d, [p1, p2], '#3f5580' if a >= 4 else '#3f4b60', width=1, head=6)

    ring = [(_s(_cx(8)), _s(bot)), (_s(_cx(8)), _s(arc_y)),
            (_s(_cx(4)), _s(arc_y)), (_s(_cx(4)), _s(bot))]
    if dims:
        for p, q in zip(ring, ring[1:]):
            _dash(d, p, q, '#d4a017')
        _head(d, ring[-2], ring[-1], '#d4a017')
    else:
        _arrow(d, ring, '#3f5580', width=1, head=6)

    for k in range(1, N + 1):
        style = marks.get(k, 'plain')
        bg, fg = STYLES[style]
        gold = entry_gold and k == 4
        outline = '#d4a017' if gold else '#8fa4c9'
        d.rounded_rectangle(
            [_s(_cx(k) - NODE_W / 2), _s(top), _s(_cx(k) + NODE_W / 2), _s(bot)],
            radius=_s(7), fill=bg, outline=outline, width=_s(3 if gold else 1),
        )
        d.text((_s(_cx(k)), _s(top + NODE_H / 2)), str(k),
               font=_f(15), fill=fg, anchor='mm')

    for node, label, color in pointers:
        d.text((_s(_cx(node)), _s(top - 7)), label,
               font=_f(9), fill=color, anchor='mb')

    if dims:
        _dim(d, _cx(1), _cx(4), 43, 'D = 3', '#b06a00')
        _dim(d, _cx(4), _cx(6), 43, 'S1 = 2', '#1f6f7f')
        d.text((_s((_cx(4) + _cx(8)) / 2), _s(arc_y + 8)),
               'S2 = 3（金色虚线：6 → 7 → 8 → 4）',
               font=_f(10), fill='#8a5a00', anchor='mt')
    return im


def _grid(cards, cols=2, gap=22):
    rows = [cards[i:i + cols] for i in range(0, len(cards), cols)]
    cw = max(c.width for c in cards)
    ch = max(c.height for c in cards)
    w = cols * cw + _s(gap) * (cols - 1)
    h = len(rows) * ch + _s(gap) * (len(rows) - 1)
    canvas = Image.new('RGB', (w, h), 'white')
    for r, row in enumerate(rows):
        row_offset = (w - (len(row) * cw + _s(gap) * (len(row) - 1))) // 2
        for c, card in enumerate(row):
            canvas.paste(card, (row_offset + c * (cw + _s(gap)), r * (ch + _s(gap))))
    return canvas


def _vstack(imgs, gap=14):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + _s(gap) * (len(imgs) - 1)
    canvas = Image.new('RGB', (w, h), 'white')
    y = 0
    for im in imgs:
        canvas.paste(im, ((w - im.width) // 2, y))
        y += im.height + _s(gap)
    return canvas


def _dash_box(d, box, color):
    x1, y1, x2, y2 = box
    _dash(d, (x1, y1), (x2, y1), color, width=1, dash=4, gap=3)
    _dash(d, (x2, y1), (x2, y2), color, width=1, dash=4, gap=3)
    _dash(d, (x2, y2), (x1, y2), color, width=1, dash=4, gap=3)
    _dash(d, (x1, y2), (x1, y1), color, width=1, dash=4, gap=3)


def _broken_link(d, x1, x2, y):
    """两段红色虚线 + 中间 ×，表示 prev / next 指针已断开。"""
    mid = (x1 + x2) / 2
    _dash(d, (x1, y), (mid - _s(5), y), '#d05a5a', width=1, dash=3, gap=3)
    _dash(d, (mid + _s(5), y), (x2, y), '#d05a5a', width=1, dash=3, gap=3)
    r = _s(4)
    d.line([(mid - r, y - r), (mid + r, y + r)], fill='#c0392b', width=_s(2))
    d.line([(mid - r, y + r), (mid + r, y - r)], fill='#c0392b', width=_s(2))


def _formula_panel():
    lines = [
        '首次相遇：2(D + S1) = D + S1 + n(S1 + S2)',
        '整理得 D = (n − 1)(S1 + S2) + S2；本例 n = 1，所以 D = S2 = 3',
    ]
    im = Image.new('RGB', (_s(CARD_W), _s(66)), 'white')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, _s(CARD_W) - 1, _s(66) - 1],
                        radius=_s(10), fill='#fafcff', outline='#dfe6f0', width=_s(1))
    d.rounded_rectangle([0, _s(10), _s(4), _s(56)], radius=_s(2), fill='#d4a017')
    for i, line in enumerate(lines):
        d.text((_s(14), _s(10 + i * 25)), line, font=_f(11), fill='#4a5568')
    return im


def _finish(img, filename, legend):
    legend_w = _tw(legend, 11)
    w = max(img.width, legend_w) + _s(24)
    h = img.height + _s(42)
    canvas = Image.new('RGB', (w, h), 'white')
    canvas.paste(img, ((w - img.width) // 2, _s(6)))
    d = ImageDraw.Draw(canvas)
    d.text((w / 2, img.height + _s(17)), legend,
           font=_f(11), fill='#5a6577', anchor='mt')
    canvas.save(BASE + filename)
    print(f'已生成 {filename}（{canvas.width}×{canvas.height}）')


def build_cycle_detect_plot():
    snaps = [
        (None, None, '出发：快、慢指针都从头节点 1 开始'),
        (3, 2, '前进 1 次：快指针到 3，慢指针到 2'),
        (5, 3, '前进 2 次：快指针到 5，慢指针到 3'),
        (7, 4, '前进 3 次：快指针到 7，慢指针到入环点 4'),
        (4, 5, '前进 4 次：快指针绕回 4，慢指针到 5'),
        (6, 6, '前进 5 次：两指针在节点 6 相遇，因此有环'),
    ]
    cards = []
    for fast, slow, caption in snaps:
        if fast is None:
            marks, pointers = {}, [(1, '快、慢', '#5a6577')]
        elif fast == slow:
            marks = {fast: 'green'}
            pointers = [(fast, '快 = 慢', '#0b3d2e')]
        else:
            marks = {fast: 'orange', slow: 'purple'}
            pointers = [(fast, '快', '#c85f16'), (slow, '慢', '#5d4494')]
        cards.append(_list_card(caption, marks, pointers))
    _finish(
        _grid(cards), 'linked_list_cycle_detect.png',
        '橙 = 快指针（每次 2 步）    紫 = 慢指针（每次 1 步）    绿 = 相遇；'
        '示例环为 4 → 5 → 6 → 7 → 8 → 4，第 5 次前进在节点 6 相遇',
    )


def build_cycle_entry_plot():
    overview = _list_card(
        '首次相遇的位置关系：头节点 1，入环点 4，相遇点 6',
        marks={6: 'gold'}, pointers=[(6, '首次相遇', '#7a5200')],
        entry_gold=True, dims=True,
    )
    snaps = [
        (1, 6, '出发：A 在头节点 1，B 在相遇点 6；每次同走 1 步'),
        (2, 7, '前进 1 次：A 到 2，B 到 7'),
        (3, 8, '前进 2 次：A 到 3，B 到 8'),
        (4, 4, '前进 3 次：A、B 同时在 4，第二次相遇即入环点'),
    ]
    cards = []
    for a, b, caption in snaps:
        if a == b:
            marks = {a: 'gold'}
            pointers = [(a, 'A = B', '#7a5200')]
        else:
            marks = {a: 'orange', b: 'purple'}
            pointers = [(a, 'A', '#c85f16'), (b, 'B', '#5d4494')]
        cards.append(_list_card(caption, marks, pointers, entry_gold=True))
    body = _vstack([overview, _formula_panel(), _grid(cards)], gap=14)
    _finish(
        body, 'linked_list_cycle_entry.png',
        '橙 = 指针 A（从头节点 1 出发）    紫 = 指针 B（从相遇点 6 出发）    金 = 相遇点 / 入环点；'
        '本例 n = 1，D = S2 = 3，所以同速走 3 步在节点 4 会合',
    )


LRU_CARD_W, LRU_CARD_H = 500, 190
LRU_NODE_W, LRU_NODE_H, LRU_GAP = 44, 34, 22
LRU_PAGE_W = 2 * LRU_CARD_W + 20


def _lru_card(caption, detail, columns, hash_keys, note='', broken=False):
    """哈希链表卡片：上行哈希键，下行双向链表，虚线表示 key → 节点。

    columns: [(值, 类型)]，类型为 node / touched / ghost / evicted。
    broken: 涉及 ghost 的相邻指针画成断开样式。
    """
    im = Image.new('RGB', (_s(LRU_CARD_W), _s(LRU_CARD_H)), 'white')
    d = ImageDraw.Draw(im)
    kinds = [k for _, k in columns]
    accent = '#c94a4a' if 'evicted' in kinds else '#7a6bb5' if 'ghost' in kinds else \
        '#ff9944' if 'touched' in kinds else '#8fa4c9'
    d.rounded_rectangle([0, 0, _s(LRU_CARD_W) - 1, _s(LRU_CARD_H) - 1],
                        radius=_s(10), fill='#fafcff', outline='#dfe6f0', width=_s(1))
    d.rounded_rectangle([0, _s(10), _s(4), _s(LRU_CARD_H - 10)], radius=_s(2), fill=accent)
    d.text((_s(14), _s(8)), caption, font=_f(12), fill='#2f3a4d')
    d.text((_s(14), _s(28)), detail, font=_f(9), fill='#6b788c')
    d.text((_s(14), _s(64)), '哈希表', font=_f(9), fill='#6a5a78', anchor='lm')

    evicted = [c for c in columns if c[1] == 'evicted']
    main = [c for c in columns if c[1] != 'evicted']
    main_w = len(main) * LRU_NODE_W + (len(main) - 1) * LRU_GAP
    total = main_w + (LRU_NODE_W + 22 if evicted else 0)
    start = (LRU_CARD_W - total) / 2

    if evicted:
        ev_cx = start + LRU_NODE_W / 2
        main_start = start + LRU_NODE_W + 22
    else:
        ev_cx, main_start = None, start

    centers = [main_start + i * (LRU_NODE_W + LRU_GAP) + LRU_NODE_W / 2
               for i in range(len(main))]
    node_top, node_bot = 104, 104 + LRU_NODE_H
    ymid = node_top + LRU_NODE_H / 2

    for (value, kind), cx in zip(main, centers):
        if value not in hash_keys:
            continue
        ghost = kind == 'ghost'
        d.rounded_rectangle([_s(cx - LRU_NODE_W / 2), _s(52),
                             _s(cx + LRU_NODE_W / 2), _s(76)],
                            radius=_s(5), fill='#f6f7fa' if ghost else '#f3f0fb',
                            outline='#d8dde7' if ghost else '#d5cdf0', width=_s(1))
        d.text((_s(cx), _s(64)), f'键 {value}', font=_f(9),
               fill='#9aa5b8' if ghost else '#5b4b8a', anchor='mm')
        _dash(d, (_s(cx), _s(76)), (_s(cx), _s(node_top - 2)),
              '#cfd6e2' if ghost else '#b9aede', width=1, dash=3, gap=3)

    if evicted:
        box = [_s(ev_cx - LRU_NODE_W / 2), _s(node_top),
               _s(ev_cx + LRU_NODE_W / 2), _s(node_bot)]
        d.rounded_rectangle(box, radius=_s(7), fill=STYLES['red'][0],
                            outline='#c94a4a', width=_s(2))
        d.text((_s(ev_cx), _s(ymid)), str(evicted[0][0]),
               font=_f(14), fill=STYLES['red'][1], anchor='mm')
        d.text((_s(ev_cx), _s(node_bot + 4)), '已淘汰',
               font=_f(8), fill='#a43838', anchor='mt')
        _broken_link(d, _s(ev_cx + LRU_NODE_W / 2),
                     _s(centers[0] - LRU_NODE_W / 2), _s(ymid))

    for (value, kind), cx in zip(main, centers):
        box = [_s(cx - LRU_NODE_W / 2), _s(node_top),
               _s(cx + LRU_NODE_W / 2), _s(node_bot)]
        if kind == 'ghost':
            _dash_box(d, box, '#b7c0cf')
            d.text((_s(cx), _s(ymid)), str(value), font=_f(14), fill='#9aa5b8', anchor='mm')
            d.text((_s(cx), _s(node_bot + 4)), '已摘下', font=_f(8), fill='#a43838', anchor='mt')
        else:
            if kind == 'touched':
                bg, fg, outline, wd = STYLES['orange'][0], STYLES['orange'][1], '#d48806', 2
            else:
                bg, fg, outline, wd = STYLES['plain'][0], STYLES['plain'][1], '#8fa4c9', 1
            d.rounded_rectangle(box, radius=_s(7), fill=bg, outline=outline, width=_s(wd))
            d.text((_s(cx), _s(ymid)), str(value), font=_f(14), fill=fg, anchor='mm')

    for i in range(len(main) - 1):
        x1 = _s(centers[i] + LRU_NODE_W / 2)
        x2 = _s(centers[i + 1] - LRU_NODE_W / 2)
        if broken and (main[i][1] == 'ghost' or main[i + 1][1] == 'ghost'):
            _broken_link(d, x1, x2, _s(ymid))
        else:
            _arrow(d, [(x1, _s(ymid)), (x2, _s(ymid))], '#5a6577', width=1, head=5, both=True)

    d.text((_s(centers[0]), _s(node_bot + 18)), 'LRU · 最久',
           font=_f(9), fill='#68758a', anchor='mt')
    d.text((_s(centers[-1]), _s(node_bot + 18)), 'MRU · 最近',
           font=_f(9), fill='#68758a', anchor='mt')
    d.text((_s(14), _s(166)), note, font=_f(9), fill='#6b788c')
    return im


def _lru_stage(title, color, cards):
    head = Image.new('RGB', (_s(LRU_PAGE_W), _s(24)), 'white')
    hd = ImageDraw.Draw(head)
    hd.rounded_rectangle([0, _s(5), _s(4), _s(19)], radius=_s(2), fill=color)
    hd.text((_s(13), _s(3)), title, font=_f(14), fill='#26313f')

    row = Image.new('RGB', (_s(LRU_PAGE_W), _s(LRU_CARD_H)), 'white')
    x = 0
    for card in cards:
        row.paste(card, (x, 0))
        x += _s(LRU_CARD_W + 20)

    canvas = Image.new('RGB', (_s(LRU_PAGE_W), _s(24) + _s(8) + _s(LRU_CARD_H)), 'white')
    canvas.paste(head, (0, 0))
    canvas.paste(row, (0, _s(32)))
    return canvas


def build_lru_plot():
    stages = [
        _lru_stage('阶段 1 · 未命中：直接插入 MRU 端', '#ff9944', [
            _lru_card(
                '初始：容量 5，已有 1、2、3、4', '哈希表存 4 个键，双向链表按访问顺序排列',
                [(1, 'node'), (2, 'node'), (3, 'node'), (4, 'node')], {1, 2, 3, 4},
                '哈希表：{1,2,3,4} 各指向一个节点，键与节点一一对应',
            ),
            _lru_card(
                '访问 5：未命中，插到 MRU 端', '容量未满，不淘汰；哈希表新增键 5',
                [(1, 'node'), (2, 'node'), (3, 'node'), (4, 'node'), (5, 'touched')],
                {1, 2, 3, 4, 5}, '哈希表新增 5 → node5，链表尾节点变为 5',
            ),
        ]),
        _lru_stage('阶段 2 · 命中：先断开前后指针，再挂到 MRU 端（以节点 2 为例）', '#7a6bb5', [
            _lru_card(
                '第一步：node2 从 prev(1) 与 next(3) 断开', '哈希表仍保留键 2，可直接定位到 node2',
                [(1, 'node'), (2, 'ghost'), (3, 'node'), (4, 'node'), (5, 'node')],
                {1, 2, 3, 4, 5},
                '红色 × = 两条指针已断开；此时顺序为 1 → 3 → 4 → 5，node2 暂时悬空',
                broken=True,
            ),
            _lru_card(
                '第二步：把 node2 接到 MRU 端', 'prev 指向 5、next 为空，node2 成为新的尾节点',
                [(1, 'node'), (3, 'node'), (4, 'node'), (5, 'node'), (2, 'touched')],
                {1, 2, 3, 4, 5},
                '哈希表键集合不变，只改双向链表指针；顺序变为 1 → 3 → 4 → 5 → 2',
            ),
        ]),
        _lru_stage('阶段 3 · 修改视同访问：节点 4 移到 MRU 端', '#4d9472', [
            _lru_card(
                '修改 4：同样视为一次访问', '把 node4 摘下后挂到尾部；node1 仍是最久未使用',
                [(1, 'node'), (3, 'node'), (5, 'node'), (2, 'node'), (4, 'touched')],
                {1, 2, 3, 4, 5},
                '哈希表键集合不变，仅更新链表顺序为 1 → 3 → 5 → 2 → 4',
            ),
        ]),
        _lru_stage('阶段 4 · 容量已满：淘汰 LRU 端节点 1，再插入 6', '#c94a4a', [
            _lru_card(
                '访问 6：未命中且链表已满', '哈希表删除键 1、插入键 6；新的 LRU 端变为 node3',
                [(1, 'evicted'), (3, 'node'), (5, 'node'), (2, 'node'), (4, 'node'),
                 (6, 'touched')],
                {2, 3, 4, 5, 6},
                '红框 = 已从哈希表与链表同时删除的 node1；node6 成为 MRU',
            ),
        ]),
    ]

    gap = _s(26)
    total_h = sum(st.height for st in stages) + gap * (len(stages) - 1)
    body = Image.new('RGB', (_s(LRU_PAGE_W), total_h), 'white')
    y = 0
    for st in stages:
        body.paste(st, (0, y))
        y += st.height + gap

    _finish(
        body, 'lru_cache.png',
        '上排 = 哈希表（key 直接定位节点）    下排 = 双向链表（prev / next）    '
        '橙 = 本次访问或新插入    红 = 被淘汰    紫虚线框 = 已摘下、指针断开    '
        '左端 LRU、右端 MRU，两者配合实现 O(1) 查询与 O(1) 移动',
    )


if __name__ == '__main__':
    build_cycle_detect_plot()
    build_cycle_entry_plot()
    build_lru_plot()
