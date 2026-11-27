"""生成最小栈、用栈实现队列的演示图。

版式：按操作阶段分组，每个阶段一行卡片，从左到右阅读；
不再使用 2 列网格，避免步骤左右交替。
清晰度：全局 2 倍超采样后直接输出，不做缩小。
"""

import math

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
BASE = '/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/'

S = 2
PAGE_W = 1180
CARD_W, CARD_H = 280, 200
CARD_GAP = 20
BOX_W, BOX_H, BOX_GAP = 52, 28, 5
COL_W, COL_GAP = 112, 24
STACK_BOTTOM = 172
STAGE_GAP = 26

STYLES = {
    'plain': ('#dfe7ff', '#1d3557'),
    'orange': ('#ff9944', 'white'),
    'green': ('#7ec8a0', '#0b3d2e'),
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


def _head(d, p1, p2, color, size=6):
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    size = _s(size)
    d.polygon([
        p2,
        (p2[0] - size * math.cos(ang - 0.42), p2[1] - size * math.sin(ang - 0.42)),
        (p2[0] - size * math.cos(ang + 0.42), p2[1] - size * math.sin(ang + 0.42)),
    ], fill=color)


def _arrow(d, p1, p2, color='#5a6577', width=1, head=5):
    d.line([p1, p2], fill=color, width=_s(width))
    _head(d, p1, p2, color, head)


def _draw_stack(d, col_left, label, elements, top_style=None):
    """elements 下标 0 为栈顶；各栈底部对齐。"""
    center = col_left + COL_W / 2
    d.text((_s(center), _s(45)), label, font=_f(11), fill='#2a3a5e', anchor='mt')

    box_left = center - BOX_W / 2
    if not elements:
        top = STACK_BOTTOM - BOX_H
        d.rounded_rectangle(
            [_s(box_left), _s(top), _s(box_left + BOX_W), _s(STACK_BOTTOM)],
            radius=_s(5), fill=STYLES['gray'][0], outline='#c9d2e3', width=_s(1),
        )
        d.text((_s(center), _s(top + BOX_H / 2)), '空',
               font=_f(11), fill='#9aa5b8', anchor='mm')
    else:
        total_h = len(elements) * BOX_H + (len(elements) - 1) * BOX_GAP
        first_top = STACK_BOTTOM - total_h
        for i, value in enumerate(elements):
            top = first_top + i * (BOX_H + BOX_GAP)
            style = top_style if i == 0 and top_style else 'plain'
            bg, fg = STYLES[style]
            outline = '#d48806' if style == 'orange' else '#4d9472' if style == 'green' else '#8fa4c9'
            d.rounded_rectangle(
                [_s(box_left), _s(top), _s(box_left + BOX_W), _s(top + BOX_H)],
                radius=_s(5), fill=bg, outline=outline,
                width=_s(2 if i == 0 and top_style else 1),
            )
            d.text((_s(center), _s(top + BOX_H / 2)), str(value),
                   font=_f(14), fill=fg, anchor='mm')

        color = '#d48806' if top_style == 'orange' else '#4d9472' if top_style == 'green' else '#7b8ba5'
        arrow_y = first_top + BOX_H / 2
        d.text((_s(box_left - 7), _s(arrow_y)), '栈顶',
               font=_f(9), fill=color, anchor='rm')

    d.line([(_s(center - 34), _s(STACK_BOTTOM + 7)),
            (_s(center + 34), _s(STACK_BOTTOM + 7))], fill='#c9d2e3', width=_s(1))
    d.text((_s(center), _s(STACK_BOTTOM + 10)), '栈底',
           font=_f(9), fill='#9aa5b8', anchor='mt')


def _stack_card(caption, detail, label_a, stack_a, label_b, stack_b,
                top_a=None, top_b=None, accent='#ff9944', transfer=False):
    im = Image.new('RGB', (_s(CARD_W), _s(CARD_H)), 'white')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, _s(CARD_W) - 1, _s(CARD_H) - 1],
                        radius=_s(9), fill='#ffffff', outline='#dfe6f0', width=_s(1))
    d.rounded_rectangle([0, _s(10), _s(4), _s(CARD_H - 10)], radius=_s(2), fill=accent)
    d.text((_s(14), _s(8)), caption, font=_f(12), fill='#2f3a4d')
    d.text((_s(14), _s(28)), detail, font=_f(9), fill='#6b788c')

    left_a = 15
    left_b = left_a + COL_W + COL_GAP
    _draw_stack(d, left_a, label_a, stack_a, top_a)
    _draw_stack(d, left_b, label_b, stack_b, top_b)

    if transfer:
        x1 = left_a + COL_W + 4
        x2 = left_b - 5
        if stack_b:
            total_h = len(stack_b) * BOX_H + (len(stack_b) - 1) * BOX_GAP
            y = STACK_BOTTOM - total_h + BOX_H / 2
        else:
            y = 120
        d.line([(_s(x1), _s(y)), (_s(x2), _s(y))], fill='#d48806', width=_s(2))
        _head(d, (_s(x1), _s(y)), (_s(x2), _s(y)), '#d48806', 5)
    return im


def _stage(title, color, cards):
    """一个阶段：色条标题 + 一行卡片（左对齐）。"""
    body_w = len(cards) * CARD_W + (len(cards) - 1) * CARD_GAP

    head = Image.new('RGB', (_s(PAGE_W), _s(24)), 'white')
    hd = ImageDraw.Draw(head)
    hd.rounded_rectangle([0, _s(5), _s(4), _s(19)], radius=_s(2), fill=color)
    hd.text((_s(13), _s(3)), title, font=_f(14), fill='#26313f')

    row = Image.new('RGB', (_s(PAGE_W), _s(CARD_H)), 'white')
    x = 0
    for card in cards:
        row.paste(card, (x, 0))
        x += _s(CARD_W + CARD_GAP)

    gap = _s(8)
    canvas = Image.new('RGB', (_s(PAGE_W), _s(24) + gap + _s(CARD_H)), 'white')
    canvas.paste(head, (0, 0))
    canvas.paste(row, (0, _s(24) + gap))
    return canvas


def _finish(stages, filename, legend):
    """垂直拼接各阶段，底部加一行图例，直接按 2 倍输出。"""
    gap = _s(STAGE_GAP)
    total_h = sum(st.height for st in stages) + gap * (len(stages) - 1)
    body = Image.new('RGB', (_s(PAGE_W), total_h), 'white')
    y = 0
    for st in stages:
        body.paste(st, (0, y))
        y += st.height + gap

    legend_w = _tw(legend, 11)
    w = max(_s(PAGE_W), legend_w) + _s(28)
    canvas = Image.new('RGB', (w, total_h + _s(40)), 'white')
    canvas.paste(body, ((w - _s(PAGE_W)) // 2, _s(4)))
    d = ImageDraw.Draw(canvas)
    d.text((w / 2, total_h + _s(15)), legend,
           font=_f(11), fill='#5a6577', anchor='mt')
    canvas.save(BASE + filename)
    print(f'已生成 {filename}（{canvas.width}×{canvas.height}）')


def build_min_stack_plot():
    s1 = [
        dict(cap='初始：A、B 均为空', detail='准备 push 3；空栈时两栈同步写入',
             a=[], b=[], accent='#8fa4c9'),
        dict(cap='push(3)：A 为空', detail='A、B 都入 3；最小值 = B 栈顶 = 3',
             a=[3], b=[3], top_a='orange', top_b='orange'),
        dict(cap='push(2)：2 ≤ B 栈顶 3', detail='A、B 都入 2；最小值更新为 2',
             a=[2, 3], b=[2, 3], top_a='orange', top_b='orange'),
        dict(cap='push(5)：5 > B 栈顶 2', detail='只入 A，B 不变；最小值仍为 2',
             a=[5, 2, 3], b=[2, 3], top_a='orange'),
    ]
    s2 = [
        dict(cap='getMin()：读取 B 栈顶', detail='返回 2；A、B 都不变',
             a=[5, 2, 3], b=[2, 3], top_b='green', accent='#4d9472'),
        dict(cap='pop()：A 栈顶 5 ≠ B 栈顶 2', detail='只弹 A，B 不弹；最小值仍为 2',
             a=[2, 3], b=[2, 3]),
        dict(cap='getMin()：再次读取 B 栈顶', detail='仍返回 2，5 从未进入 B，不影响最小值',
             a=[2, 3], b=[2, 3], top_b='green', accent='#4d9472'),
    ]
    s3 = [
        dict(cap='push(1)：1 ≤ B 栈顶 2', detail='A、B 都入 1；最小值变为 1',
             a=[1, 2, 3], b=[1, 2, 3], top_a='orange', top_b='orange'),
        dict(cap='getMin()：再次读取 B 栈顶', detail='返回 1；无需扫描数据栈 A',
             a=[1, 2, 3], b=[1, 2, 3], top_b='green', accent='#4d9472'),
        dict(cap='pop()：A、B 栈顶都为 1', detail='两栈同步弹出 1；最小值还原为 2',
             a=[2, 3], b=[2, 3]),
        dict(cap='pop()：A、B 栈顶都为 2', detail='两栈同步弹出 2；最终最小值 = 3',
             a=[3], b=[3]),
    ]

    def make(group):
        return [
            _stack_card(s['cap'], s['detail'], '栈 A · 数据栈', s['a'],
                        '栈 B · 最小值栈', s['b'], s.get('top_a'), s.get('top_b'),
                        s.get('accent', '#ff9944'))
            for s in group
        ]

    stages = [
        _stage('阶段 1 · 入栈 push：B 是否同步入栈', '#ff9944', make(s1)),
        _stage('阶段 2 · 取最小值 getMin 与出栈 pop', '#4d9472', make(s2)),
        _stage('阶段 3 · 出现更小值后的入栈与出栈', '#7a6bb5', make(s3)),
    ]
    _finish(
        stages, 'min_stack.png',
        '橙 = 本次入栈    绿 = getMin 结果    val ≤ B 栈顶时 B 同步入栈；'
        'A、B 栈顶相同时 B 同步出栈；getMin 直接读 B 栈顶，O(1)',
    )


def build_queue_by_stack_plot():
    s1 = [
        dict(cap='初始：A、B 均为空', detail='准备入队 1、2、3；入队只压栈 A',
             a=[], b=[], accent='#8fa4c9'),
        dict(cap='enqueue(1)：压入栈 A', detail='B 保持为空；队首、队尾都是 1',
             a=[1], b=[], top_a='orange'),
        dict(cap='enqueue(2)：继续压入栈 A', detail='A 栈顶为 2；队列顺序 1、2',
             a=[2, 1], b=[], top_a='orange'),
        dict(cap='enqueue(3)：继续压入栈 A', detail='A 栈顶为 3；出队前需要倒栈',
             a=[3, 2, 1], b=[], top_a='orange'),
    ]
    s2 = [
        dict(cap='dequeue 准备：B 为空', detail='A 依次弹出 3、2、1 压入 B；B 栈顶 = 队首 1',
             a=[], b=[1, 2, 3], top_b='orange', transfer=True),
        dict(cap='dequeue：弹出 B 栈顶 1', detail='出队结果 = 1；新的队首为 2',
             a=[], b=[2, 3]),
    ]
    s3 = [
        dict(cap='enqueue(4)：只压入栈 A', detail='B 仍有元素，此时不能倒栈',
             a=[4], b=[2, 3], top_a='orange'),
        dict(cap='enqueue(5)：继续压入栈 A', detail='队列顺序为 2、3、4、5',
             a=[5, 4], b=[2, 3], top_a='orange'),
    ]
    s4 = [
        dict(cap='dequeue：B 非空，弹栈顶 2', detail='出队结果 = 2；新的队首为 3',
             a=[5, 4], b=[3]),
        dict(cap='dequeue：B 非空，弹栈顶 3', detail='出队结果 = 3；此时 B 已空',
             a=[5, 4], b=[]),
        dict(cap='dequeue：B 为空，再倒栈后弹 4', detail='A 的 5、4 倒入 B，弹出 4；队列只剩 5',
             a=[], b=[5], top_b='orange', transfer=True),
    ]

    def make(group):
        return [
            _stack_card(s['cap'], s['detail'], '栈 A · 入队', s['a'],
                        '栈 B · 出队', s['b'], s.get('top_a'), s.get('top_b'),
                        s.get('accent', '#ff9944'), s.get('transfer', False))
            for s in group
        ]

    stages = [
        _stage('阶段 1 · 入队 enqueue：全部压入栈 A', '#ff9944', make(s1)),
        _stage('阶段 2 · 出队 dequeue：B 为空时整体倒栈', '#4d9472', make(s2)),
        _stage('阶段 3 · 继续入队：B 非空时只压 A', '#7a6bb5', make(s3)),
        _stage('阶段 4 · 继续出队：B 非空直接弹，弹空再倒', '#3f7fbf', make(s4)),
    ]
    _finish(
        stages, 'queue_by_stack.png',
        '橙 = 本次入栈或倒栈后的栈顶    入队只压 A；B 为空才把 A 整体倒入 B，'
        'B 非空直接弹栈顶；出队顺序 1 → 2 → 3 → 4，符合 FIFO',
    )


if __name__ == '__main__':
    build_min_stack_plot()
    build_queue_by_stack_plot()
