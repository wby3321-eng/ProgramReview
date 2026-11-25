"""生成排序算法相关的原理示意图。"""

import io
from collections import defaultdict

from graphviz import Digraph
from PIL import Image

FONT = 'PingFang SC'
BASE = '/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/'


def _row_png(values, caption, highlights=(), greens=(), purples=()):
    """画一行数组：橙色 = 去程比较/冒泡，紫色 = 回程比较，绿色 = 已有序，蓝色 = 待排序。"""
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', nodesep='0.12', ranksep='0.05', pad='0.05')
    dot.attr('node', fontname=FONT, penwidth='0')

    with dot.subgraph() as c:
        c.attr(rank='same')
        for j, v in enumerate(values):
            if j in highlights:
                fill, fc = '#ff7744', 'white'
            elif j in purples:
                fill, fc = '#7766cc', 'white'
            elif j in greens:
                fill, fc = '#7ec8a0', '#0b3d2e'
            else:
                fill, fc = '#dfe7ff', '#1d3557'
            c.node(str(j), str(v), shape='box', style='filled,rounded',
                   fillcolor=fill, fontcolor=fc, fontsize='15',
                   width='0.72', height='0.72', fixedsize='true')
        for j in range(len(values) - 1):
            c.edge(str(j), str(j + 1), style='invis')

    dot.attr(label=caption, labelloc='b', fontname=FONT, fontsize='11', fontcolor='#555')
    return Image.open(io.BytesIO(dot.pipe(format='png'))).convert('RGBA')


def _stack(images, gap=12, margin=18):
    """把多张行图垂直堆叠并居中对齐。"""
    height = sum(im.height for im in images) + gap * (len(images) - 1) + margin * 2
    width = max(im.width for im in images) + margin * 2
    canvas = Image.new('RGBA', (width, height), 'white')
    y = margin
    for im in images:
        x = (width - im.width) // 2
        canvas.alpha_composite(im, (x, y))
        y += im.height + gap
    return canvas


def _text_png(text, fontsize, color):
    """用 graphviz 渲染一行文字（中文稳定显示），返回 PIL 图。"""
    dot = Digraph(format='png')
    dot.attr(bgcolor='white', pad='0.1')
    dot.node('t', text, shape='plain', fontname=FONT,
             fontsize=str(fontsize), fontcolor=color)
    return Image.open(io.BytesIO(dot.pipe(format='png'))).convert('RGBA')


def _add_text_bar(img, top_text, bottom_text):
    """在图的顶部和底部各加一行文字说明。"""
    top = _text_png(top_text, 24, '#1d3557')
    bot = _text_png(bottom_text, 12, '#555')
    width = max(img.width, top.width, bot.width)
    height = img.height + top.height + bot.height + 20
    canvas = Image.new('RGBA', (width, height), 'white')
    canvas.alpha_composite(top, ((width - top.width) // 2, 8))
    canvas.alpha_composite(img, ((width - img.width) // 2, top.height + 10))
    canvas.alpha_composite(bot, ((width - bot.width) // 2,
                                 top.height + 10 + img.height + 6))
    return canvas.convert('RGB')


def build_bubble_sort_plot():
    """冒泡排序原理：左栏 = 每轮整体演变，右栏 = 第 1 轮逐次比较交换细节。"""
    overview = [
        ([5, 3, 8, 6, 2, 7], '初始数组', (), ()),
        ([3, 5, 6, 2, 7, 8], '第 1 轮：8 冒泡到末尾', (5,), (5,)),
        ([3, 5, 2, 6, 7, 8], '第 2 轮：7 冒泡到末尾', (4,), (4, 5)),
        ([3, 2, 5, 6, 7, 8], '第 3 轮：6 冒泡到末尾', (3,), (3, 4, 5)),
        ([2, 3, 5, 6, 7, 8], '第 4 轮：5 冒泡到末尾', (2,), (2, 3, 4, 5)),
        ([2, 3, 5, 6, 7, 8], '第 5 轮：无交换，排序完成（可提前结束）', (), (0, 1, 2, 3, 4, 5)),
    ]
    left = _stack([_row_png(*s) for s in overview])

    detail = [
        ([5, 3, 8, 6, 2, 7], '比较 5 与 3，逆序 → 交换', (0, 1), ()),
        ([3, 5, 8, 6, 2, 7], '比较 5 与 8，顺序正确，不交换', (1, 2), ()),
        ([3, 5, 8, 6, 2, 7], '比较 8 与 6，逆序 → 交换', (2, 3), ()),
        ([3, 5, 6, 8, 2, 7], '比较 8 与 2，逆序 → 交换', (3, 4), ()),
        ([3, 5, 6, 2, 8, 7], '比较 8 与 7，逆序 → 交换', (4, 5), ()),
        ([3, 5, 6, 2, 7, 8], '本轮结束：8 冒泡到末尾（已有序，绿色）', (), (5,)),
    ]
    right = _stack([_row_png(*s) for s in detail])

    # 左右拼接
    gap, margin = 40, 30
    content_h = max(left.height, right.height)
    content_w = left.width + right.width + gap + margin * 2
    content = Image.new('RGBA', (content_w, content_h + margin * 2), 'white')
    content.alpha_composite(left, (margin, margin + (content_h - left.height) // 2))
    content.alpha_composite(right, (margin + left.width + gap,
                                    margin + (content_h - right.height) // 2))

    final = _add_text_bar(
        content,
        '冒泡排序原理 Bubble Sort',
        '橙色 = 正在比较 / 冒泡的元素    绿色 = 已有序（下一轮不再参与）    蓝色 = 待排序    '
        '时间复杂度 O(n²)，空间 O(1)，稳定',
    )
    final.save(BASE + 'bubble_sort.png')


def _hstack(left, right, gap=40, margin=30):
    """左右拼接两张图，居中对齐。"""
    height = max(left.height, right.height)
    width = left.width + right.width + gap + margin * 2
    canvas = Image.new('RGBA', (width, height + margin * 2), 'white')
    canvas.alpha_composite(left, (margin, margin + (height - left.height) // 2))
    canvas.alpha_composite(right, (margin + left.width + gap,
                                   margin + (height - right.height) // 2))
    return canvas


def build_bubble_sort_optimized_plot():
    """冒泡排序优化：左栏 = 朴素版（跑满 n-1 轮），右栏 = 优化版（本轮无交换则 break 外层循环）。"""
    naive = [
        ([2, 1, 3, 4, 6, 5], '初始数组', (), ()),
        ([1, 2, 3, 4, 5, 6], '第 1 轮：已有序', (), (0, 1, 2, 3, 4, 5)),
        ([1, 2, 3, 4, 5, 6], '第 2 轮：仍比较到末尾，无变化（空跑）', (), (0, 1, 2, 3, 4, 5)),
        ([1, 2, 3, 4, 5, 6], '第 3 轮：无变化（空跑）', (), (0, 1, 2, 3, 4, 5)),
        ([1, 2, 3, 4, 5, 6], '第 4 轮：无变化（空跑）', (), (0, 1, 2, 3, 4, 5)),
        ([1, 2, 3, 4, 5, 6], '第 5 轮：完成（跑满 n-1=5 轮）', (), (0, 1, 2, 3, 4, 5)),
    ]
    left = _stack([_row_png(*s) for s in naive])

    optimized = [
        ([2, 1, 3, 4, 6, 5], '初始数组', (), ()),
        ([1, 2, 3, 4, 5, 6], '第 1 轮：发生过交换，swapped = True，继续', (), (0, 1, 2, 3, 4, 5)),
        ([1, 2, 3, 4, 5, 6], '第 2 轮：一次交换都没发生，swapped = False → break 跳出外层循环', (), (0, 1, 2, 3, 4, 5)),
    ]
    right = _stack([_row_png(*s) for s in optimized])

    content = _hstack(left, right)
    final = _add_text_bar(
        content,
        '冒泡排序优化 Bubble Sort Optimized',
        '朴素版：固定跑满 n-1 轮（此处 5 轮，后 4 轮空跑）    '
        '优化版：每轮开始置 swapped = False，发生交换则置 True；一轮结束若 swapped 仍为 False，'
        '说明数组已有序，直接 break 跳出最外层循环（此处仅 2 轮）',
    )
    final.save(BASE + 'bubble_sort_optimized.png')


def build_cocktail_sort_plot():
    """鸡尾酒排序：数组 [12,3,4,5,6,8,1] 大部分有序，仅两端错位，展示双向冒泡的优势。"""
    # 左栏：每轮整体演变
    overview = [
        ([12, 3, 4, 5, 6, 8, 1], '初始数组（大部分有序，仅两端 12、1 错位）', (), ()),
        ([3, 4, 5, 6, 8, 1, 12], '第 1 轮 → 从左到右：12 冒泡到右端', (6,), (6,)),
        ([1, 3, 4, 5, 6, 8, 12], '第 1 轮 ← 从右到左：1 冒泡到左端', (0,), (0, 6)),
        ([1, 3, 4, 5, 6, 8, 12], '第 2 轮 → 从左到右扫描中间：无交换', (), (0, 6)),
        ([1, 3, 4, 5, 6, 8, 12], '第 2 轮 ← 从右到左扫描中间：无交换 → 完成', (), (0, 1, 2, 3, 4, 5, 6)),
    ]
    left = _stack([_row_png(*s) for s in overview])

    # 右栏：第 1 轮逐次比较细节（去程橙色 →，回程紫色 ←）
    detail = [
        # → 去程（左→右）：12 逐步右移
        ([3, 12, 4, 5, 6, 8, 1], '→ 比较 12 与 3，逆序 → 交换', (0, 1), ()),
        ([3, 4, 12, 5, 6, 8, 1], '→ 比较 12 与 4，逆序 → 交换', (1, 2), ()),
        ([3, 4, 5, 12, 6, 8, 1], '→ 比较 12 与 5，逆序 → 交换', (2, 3), ()),
        ([3, 4, 5, 6, 12, 8, 1], '→ 比较 12 与 6，逆序 → 交换', (3, 4), ()),
        ([3, 4, 5, 6, 8, 12, 1], '→ 比较 12 与 8，逆序 → 交换', (4, 5), ()),
        ([3, 4, 5, 6, 8, 1, 12], '→ 比较 12 与 1，逆序 → 交换（去程结束）', (5, 6), (6,)),
        # ← 回程（右→左）：1 逐步左移
        ([3, 4, 5, 6, 1, 8, 12], '← 比较 8 与 1，逆序 → 交换', (), (6,), (4, 5)),
        ([3, 4, 5, 1, 6, 8, 12], '← 比较 6 与 1，逆序 → 交换', (), (6,), (3, 4)),
        ([3, 4, 1, 5, 6, 8, 12], '← 比较 5 与 1，逆序 → 交换', (), (6,), (2, 3)),
        ([3, 1, 4, 5, 6, 8, 12], '← 比较 4 与 1，逆序 → 交换', (), (6,), (1, 2)),
        ([1, 3, 4, 5, 6, 8, 12], '← 比较 3 与 1，逆序 → 交换（回程结束）', (), (0, 6), (0, 1)),
    ]
    right = _stack([_row_png(*s) for s in detail])

    content = _hstack(left, right)
    final = _add_text_bar(
        content,
        '鸡尾酒排序 Cocktail Sort（双向冒泡）· 大部分有序场景',
        '橙色 → 从左到右扫描（去程，最大值往右冒泡）    '
        '紫色 ← 从右到左扫描（回程，最小值往左冒泡）    绿色 = 已有序    '
        '此例：第 1 轮把 12 推到右端、1 推到左端，第 2 轮双向均无交换即结束（仅 2 轮）；'
        '普通冒泡因 1 在末尾每轮只能左移一位，需 6 轮',
    )
    final.save(BASE + 'cocktail_sort.png')


def _qs_row(values, caption, pivot=-1, pointers=None, highlights=(),
            lt_zone=(), gt_zone=()):
    """画一行数组。

    金色 = 基准 pivot；橙色边框 = 正在比较/交换；
    浅绿底 = 小于 pivot 的区域；浅蓝底 = 大于等于 pivot 的区域；白底 = 未处理；
    下方可挂指针标签（left/right/mark/j）。
    """
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', nodesep='0.1', ranksep='0.08', pad='0.05')
    dot.attr('node', fontname=FONT, penwidth='0')
    pointers = pointers or {}

    with dot.subgraph() as c:
        c.attr(rank='same')
        for j, v in enumerate(values):
            if j == pivot:
                fill, fc, pw = '#f4c542', '#5a3e00', '2'
            elif j in highlights:
                fill, fc, pw = '#ff7744', 'white', '2'
            elif j in lt_zone:
                fill, fc, pw = '#c8e6c9', '#1b5e20', '0'
            elif j in gt_zone:
                fill, fc, pw = '#dfe7ff', '#1d3557', '0'
            else:
                fill, fc, pw = '#ffffff', '#555555', '0'
            c.node(f'b{j}', str(v), shape='box', style='filled,rounded',
                   fillcolor=fill, fontcolor=fc, fontsize='15',
                   width='0.72', height='0.72', fixedsize='true', penwidth=pw)
        for j in range(len(values) - 1):
            c.edge(f'b{j}', f'b{j + 1}', style='invis')

    # 指针标签：挂在对应格子下方
    pcolor = {'left': '#ff7744', 'right': '#7766cc', 'mark': '#2a9d8f', 'j': '#e76f51'}
    for label, idx in pointers.items():
        pname = f'p_{label}'
        dot.node(pname, label, shape='plain', fontname=FONT,
                 fontsize='12', fontcolor=pcolor.get(label, '#555'))
        dot.edge(f'b{idx}', pname, style='invis')

    dot.attr(label=caption, labelloc='b', fontname=FONT, fontsize='11', fontcolor='#555')
    return Image.open(io.BytesIO(dot.pipe(format='png'))).convert('RGBA')


def _hoare_partition(arr, lo, hi):
    """Hoare 分区（双边循环）：基准取 arr[lo]，先移 right 再移 left，相遇处即基准最终位置。"""
    pivot = arr[lo]
    left, right = lo, hi
    while left < right:
        while left < right and arr[right] >= pivot:  # 先移动右指针，找 < pivot
            right -= 1
        while left < right and arr[left] <= pivot:   # 右指针停住后再移左指针，找 > pivot
            left += 1
        if left < right:
            arr[left], arr[right] = arr[right], arr[left]
    arr[lo], arr[left] = arr[left], arr[lo]
    return left


def _lomuto_partition(arr, lo, hi):
    """Lomuto 分区（单边循环）：基准取 arr[lo]（首元素），mark 为小于区右边界，从 lo 起。"""
    pivot = arr[lo]
    mark = lo  # 小于基准区域的右边界，初始在起始位置
    for j in range(lo + 1, hi + 1):  # j 从基准元素之后开始遍历
        if arr[j] < pivot:
            mark += 1
            arr[mark], arr[j] = arr[j], arr[mark]
    arr[lo], arr[mark] = arr[mark], arr[lo]
    return mark


def _hoare_partition_traced(arr, lo, hi):
    """Hoare 分区（先右后左），沿途记录每一步。返回 (基准位置, steps)。

    规则：right 先左移找 < pivot 的元素；right 停住后 left 再右移找 > pivot；
    两者未相遇则交换，再回到「先移 right」。最终 left == right 相遇处就是基准最终位置。
    每个 step = (values, pointers, highlights, pivot_idx, caption)。
    """
    pivot = arr[lo]
    left, right = lo, hi
    steps = []

    def snap(ptr, hl, cap, pv=lo):
        steps.append((list(arr), dict(ptr), set(hl), pv, cap))

    snap({'left': left, 'right': right}, set(),
         f'当前：基准={pivot}(idx{lo})，left={lo}、right={hi}\n'
         f'下一步：先移 right，向左找 <{pivot} 的元素')
    while left < right:
        while left < right and arr[right] >= pivot:  # 先移动右指针
            right -= 1
        if left == right:
            break
        snap({'left': left, 'right': right}, {right},
             f'当前：right 停在 idx{right}（<{pivot}）\n'
             f'下一步：right 不动，移 left 向右找 >{pivot} 的元素')
        while left < right and arr[left] <= pivot:   # 再移动左指针
            left += 1
        if left == right:
            break
        snap({'left': left, 'right': right}, {left},
             f'当前：left 停在 idx{left}（>{pivot}）\n'
             f'下一步：交换 idx{left} 与 idx{right}')
        arr[left], arr[right] = arr[right], arr[left]
        snap({'left': left, 'right': right}, set(),
             f'当前：交换完成，left={left}、right={right}，未相遇\n'
             f'下一步：回到开头，继续先移 right')
    snap({'left': left, 'right': right}, {left},
         f'当前：left 与 right 在 idx{left} 相遇\n'
         f'下一步：相遇处即基准位置，把基准 idx{lo} 换到 idx{left}')
    arr[lo], arr[left] = arr[left], arr[lo]
    snap({}, {lo, left} if lo != left else {left},
         f'当前：基准 {pivot} 已归位 idx{left} 并锁定\n'
         f'下一步：递归处理左[{lo}..{left - 1}]、右[{left + 1}..{hi}]', pv=left)
    return left, steps


def _lomuto_partition_traced(arr, lo, hi):
    """Lomuto 分区（基准取首元素），mark 为小于区右边界，沿途记录每一步。返回 (基准位置, steps)。"""
    pivot = arr[lo]
    mark = lo  # 小于基准区域的右边界，初始在起始位置
    steps = []

    def snap(ptr, hl, cap, pv=lo):
        steps.append((list(arr), dict(ptr), set(hl), pv, cap))

    snap({'mark': mark, 'j': lo}, set(),
         f'当前：基准={pivot}(idx{lo})，mark={lo} 指向起始位置\n'
         f'下一步：j 从基准之后 idx{lo + 1} 开始遍历，<{pivot} 的放进 mark 区')
    for j in range(lo + 1, hi + 1):
        if arr[j] < pivot:
            mark += 1
            snap({'mark': mark, 'j': j}, {mark, j},
                 f'当前：j={j} 检查值{arr[j]} < {pivot}，mark 右移到 {mark}\n'
                 f'下一步：交换 idx{mark} 与 idx{j}，把 {arr[j]} 移入小于区')
            arr[mark], arr[j] = arr[j], arr[mark]
            snap({'mark': mark, 'j': j}, set(),
                 f'当前：交换完成，小于区扩到 idx{mark}\n'
                 f'下一步：j 右移继续检查')
        else:
            snap({'mark': mark, 'j': j}, set(),
                 f'当前：j={j} 检查值{arr[j]} ≥ {pivot}\n'
                 f'下一步：跳过，mark 不动，j 右移')
    snap({'mark': mark}, set(),
         f'当前：j 遍历完 [{lo + 1}..{hi}]，mark={mark} 是小于区右边界\n'
         f'下一步：把基准 idx{lo} 换到 idx{mark}')
    arr[lo], arr[mark] = arr[mark], arr[lo]
    snap({}, {lo, mark} if lo != mark else {mark},
         f'当前：基准 {pivot} 已归位 idx{mark} 并锁定\n'
         f'下一步：递归处理左[{lo}..{mark - 1}]、右[{mark + 1}..{hi}]', pv=mark)
    return mark, steps


def _trace_quick_sort(arr, partition, pivot_side):
    """递归运行快速排序，记录每一步快照。

    返回列表，每条记录 = (values, depth, active, pivot, caption, locked)：
    values=当前数组副本, depth=递归深度, active=(lo,hi) 或 None,
    pivot=当前基准下标或 -1, caption=说明, locked=已归位锁定的下标集合。
    pivot_side: 'first'（基准取首元素）；两种分区现在都用首元素基准。
    """
    arr = list(arr)
    recs = []
    locked = set()

    def qs(lo, hi, depth):
        indent = '　' * depth  # 全角空格缩进，体现递归层级
        if lo > hi:
            return
        if lo == hi:
            locked.add(lo)
            recs.append((list(arr), depth, None, -1,
                         f'{indent}深度{depth} · 区间[{lo}..{hi}] 单元素 {arr[lo]}，直接锁定（已有序）',
                         frozenset(locked)))
            return
        pivot_idx = lo if pivot_side == 'first' else hi
        side_word = '首' if pivot_side == 'first' else '末'
        recs.append((list(arr), depth, (lo, hi), pivot_idx,
                     f'{indent}深度{depth} · 分区[{lo}..{hi}]，选基准 {arr[pivot_idx]}（{side_word}元素）',
                     frozenset(locked)))
        p = partition(arr, lo, hi)
        locked.add(p)
        recs.append((list(arr), depth, (lo, hi), p,
                     f'{indent}深度{depth} · 基准 {arr[p]} 归位到 idx{p} 并锁定 → 左[{lo}..{p - 1}]、右[{p + 1}..{hi}] 待递归',
                     frozenset(locked)))
        qs(lo, p - 1, depth + 1)
        qs(p + 1, hi, depth + 1)

    qs(0, len(arr) - 1, 0)
    recs.append((list(arr), 0, None, -1,
                 '✓ 全部元素已锁定，排序完成：' + ' '.join(map(str, arr)),
                 frozenset(range(len(arr)))))
    return recs


def _full_sort_row(values, caption, active=None, pivot=-1, locked=()):
    """画完整流程的一行：绿=已锁定归位，金=当前基准，蓝=活动子区间，白=其他待处理。"""
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', nodesep='0.1', ranksep='0.08', pad='0.05')
    dot.attr('node', fontname=FONT, penwidth='0')
    locked = set(locked)

    with dot.subgraph() as c:
        c.attr(rank='same')
        for j, v in enumerate(values):
            if j in locked:
                fill, fc, pw = '#7ec8a0', '#0b3d2e', '0'
            elif j == pivot:
                fill, fc, pw = '#f4c542', '#5a3e00', '2'
            elif active and active[0] <= j <= active[1]:
                fill, fc, pw = '#dfe7ff', '#1d3557', '0'
            else:
                fill, fc, pw = '#ffffff', '#888888', '0'
            c.node(f'b{j}', str(v), shape='box', style='filled,rounded',
                   fillcolor=fill, fontcolor=fc, fontsize='15',
                   width='0.72', height='0.72', fixedsize='true', penwidth=pw)
        for j in range(len(values) - 1):
            c.edge(f'b{j}', f'b{j + 1}', style='invis')

    dot.attr(label=caption, labelloc='b', fontname=FONT, fontsize='11', fontcolor='#555')
    return Image.open(io.BytesIO(dot.pipe(format='png'))).convert('RGBA')


def _trace_qs_tree(arr, partition, pivot_side):
    """递归运行快速排序，返回横向展开所需的节点表与衍生边。

    节点：{id, steps, active, caption, locked, depth}
    steps 里每条 = (values, pointers, highlights, pivot_idx, caption, locked_set)：
    values=该步数组副本, pointers={标签:下标}, highlights=正在交换的下标,
    pivot_idx=基准当前下标, caption=该步说明, locked_set=该步时已锁定的下标。
    边：(parent_id, child_id, label)。
    depth = 递归深度（0 起），同 depth 属同一轮，渲染时纵向对齐成一列。
    """
    arr = list(arr)
    nodes = []
    edges = []
    locked = set()
    counter = [0]

    def add_node(steps, active, caption, depth, parent_id, edge_label):
        nid = counter[0]
        counter[0] += 1
        nodes.append({'id': nid, 'steps': steps, 'active': active,
                      'caption': caption, 'locked': frozenset(locked),
                      'depth': depth})
        if parent_id is not None:
            edges.append((parent_id, nid, edge_label))
        return nid

    def qs(lo, hi, depth, parent_id, edge_label):
        rnd = depth + 1  # 第几轮
        if lo > hi:
            return
        if lo == hi:
            locked.add(lo)
            step = (list(arr), {}, {lo}, lo,
                    f'当前：区间[{lo}..{lo}] 只有一个元素 {arr[lo]}\n'
                    f'下一步：直接锁定（已有序）', frozenset(locked))
            add_node([step], None, f'第{rnd}轮 [{lo}] 单元素锁定',
                     depth, parent_id, edge_label)
            return
        ancestor = frozenset(locked)  # 本轮分区前已锁定的下标
        p, steps = partition(arr, lo, hi)
        locked.add(p)
        final = frozenset(locked)  # 本轮分区后（含本次基准）
        # 给每一步标注它当时的锁定集合：除最后一步外都还是 ancestor，最后一步含 p
        ann = []
        for i, st in enumerate(steps):
            lk = final if i == len(steps) - 1 else ancestor
            ann.append(st + (lk,))
        nid = add_node(ann, (lo, hi),
                       f'第{rnd}轮 [{lo}..{hi}] 基准归位 idx{p}',
                       depth, parent_id, edge_label)
        qs(lo, p - 1, depth + 1, nid, f'左 [{lo}..{p - 1}]')
        qs(p + 1, hi, depth + 1, nid, f'右 [{p + 1}..{hi}]')

    qs(0, len(arr) - 1, 0, None, None)
    max_depth = max(n['depth'] for n in nodes) if nodes else 0
    finish_step = (list(arr), {}, set(), -1,
                   '当前：所有元素已归位锁定\n下一步：排序完成',
                   frozenset(range(len(arr))))
    add_node([finish_step], None, '✓ 排序完成：' + ' '.join(map(str, arr)),
             max_depth + 1, None, None)
    return nodes, edges


_PCOLOR = {'left': '#ff7744', 'right': '#7766cc', 'mark': '#2a9d8f', 'j': '#e76f51'}


def _html_escape(s):
    """转义 graphviz HTML-like label 里的特殊字符。"""
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _format_caption(cap):
    """注解按 \\n 分段：第 1 段「当前状态」深灰，第 2 段「下一步」青绿。

    每段严格保持一行，不做换行。
    """
    parts = cap.split('\n')
    colors = ['#333333', '#2a9d8f', '#666666']
    out = []
    for i, p in enumerate(parts):
        c = colors[i] if i < len(colors) else '#666'
        out.append(f'<FONT COLOR="{c}">{_html_escape(p)}</FONT>')
    return '<BR/>'.join(out)


def _cell(v, bg, fc):
    return (f'<TD BGCOLOR="{bg}" WIDTH="36" HEIGHT="28" FIXEDSIZE="TRUE" BORDER="1">'
            f'<FONT FACE="{FONT}" POINT-SIZE="12" COLOR="{fc}">{v}</FONT></TD>')


def _array_html_label(node):
    """把一个节点渲染成 graphviz HTML 表格：每一步 = 数组行 + 指针行 + 说明行。"""
    steps = node['steps']
    active = node['active']
    n = len(steps[0][0])
    rows_html = []
    # 节点标题（第几轮）
    rows_html.append(
        f'<TR><TD COLSPAN="{n}" BORDER="0" ALIGN="CENTER">'
        f'<FONT FACE="{FONT}" POINT-SIZE="11" COLOR="#1d3557"><B>{_html_escape(node["caption"])}</B></FONT>'
        f'</TD></TR>'
    )
    for values, pointers, highlights, pv, cap, lk in steps:
        lk = set(lk)
        # 数组行
        cells = []
        for j, v in enumerate(values):
            if j in lk:
                bg, fc = '#7ec8a0', '#0b3d2e'
            elif j == pv:
                bg, fc = '#f4c542', '#5a3e00'
            elif j in highlights:
                bg, fc = '#ff7744', 'white'
            elif active and active[0] <= j <= active[1]:
                bg, fc = '#dfe7ff', '#1d3557'
            else:
                bg, fc = '#ffffff', '#888'
            cells.append(_cell(v, bg, fc))
        rows_html.append(f'<TR>{"".join(cells)}</TR>')
        # 指针行：在对应下标下方放彩色标签
        pcells = []
        for j in range(n):
            labels = [lab for lab, idx in pointers.items() if idx == j]
            txt = ''.join(
                f'<FONT FACE="{FONT}" POINT-SIZE="9" COLOR="{_PCOLOR.get(lab, "#555")}">{_html_escape(lab)}</FONT>'
                for lab in labels)
            pcells.append(f'<TD WIDTH="36" BORDER="0" ALIGN="CENTER">{txt}</TD>')
        rows_html.append(f'<TR>{"".join(pcells)}</TR>')
        # 说明行（当前状态 + 下一步，两段不同颜色）
        rows_html.append(
            f'<TR><TD COLSPAN="{n}" BORDER="0" ALIGN="LEFT">'
            f'<FONT FACE="{FONT}" POINT-SIZE="9">{_format_caption(cap)}</FONT>'
            f'</TD></TR>'
        )
    return (f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="1">'
            + ''.join(rows_html) + '</TABLE>>')


def _render_expand_tree(nodes, edges, title, legend, filename):
    """把递归分区树横向（从左到右）渲染成 PNG。"""
    dot = Digraph(format='png')
    dot.attr(rankdir='LR', splines='polyline', nodesep='0.35', ranksep='0.8',
             pad='0.15', bgcolor='white')
    dot.attr('node', shape='plain', fontname=FONT)
    dot.attr('edge', fontname=FONT, fontsize='10', color='#aaa',
             arrowsize='0.7', fontcolor='#777')

    by_depth = defaultdict(list)
    for n in nodes:
        by_depth[n['depth']].append(n['id'])
        dot.node(str(n['id']), _array_html_label(n))

    # 同深度（同一轮）节点纵向对齐成一列
    for depth in sorted(by_depth):
        ids = by_depth[depth]
        with dot.subgraph() as s:
            s.attr(rank='same')
            for i in ids:
                s.node(str(i))

    for pid, cid, label in edges:
        dot.edge(str(pid), str(cid), label=label)

    # 完成节点没有入边，graphviz 会把它放到最左；用不可见边从所有叶子连过去，约束到最右
    finish_id = max(nodes, key=lambda n: n['depth'])['id']
    has_child = {pid for pid, _, _ in edges}
    leaves = [n['id'] for n in nodes if n['id'] != finish_id and n['id'] not in has_child]
    for lid in leaves:
        dot.edge(str(lid), str(finish_id), style='invis')

    img = Image.open(io.BytesIO(dot.pipe(format='png', quiet=True))).convert('RGBA')
    final = _add_text_bar(img, title, legend)
    final.save(BASE + filename)




def build_quick_sort_lomuto_full_plot():
    """快速排序（Lomuto 单边循环）完整递归流程：把数组完全排完。"""
    a = [4, 2, 7, 1, 3, 6, 5]
    recs = _trace_quick_sort(a, _lomuto_partition, 'first')
    rows = [_full_sort_row(v, cap, active=act, pivot=pv, locked=lk)
            for (v, _d, act, pv, cap, lk) in recs]
    content = _stack(rows)
    final = _add_text_bar(
        content,
        '快速排序 · 单边循环法（Lomuto）完整流程',
        '绿 = 已归位锁定（最终位置确定，不再参与）    金 = 本轮基准    '
        '蓝 = 当前正在分区的子区间    白 = 其他分支待处理    '
        '每行展示「选基准 → 基准归位锁定 → 递归左右子区间」，缩进表示递归深度；'
        '子区间长度 ≤1 时直接锁定；全部变绿即排序完成',
    )
    final.save(BASE + 'quick_sort_lomuto_full.png')


def build_quick_sort_hoare_expand_plot():
    """快速排序（Hoare 双边循环）：从左到右横向展开整个递归分区树，每轮展示判断与交换细节。"""
    a = [4, 7, 3, 5, 6, 2, 8, 1]
    nodes, edges = _trace_qs_tree(a, _hoare_partition_traced, 'first')
    _render_expand_tree(
        nodes, edges,
        '快速排序 · 双边循环法（Hoare）从左到右逐步展开（含判断与交换细节）',
        '每列 = 一轮（递归深度），从左到右：第一轮 → 衍生第二轮 → 第三轮 …    '
        '绿 = 已归位锁定    金 = 本轮基准    橙 = 正在交换    蓝 = 当前活动子区间    白 = 待处理    '
        '橙标签 left（后移，右移找 > 基准）    紫标签 right（先移，左移找 < 基准），标签只标下标    '
        '每格下方是该步指针位置，文字说明这一步如何判断、是否交换；左右指针相遇处即基准位置',
        'quick_sort_hoare_expand.png',
    )


def build_quick_sort_lomuto_expand_plot():
    """快速排序（Lomuto 单边循环，首元素基准）：从左到右横向展开整个递归分区树。"""
    a = [4, 7, 3, 5, 6, 2, 8, 1]
    nodes, edges = _trace_qs_tree(a, _lomuto_partition_traced, 'first')
    _render_expand_tree(
        nodes, edges,
        '快速排序 · 单边循环法（Lomuto，首元素基准）从左到右逐步展开（含判断与交换细节）',
        '每列 = 一轮（递归深度），从左到右：第一轮 → 衍生第二轮 → 第三轮 …    '
        '绿 = 已归位锁定    金 = 本轮基准    橙 = 正在交换    蓝 = 当前活动子区间    白 = 待处理    '
        '青标签 mark（小于基准区的右边界，从起始位置起）    红标签 j（遍历指针，从基准后开始）    '
        '每格下方是该步指针位置，文字说明 j 检查到什么、是否与 mark 交换；子区间 ≤1 个元素时直接锁定',
        'quick_sort_lomuto_expand.png',
    )


def build_bucket_sort_plot():
    """桶排序原理：按公式确定桶区间 → 分桶 → 桶内排序 → 按桶顺序拼接，一副图展示完整过程。"""
    import math

    arr = [29, 25, 3, 49, 9, 37, 21, 43]
    k = 5
    mn, mx = min(arr), max(arr)
    span = mx - mn + 1
    w = math.ceil(span / k)          # 每桶宽度（向上取整）

    def bucket_of(v):
        return (v - mn) // w          # 桶号公式

    # 每个桶：桶号、区间、原始顺序下的元素
    buckets = []
    for i in range(k):
        lo, hi = mn + i * w, mn + (i + 1) * w
        items = [v for v in arr if bucket_of(v) == i]
        buckets.append((i, lo, hi, items))

    def _bucket_png(i, lo, hi, items, mode):
        """画一个桶（上宽下窄的梯形），内部竖排元素；mode=sorted 时元素变绿。"""
        chip = '#7ec8a0' if mode == 'sorted' else '#c9d8ff'
        tc = '#0b3d2e' if mode == 'sorted' else '#1d3557'
        rows = (f'<TR><TD><B><FONT POINT-SIZE="12">桶 b{i}</FONT></B></TD></TR>'
                f'<TR><TD><FONT POINT-SIZE="11" COLOR="#44507a">[{lo}, {hi})</FONT></TD></TR>')
        if items:
            for v in items:
                rows += (f'<TR><TD BGCOLOR="{chip}" CELLPADDING="4">'
                         f'<FONT COLOR="{tc}" POINT-SIZE="14"><B>{v}</B></FONT></TD></TR>')
        else:
            rows += ('<TR><TD CELLPADDING="4"><FONT COLOR="#aaaaaa" POINT-SIZE="12">空</FONT>'
                     '</TD></TR>')
        label = (f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="3" CELLPADDING="2">'
                 f'{rows}</TABLE>>')
        dot = Digraph(format='png')
        dot.attr(pad='0.06')
        dot.attr('node', shape='invtrapezium', style='filled', fillcolor='#eef2fb',
                 color='#5a6b99', penwidth='1.5', fontname=FONT)
        dot.node('b', label)
        return Image.open(io.BytesIO(dot.pipe(format='png', quiet=True))).convert('RGBA')

    def _pack_h(images, gap=18, margin=18):
        """把多个桶横向排开，顶部对齐。"""
        height = max(im.height for im in images)
        width = sum(im.width for im in images) + gap * (len(images) - 1) + margin * 2
        canvas = Image.new('RGBA', (width, height + margin * 2), 'white')
        x = margin
        for im in images:
            canvas.alpha_composite(im, (x, margin))
            x += im.width + gap
        return canvas

    # ① 原始数组
    sec1 = _row_png(arr, '① 原始数组（无序）')

    # ② 桶区间公式
    formula = _stack([
        _text_png('② 如何确定桶的区间', 13, '#1d3557'),
        _text_png(f'桶数量 k = {k}', 12, '#333'),
        _text_png(f'数据跨度 = max - min + 1 = {mx} - {mn} + 1 = {span}', 12, '#333'),
        _text_png(f'每桶宽度 w = ceil(跨度 / k) = ceil({span} / {k}) = {w}', 12, '#333'),
        _text_png('元素 v 的桶号 i = floor((v - min) / w)', 12, '#333'),
        _text_png('第 i 个桶负责区间 [min + i*w, min + (i+1)*w)', 12, '#333'),
    ], gap=4, margin=8)

    # ③ 分配入桶
    sec3 = _stack([
        _text_png(f'③ 按公式把元素放进对应桶（k = {k}，桶宽 w = {w}）', 13, '#1d3557'),
        _pack_h([_bucket_png(i, lo, hi, items, 'raw') for i, lo, hi, items in buckets]),
    ])

    # ④ 桶内排序
    sec4 = _stack([
        _text_png('④ 每个桶内部各自排序（桶内用插入排序等）', 13, '#1d3557'),
        _pack_h([_bucket_png(i, lo, hi, sorted(items), 'sorted') for i, lo, hi, items in buckets]),
    ])

    # ⑤ 拼接
    out = [v for _, _, _, items in buckets for v in sorted(items)]
    sec5 = _row_png(out, '⑤ 按桶的顺序依次取出拼接 → 排序完成', greens=tuple(range(len(out))))

    body = _stack([sec1, formula, sec3, sec4, sec5], gap=20, margin=24)
    final = _add_text_bar(
        body,
        '桶排序原理 Bucket Sort',
        '蓝色 = 待排序    绿色 = 已排序    梯形 = 桶（上宽下窄）    桶号与区间由公式算出    '
        '思路：算区间 → 分桶 → 桶内排序 → 按桶拼接；平均 O(n+k)，最坏 O(n²)（元素全挤进同一桶时退化）',
    )
    final.save(BASE + 'bucket_sort.png')


def build_counting_sort_plot():
    """计数排序（稳定版）：统计频次 → 前缀和 → 从后往前回填。

    用 [90, 99, 95, 94, 95] 演示：两个 95 打上 95₁ / 95₂ 身份，
    验证排序后相对顺序不变（即稳定性）。
    """
    arr = [90, 99, 95, 94, 95]
    mn, mx = min(arr), max(arr)
    vals = list(range(mn, mx + 1))
    n = len(arr)

    # 给两个 95 打身份：95₁ / 95₂
    sub = {1: '₁', 2: '₂'}
    seen, tokens = 0, []
    for v in arr:
        if v == 95:
            seen += 1
            tokens.append(f'95{sub[seen]}')
        else:
            tokens.append(str(v))

    def _cell_colors(tok):
        """两个 95 用金色突出，其余用蓝色。"""
        if tok.startswith('95'):
            return '#f4c542', '#5a3e00'
        return '#dfe7ff', '#1d3557'

    def _cells_png(cells, caption=''):
        """cells: [(文字, 底色, 字色)]，横排一行格子。"""
        dot = Digraph(format='png')
        dot.attr(rankdir='TB', nodesep='0.12', ranksep='0.05', pad='0.05')
        dot.attr('node', fontname=FONT, penwidth='0')
        with dot.subgraph() as c:
            c.attr(rank='same')
            for j, (txt, bg, fc) in enumerate(cells):
                c.node(str(j), txt, shape='box', style='filled,rounded',
                       fillcolor=bg, fontcolor=fc, fontsize='15',
                       width='0.8', height='0.72', fixedsize='true')
            for j in range(len(cells) - 1):
                c.edge(str(j), str(j + 1), style='invis')
        if caption:
            dot.attr(label=caption, labelloc='b', fontname=FONT,
                     fontsize='11', fontcolor='#555')
        return Image.open(io.BytesIO(dot.pipe(format='png', quiet=True))).convert('RGBA')

    def _tally_png(numbers, caption='', hit=()):
        """把计数 / 前缀和画成一行：上排是值，下排是数字。"""
        cells = []
        for v, num in zip(vals, numbers):
            if v in hit:
                bg, fc = '#f4c542', '#5a3e00'
            elif num > 0:
                bg, fc = '#dfe7ff', '#1d3557'
            else:
                bg, fc = '#f7f7f7', '#c0c0c0'
            cells.append(
                '<TD BORDER="0" CELLPADDING="1">'
                '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">'
                f'<TR><TD ALIGN="CENTER"><FONT POINT-SIZE="10" COLOR="#888888">{v}</FONT></TD></TR>'
                f'<TR><TD BGCOLOR="{bg}" WIDTH="28" HEIGHT="26" ALIGN="CENTER">'
                f'<FONT POINT-SIZE="14" COLOR="{fc}"><B>{num}</B></FONT></TD></TR>'
                '</TABLE></TD>')
        label = ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="3">'
                 f'<TR>{"".join(cells)}</TR></TABLE>>')
        dot = Digraph(format='png')
        dot.attr(pad='0.05')
        dot.attr('node', shape='plaintext', fontname=FONT, penwidth='0')
        dot.node('t', label)
        if caption:
            dot.attr(label=caption, labelloc='b', fontname=FONT,
                     fontsize='11', fontcolor='#555')
        return Image.open(io.BytesIO(dot.pipe(format='png', quiet=True))).convert('RGBA')

    # ① 原始数组
    sec1 = _cells_png([(t, *_cell_colors(t)) for t in tokens],
                      '① 原始数组（两个 95 打上身份：95₁ 在 95₂ 左边）')

    # ② 统计频次
    count = {v: arr.count(v) for v in vals}
    sec2 = _stack([
        _text_png('② 统计每个值出现次数 count[v]++（下标 = 值 - 90）', 13, '#1d3557'),
        _tally_png([count[v] for v in vals], '蓝色 = 出现过，灰色 0 = 没出现', hit=(95,)),
    ], gap=4, margin=8)

    # ③ 求前缀和
    prefix, run = {}, 0
    for v in vals:
        run += count[v]
        prefix[v] = run
    sec3 = _stack([
        _text_png('③ 求前缀和 prefix[v] = 之前所有计数之和 → 该值的右边界', 13, '#1d3557'),
        _tally_png([prefix[v] for v in vals], 'prefix[95] = 4 表示两个 95 应占据下标 2、3', hit=(95,)),
    ], gap=4, margin=8)

    # ④ 从后往前回填
    out = [''] * n
    pre = dict(prefix)
    items = []
    for i in range(n - 1, -1, -1):
        v = arr[i]
        before = pre[v]
        pos = before - 1
        pre[v] -= 1
        out[pos] = tokens[i]
        desc = f'i={i}  处理 {tokens[i]}：prefix[{v}]={before} → 放 output[{pos}]'
        snap = _cells_png([(t, '#7ec8a0', '#0b3d2e') if t else ('·', '#eef1f6', '#aab4c8')
                           for t in out])
        items.append((desc, snap))

    desc_imgs = [_text_png(t, 11, '#333333') for t, _ in items]
    dw = max(im.width for im in desc_imgs)
    rows = [_text_png('④ 从后往前回填：每放一个元素，prefix[v] 减 1（右侧为 output，· = 空位）',
                      13, '#1d3557')]
    for desc_img, (_, snap) in zip(desc_imgs, items):
        padded = Image.new('RGBA', (dw, desc_img.height), 'white')
        padded.alpha_composite(desc_img, (0, 0))
        rows.append(_hstack(padded, snap, gap=18, margin=12))
    sec4 = _stack(rows, gap=8, margin=8)

    # ⑤ 排序结果
    sec5 = _cells_png([(t, *_cell_colors(t)) for t in out],
                      '⑤ 排序完成：95₁ 仍在 95₂ 左边 → 相同元素相对顺序保持不变')

    body = _stack([sec1, sec2, sec3, sec4, sec5], gap=20, margin=24)
    final = _add_text_bar(
        body,
        '计数排序（稳定版）Counting Sort',
        '蓝色 = 待排序    金色 = 两个 95（用于验证稳定性）    绿色 = 已回填    空位 = 尚未填充    '
        '不比较元素大小，靠下标定位；从后往前回填 + 前缀和递减才能保证相同元素相对顺序不变；时间 O(n + k)',
    )

    assert [int(t[:2]) for t in out] == sorted(arr)
    assert out.index('95₁') < out.index('95₂'), '95 的相对顺序被破坏'
    print('计数排序结果：', out)
    final.save(BASE + 'counting_sort.png')


def build_counting_sort_compare_plot():
    """计数排序稳定版 vs 不稳定版对比（一张图）。

    频次 count 与累计 ≤ v 合并成一张表；随后分别按「倒序 / 正序」回填，
    用金色追踪两个 95，直观看出正序回填会把 95₁ 与 95₂ 的顺序颠倒。
    """
    arr = [90, 99, 95, 94, 95]
    mn, mx = min(arr), max(arr)
    vals = list(range(mn, mx + 1))
    n = len(arr)

    sub = {1: '₁', 2: '₂'}
    seen, tokens = 0, []
    for v in arr:
        if v == 95:
            seen += 1
            tokens.append(f'95{sub[seen]}')
        else:
            tokens.append(str(v))

    count = {v: arr.count(v) for v in vals}
    prefix, run = {}, 0
    for v in vals:
        run += count[v]
        prefix[v] = run

    def _cells_png(cells, caption=''):
        """cells: [(文字, 底色, 字色)]，横排一行格子，格子下方标注下标。"""
        tds = []
        for j, (txt, bg, fc) in enumerate(cells):
            block = ('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">'
                     f'<TR><TD BGCOLOR="{bg}" WIDTH="46" HEIGHT="30" FIXEDSIZE="TRUE" '
                     f'ALIGN="CENTER"><FONT FACE="{FONT}" POINT-SIZE="14" COLOR="{fc}">'
                     f'<B>{txt}</B></FONT></TD></TR>'
                     f'<TR><TD ALIGN="CENTER"><FONT FACE="{FONT}" POINT-SIZE="9" '
                     f'COLOR="#999999">{j}</FONT></TD></TR></TABLE>')
            tds.append(f'<TD BORDER="0" CELLPADDING="2">{block}</TD>')
        label = ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR>'
                 + ''.join(tds) + '</TR></TABLE>>')
        dot = Digraph(format='png')
        dot.attr(pad='0.04')
        dot.attr('node', shape='plaintext', fontname=FONT, penwidth='0')
        dot.node('t', label)
        if caption:
            dot.attr(label=caption, labelloc='b', fontname=FONT,
                     fontsize='11', fontcolor='#555')
        return Image.open(io.BytesIO(dot.pipe(format='png', quiet=True))).convert('RGBA')

    def _gold(tok):
        """两个 95 全程用金色，方便追踪位置。"""
        return tok.startswith('95')

    # ① 原始数组
    def _raw_cell(tok):
        return ('#f4c542', '#5a3e00') if _gold(tok) else ('#dfe7ff', '#1d3557')

    sec1 = _cells_png([(t, *_raw_cell(t)) for t in tokens],
                      '① 原始数组（95₁ 在 95₂ 左边；两个 95 全程用金色追踪）')

    # ② 值 / count / 累计 ≤ v 合成一张表
    def _table_png():
        def td(txt, bg, fc, size=13, bold=True):
            inner = f'<B>{txt}</B>' if bold else str(txt)
            return (f'<TD BORDER="1" CELLPADDING="3" ALIGN="CENTER" BGCOLOR="{bg}" '
                    f'WIDTH="34" HEIGHT="26" FIXEDSIZE="TRUE" COLOR="#d0d0d0">'
                    f'<FONT POINT-SIZE="{size}" COLOR="{fc}">{inner}</FONT></TD>')

        head = ''.join(td(v, '#ffffff', '#888888', 11, False) for v in vals)
        row1 = ''.join(
            td(count[v],
               '#f4c542' if v == 95 else ('#dfe7ff' if count[v] else '#f7f7f7'),
               '#5a3e00' if v == 95 else ('#1d3557' if count[v] else '#c0c0c0'))
            for v in vals)
        row2 = ''.join(
            td(prefix[v], '#f4c542' if v == 95 else '#dfe7ff',
               '#5a3e00' if v == 95 else '#1d3557')
            for v in vals)

        def lab(title, desc):
            return (f'<TD BORDER="0" ALIGN="RIGHT" WIDTH="112" HEIGHT="34" FIXEDSIZE="TRUE">'
                    '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">'
                    f'<TR><TD ALIGN="RIGHT"><FONT POINT-SIZE="11" COLOR="#222222">'
                    f'<B>{title}</B></FONT></TD></TR>'
                    f'<TR><TD ALIGN="RIGHT"><FONT POINT-SIZE="8" COLOR="#999999">'
                    f'{desc}</FONT></TD></TR>'
                    '</TABLE></TD>')

        label = ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">'
                 f'<TR>{lab("值 v", "下标 = 值 − 90")}{head}</TR>'
                 f'<TR>{lab("count", "出现次数")}{row1}</TR>'
                 f'<TR>{lab("累计 ≤ v", "前缀和 → 右边界")}{row2}</TR>'
                 '</TABLE>>')
        dot = Digraph(format='png')
        dot.attr(pad='0.05')
        dot.attr('node', shape='plaintext', fontname=FONT, penwidth='0')
        dot.node('t', label)
        return Image.open(io.BytesIO(dot.pipe(format='png', quiet=True))).convert('RGBA')

    sec2 = _stack([
        _text_png('② 频次与前缀和（一张表）：count 统计个数，累计 ≤ v 得出右边界', 13, '#1d3557'),
        _table_png(),
        _text_png('累计 ≤ v = prefix[v]：值 v 的最后一个位置 = prefix[v] - 1', 11, '#555555'),
    ], gap=6, margin=8)

    # 回填追踪
    def trace(order):
        pre = dict(prefix)
        out = [''] * n
        recs = []
        for i in order:
            v = arr[i]
            before = pre[v]
            pos = before - 1
            pre[v] -= 1
            out[pos] = tokens[i]
            recs.append((i, tokens[i], v, before, pos, list(out)))
        return recs, out

    stable_recs, stable_out = trace(range(n - 1, -1, -1))
    unstable_recs, unstable_out = trace(range(n))

    def _desc(rec):
        return f'i={rec[0]}  {rec[1]}  prefix[{rec[2]}]={rec[3]} → out[{rec[4]}]'

    desc_w = max(_text_png(_desc(r), 10, '#333333').width
                 for r in stable_recs + unstable_recs)

    def _block(recs, title, title_color):
        rows = [_text_png(title, 12, title_color)]
        for rec in recs:
            desc_img = _text_png(_desc(rec), 10, '#333333')
            padded = Image.new('RGBA', (desc_w, desc_img.height), 'white')
            padded.alpha_composite(desc_img, (0, 0))
            cells = []
            for t in rec[5]:
                if not t:
                    cells.append(('·', '#eef1f6', '#aab4c8'))
                elif _gold(t):
                    cells.append((t, '#f4c542', '#5a3e00'))
                else:
                    cells.append((t, '#7ec8a0', '#0b3d2e'))
            rows.append(_hstack(padded, _cells_png(cells), gap=14, margin=8))
        return _stack(rows, gap=6, margin=6)

    sec3 = _block(stable_recs, '③ 稳定版：从后往前遍历', '#2a9d8f')
    sec4 = _block(unstable_recs, '④ 不稳定版：从前往后遍历', '#c0504d')
    sec34 = _hstack(sec3, sec4, gap=44, margin=16)

    # ⑤ 结果对比（左右并排）
    def _result(toks, title, color):
        cells = [(t, '#f4c542', '#5a3e00') if _gold(t) else (t, '#7ec8a0', '#0b3d2e')
                 for t in toks]
        return _stack([_text_png(title, 11, color), _cells_png(cells)], gap=4, margin=6)

    sec5 = _stack([
        _text_png('⑤ 结果对比：两版数值都正确，差别只在两个 95 的先后', 13, '#1d3557'),
        _hstack(_result(stable_out, '稳定版：95₁ 仍在 95₂ 左边', '#2a9d8f'),
                _result(unstable_out, '不稳定版：95₂ 跑到 95₁ 左边', '#c0504d'),
                gap=60, margin=16),
    ], gap=8, margin=8)

    body = _stack([sec1, sec2, sec34, sec5], gap=18, margin=24)
    final = _add_text_bar(
        body,
        '计数排序 Counting Sort —— 稳定版 vs 不稳定版',
        '蓝色 = 待排序    金色 = 两个 95（全程追踪位置）    绿色 = 已回填    空位 = 尚未填充    '
        '格下数字 = 下标    两版只差遍历方向：倒序（或正序 + 左边界）才稳定，正序 + 右边界会把相同元素顺序颠倒',
    )

    assert stable_out == ['90', '94', '95₁', '95₂', '99']
    assert unstable_out == ['90', '94', '95₂', '95₁', '99']
    print('稳定版：', stable_out)
    print('不稳定版：', unstable_out)
    final.save(BASE + 'counting_sort_compare.png')


if __name__ == '__main__':
    # build_bubble_sort_plot()
    # build_bubble_sort_optimized_plot()
    # build_cocktail_sort_plot()

    build_quick_sort_hoare_expand_plot()
    build_quick_sort_lomuto_expand_plot()
    build_bucket_sort_plot()
    build_counting_sort_plot()
    build_counting_sort_compare_plot()
