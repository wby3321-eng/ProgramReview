import numpy as np
import matplotlib.pyplot as plt


def build_time_complexity_plot():
    """绘制常见时间复杂度对比图。"""
    plt.rcParams['font.sans-serif'] = ['STHeiti']
    plt.rcParams['axes.unicode_minus'] = False

    n = np.arange(1, 11, 1)  # 输入规模：1 到 10，步长 1

    o1 = np.ones_like(n, dtype=float)
    ologn = np.log(n)
    on = n
    onlogn = n * np.log(n)
    on2 = n ** 2

    plt.figure(figsize=(10, 6))
    plt.plot(n, o1, label=r'$O(1)$ 常量', lw=2)
    plt.plot(n, ologn, label=r'$O(\log n)$ 对数', lw=2)
    plt.plot(n, on, label=r'$O(n)$ 线性', lw=2)
    plt.plot(n, onlogn, label=r'$O(n\log n)$ 线性对数', lw=2)
    plt.plot(n, on2, label=r'$O(n^2)$ 平方', lw=2)

    plt.xlabel('输入规模 n')
    plt.ylabel('运算代价')
    plt.title('常见时间复杂度对比')
    plt.legend()
    plt.xlim(1, 10)
    plt.ylim(1, 10)
    plt.xticks(range(0, 11))
    plt.yticks(range(0, 11))
    plt.grid(True, alpha=0.3)
    plt.show()


def build_tree_plot():
    """绘制树结构概念图。

    图形约定：
    - 深色实线：树的边（节点与节点之间的父子关系）
    - 灰色虚线 + 空心箭头：概念标注
    """
    from graphviz import Digraph

    font = 'PingFang SC'

    dot = Digraph(name='树结构概念图', format='png')
    dot.attr(rankdir='TB', nodesep='0.55', ranksep='0.75', pad='0.3')
    dot.attr('node', shape='circle', style='filled', fontname=font, fontsize='15', penwidth='0')
    # 树的边：深色实线，和标注线区分开
    dot.attr('edge', color='#2f2f2f', penwidth='2')

    # ---------- 树节点：橙色根、紫色内部节点、绿色叶子 ----------
    dot.node('1', '1', fillcolor='#ff9944')
    dot.node('2', '2', fillcolor='#a06cd5')
    dot.node('3', '3', fillcolor='#a06cd5')
    dot.node('4', '4', fillcolor='#a06cd5')
    dot.node('5', '5', fillcolor='#57b894')
    dot.node('6', '6', fillcolor='#57b894')
    dot.node('7', '7', fillcolor='#57b894')
    dot.node('8', '8', fillcolor='#57b894')
    dot.node('9', '9', fillcolor='#57b894')

    # ---------- 树的边（深色实线） ----------
    dot.edges([
        ('1', '2'), ('1', '3'),
        ('2', '4'), ('2', '5'),
        ('3', '6'),
        ('4', '7'), ('4', '8'), ('4', '9'),
    ])

    # ---------- 概念标注：灰色虚线框标签 + 虚线空心箭头 ----------
    label_attr = dict(shape='box', style='rounded,dashed', color='#bbbbbb',
                      fillcolor='#fafafa', fontname=font, fontsize='11', fontcolor='#555555')

    def annotate(node_id, text, target):
        dot.node(node_id, text, **label_attr)
        dot.edge(node_id, target, style='dashed', color='#9e9e9e',
                 penwidth='1.2', arrowhead='open', constraint='false')

    annotate('lab_root', '根节点 root\n没有父节点的节点', '1')
    annotate('lab_parent', '父节点 / 子节点\n2 是 4 的父节点\n4 是 2 的子节点', '2')
    annotate('lab_sibling', '兄弟节点\n2 与 3 有同一个父节点', '3')
    annotate('lab_degree', '节点的度 = 3\n4 有 3 个子节点', '4')
    annotate('lab_subtree', '子树 subtree\n以 4 为根：4、7、8、9', '4')
    annotate('lab_leaf', '叶子节点 leaf\n7、8、9 没有子节点', '8')
    annotate('lab_height', '树的高度 = 4\n最长路径：1 → 2 → 4 → 7', '9')

    # 让标注与目标节点处在同一层，左右分列，避免堆叠
    def same_rank(*ids):
        with dot.subgraph() as s:
            s.attr(rank='same')
            for i in ids:
                s.node(i)

    same_rank('lab_root', '1')
    same_rank('lab_parent', '2', '3', 'lab_sibling')
    same_rank('lab_degree', '4', '5', '6', 'lab_subtree')
    same_rank('lab_leaf', '7', '8', '9', 'lab_height')

    # 图例：说明实线与虚线的区别
    dot.attr(label='实线 —— 树的边       虚线空心箭头 —— 概念标注       橙色 = 根节点  紫色 = 内部节点  绿色 = 叶子节点',
             labelloc='b', labeljust='l', fontname=font, fontsize='11', fontcolor='#666666')

    dot.render('/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/tree_concept', view=True)


def build_binary_tree_plot():
    """绘制二叉查找树（BST）结构图并标注关键特性。

    图形约定：
    - 深色实线：树的边（父子关系）
    - 灰色虚线 + 空心箭头：特性标注
    """
    from graphviz import Digraph

    font = 'PingFang SC'

    dot = Digraph(name='二叉查找树', format='png')
    dot.attr(rankdir='TB', nodesep='0.6', ranksep='0.9', pad='0.3')
    dot.attr('node', shape='circle', style='filled', fontname=font, fontsize='14',
             penwidth='0', width='0.62', height='0.62', fixedsize='true')
    # 树的边：深色实线
    dot.attr('edge', color='#2f2f2f', penwidth='2')

    # ---------- 节点：橙色根、紫色内部节点、绿色叶子 ----------
    dot.node('50', '50', fillcolor='#ff9944')
    dot.node('30', '30', fillcolor='#a06cd5')
    dot.node('70', '70', fillcolor='#a06cd5')
    dot.node('20', '20', fillcolor='#57b894')
    dot.node('40', '40', fillcolor='#57b894')
    dot.node('60', '60', fillcolor='#57b894')
    dot.node('80', '80', fillcolor='#57b894')

    # ---------- 树的边（实线），根的两条边标出左孩子 / 右孩子 ----------
    dot.edge('50', '30', label='左孩子', fontcolor='#777777', fontsize='10', fontname=font)
    dot.edge('50', '70', label='右孩子', fontcolor='#777777', fontsize='10', fontname=font)
    dot.edges([('30', '20'), ('30', '40'), ('70', '60'), ('70', '80')])

    # ---------- 关键特性标注：灰色虚线框标签 + 虚线空心箭头 ----------
    label_attr = dict(shape='box', style='rounded,dashed', color='#bbbbbb',
                      fillcolor='#fafafa', fontname=font, fontsize='11', fontcolor='#555555',
                      fixedsize='false')

    def annotate(node_id, text, target):
        dot.node(node_id, text, **label_attr)
        dot.edge(node_id, target, style='dashed', color='#9e9e9e',
                 penwidth='1.2', arrowhead='open', constraint='false')

    annotate('lab_root', '根节点 50\n左子树全部 < 50 < 右子树全部', '50')
    annotate('lab_height', '树的高 = 3\n每层排除一半，平均 O(log n)\n退化成链表时 O(n)', '70')
    annotate('lab_inorder', '中序遍历 = 升序\n20 → 30 → 40 → 50 → 60 → 70 → 80', '80')

    # 标注与目标节点同层，避免堆叠
    def same_rank(*ids):
        with dot.subgraph() as s:
            s.attr(rank='same')
            for i in ids:
                s.node(i)

    same_rank('lab_root', '50')
    same_rank('lab_height', '30', '70')
    same_rank('20', '40', '60', '80', 'lab_inorder')

    # 图例：说明实线与虚线的区别
    dot.attr(label='实线 —— 树的边       虚线空心箭头 —— 特性标注       橙色 = 根节点  紫色 = 内部节点  绿色 = 叶子节点',
             labelloc='b', labeljust='l', fontname=font, fontsize='11', fontcolor='#666666')

    dot.render('/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/binary_search_tree',
               view=True, cleanup=True)


BST_CHILDREN = {
    '50': ('30', '70'),
    '30': ('20', '40'),
    '70': ('60', '80'),
    '20': (None, None),
    '40': (None, None),
    '60': (None, None),
    '80': (None, None),
}


def get_traversals():
    """返回二叉查找树的四种遍历序列。"""
    pre, ino, post = [], [], []

    def dfs(v):
        if v is None:
            return
        left, right = BST_CHILDREN[v]
        pre.append(v)          # 根
        dfs(left)              # 左子树
        ino.append(v)          # 根（左子树访问完之后）
        dfs(right)             # 右子树
        post.append(v)         # 根（右子树访问完之后）

    dfs('50')

    level, queue = [], ['50']
    while queue:
        v = queue.pop(0)
        level.append(v)
        queue.extend(c for c in BST_CHILDREN[v] if c)

    return {'前序': pre, '中序': ino, '后序': post, '层序': level}


def build_binary_tree_traversal_plot():
    """绘制二叉查找树的四种遍历顺序。

    每个节点内标注访问序号，底部给出遍历规则与完整序列。
    """
    from graphviz import Digraph

    font = 'PingFang SC'
    rules = {
        '前序': ('preorder', '根 → 左子树 → 右子树'),
        '中序': ('inorder', '左子树 → 根 → 右子树'),
        '后序': ('postorder', '左子树 → 右子树 → 根'),
        '层序': ('levelorder', '按层从左到右（队列 BFS）'),
    }
    colors = {
        '50': '#ff9944', '30': '#a06cd5', '70': '#a06cd5',
        '20': '#57b894', '40': '#57b894', '60': '#57b894', '80': '#57b894',
    }

    for name, seq in get_traversals().items():
        filename, rule = rules[name]
        order = {v: i + 1 for i, v in enumerate(seq)}

        dot = Digraph(name=f'{name}遍历', format='png')
        dot.attr(rankdir='TB', nodesep='0.6', ranksep='0.6', pad='0.25')
        dot.attr('node', shape='circle', style='filled', fontname=font, fontsize='13',
                 penwidth='0', width='0.85', height='0.85', fixedsize='true')
        dot.attr('edge', color='#2f2f2f', penwidth='2')

        # 节点：上排是值，下排是访问序号
        for v, color in colors.items():
            label = f'<{v}<br/><font color="#ffffff" point-size="11">第{order[v]}个</font>>'
            dot.node(v, label, fillcolor=color)

        dot.edges([('50', '30'), ('50', '70'), ('30', '20'),
                   ('30', '40'), ('70', '60'), ('70', '80')])

        dot.attr(label=f'{name}遍历：{rule}\\n访问顺序：' + ' → '.join(seq),
                 labelloc='b', labeljust='l', fontname=font, fontsize='12', fontcolor='#444444')

        dot.render('/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/'
                   f'traversal_{filename}', view=False, cleanup=True)


def build_binary_heap_plot():
    """绘制二叉堆（最大堆）结构图并标注基本概念。

    图形约定：
    - 深色实线：树的边（父子关系）
    - 灰色虚线 + 空心箭头：概念标注
    - 节点内下排 i=N：该节点在数组中的下标
    """
    from graphviz import Digraph

    font = 'PingFang SC'

    # 数组表示（下标从 0 开始），这棵树满足最大堆性质
    heap = [90, 70, 80, 50, 60, 30, 40]

    dot = Digraph(name='二叉堆', format='png')
    dot.attr(rankdir='TB', nodesep='0.55', ranksep='0.85', pad='0.3')
    dot.attr('node', shape='circle', style='filled', fontname=font, fontsize='13',
             penwidth='0', width='0.8', height='0.8', fixedsize='true')
    dot.attr('edge', color='#2f2f2f', penwidth='2')

    # ---------- 节点：橙色堆顶、紫色内部节点、绿色叶子 ----------
    for i, v in enumerate(heap):
        if i == 0:
            color = '#ff9944'
        elif i < 3:
            color = '#a06cd5'
        else:
            color = '#57b894'
        label = f'<{v}<br/><font color="#ffffff" point-size="10">i={i}</font>>'
        dot.node(str(i), label, fillcolor=color)

    # ---------- 树的边（实线），堆顶两条边标出下标公式 ----------
    dot.edge('0', '1', label='2i+1', fontcolor='#777777', fontsize='9', fontname=font)
    dot.edge('0', '2', label='2i+2', fontcolor='#777777', fontsize='9', fontname=font)
    dot.edges([('1', '3'), ('1', '4'), ('2', '5'), ('2', '6')])

    # ---------- 基本概念标注：灰色虚线框标签 + 虚线空心箭头 ----------
    label_attr = dict(shape='box', style='rounded,dashed', color='#bbbbbb',
                      fillcolor='#fafafa', fontname=font, fontsize='11', fontcolor='#555555',
                      fixedsize='false')

    def annotate(node_id, text, target):
        dot.node(node_id, text, **label_attr)
        dot.edge(node_id, target, style='dashed', color='#9e9e9e',
                 penwidth='1.2', arrowhead='open', constraint='false')

    annotate('lab_top', '堆顶 = 最大值\n最大堆：根节点 ≥ 所有节点', '0')
    annotate('lab_order', '堆序性质：父 ≥ 子\n70 ≥ 50、60，80 ≥ 30、40', '1')
    annotate('lab_complete', '完全二叉树\n最后一层从左向右连续填满', '6')

    # 标注与目标节点同层，避免堆叠
    def same_rank(*ids):
        with dot.subgraph() as s:
            s.attr(rank='same')
            for i in ids:
                s.node(i)

    same_rank('lab_top', '0')
    same_rank('lab_order', '1', '2')
    same_rank('3', '4', '5', '6', 'lab_complete')

    # 图例 + 数组存储与操作说明
    dot.attr(label='实线 —— 树的边       虚线空心箭头 —— 概念标注\\n'
                   '数组存储：[' + ', '.join(str(v) for v in heap) + ']\\n'
                   '下标关系：左孩子 2i+1　右孩子 2i+2　父节点 (i-1)//2（向下取整）\\n'
                   '操作：插入末尾上浮、删除堆顶后末尾补位下沉，均为 O(log n)',
             labelloc='b', labeljust='l', fontname=font, fontsize='11', fontcolor='#666666')

    dot.render('/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/binary_heap',
               view=True, cleanup=True)


def build_heap_sift_steps_plot():
    """把堆的上浮、下沉过程分别画成一张分步图。

    橙色粗框：当前移动的元素；灰色粗框：参与比较的节点。
    """
    import io

    from graphviz import Digraph
    from PIL import Image

    font = 'PingFang SC'
    base = '/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/'

    def stage_png(values, caption, moving, compared):
        dot = Digraph(format='png')
        dot.attr(rankdir='TB', nodesep='0.35', ranksep='0.5', pad='0.15')
        dot.attr('node', shape='circle', style='filled', fontname=font, fontsize='11',
                 penwidth='0', width='0.68', height='0.68', fixedsize='true')
        dot.attr('edge', color='#2f2f2f', penwidth='1.6')

        for i, v in enumerate(values):
            depth = (i + 1).bit_length() - 1
            color = '#ff9944' if depth == 0 else ('#a06cd5' if depth == 1 else '#57b894')
            attrs = dict(fillcolor=color)
            if i in moving:
                attrs.update(color='#e05a3a', penwidth='3')
            elif i in compared:
                attrs.update(color='#8a8a8a', penwidth='2.5')
            label = f'<{v}<br/><font color="#ffffff" point-size="8">i={i}</font>>'
            dot.node(str(i), label, **attrs)

        for i in range(1, len(values)):
            dot.edge(str((i - 1) // 2), str(i))

        dot.attr(label=caption, labelloc='b', labeljust='c',
                 fontname=font, fontsize='10', fontcolor='#555555')
        return Image.open(io.BytesIO(dot.pipe(format='png'))).convert('RGBA')

    def compose(images, out_name):
        gap, margin = 16, 20
        height = max(im.height for im in images)
        width = sum(im.width for im in images) + gap * (len(images) - 1) + margin * 2
        canvas = Image.new('RGBA', (width, height + margin * 2), 'white')
        x = margin
        for im in images:
            canvas.alpha_composite(im, (x, margin))
            x += im.width + gap
        canvas.convert('RGB').save(base + out_name)

    # 上浮全过程：最大堆插入 85
    compose([
        stage_png([90, 70, 80, 50, 60, 30, 40, 85],
                  '① 插入 85 到末尾 i=7，与父节点 50 比较\n'
                  '（橙框 = 当前元素，灰框 = 比较对象）', {7}, {3}),
        stage_png([90, 70, 80, 85, 60, 30, 40, 50],
                  '② 85 > 50，交换到 i=3，\n再与父节点 70 比较', {3}, {1}),
        stage_png([90, 85, 80, 70, 60, 30, 40, 50],
                  '③ 85 > 70，交换到 i=1；\n85 < 90，上浮停止', {1}, {0}),
    ], 'heap_sift_up_steps.png')

    # 下沉全过程：最大堆删除堆顶 90（先给出原始堆）
    compose([
        stage_png([90, 70, 80, 50, 60, 30, 40],
                  '① 原始堆：[90, 70, 80, 50, 60, 30, 40]，\n准备删除堆顶最大值 90', {0}, set()),
        stage_png([40, 70, 80, 50, 60, 30],
                  '② 删除堆顶 90，末尾 40 补到 i=0，\n与孩子 70、80 中较大的 80 比较', {0}, {1, 2}),
        stage_png([80, 70, 40, 50, 60, 30],
                  '③ 40 < 80，交换到 i=2；\n孩子 30 < 40，下沉停止', {2}, {5}),
    ], 'heap_sift_down_steps.png')


def build_traversal_grid():
    """把四种遍历图拼成一张 2×2 的总图。"""
    from PIL import Image

    base = '/Users/wangboyun/workspace/ProgramReview/计算机科学/知识库/resource/'
    names = ['preorder', 'inorder', 'postorder', 'levelorder']

    images = [Image.open(f'{base}traversal_{n}.png').convert('RGBA') for n in names]
    w = max(im.width for im in images)
    h = max(im.height for im in images)

    gap, margin = 24, 24
    canvas = Image.new('RGBA', (w * 2 + gap + margin * 2, h * 2 + gap + margin * 2), 'white')

    for i, im in enumerate(images):
        row, col = divmod(i, 2)
        x = margin + col * (w + gap) + (w - im.width) // 2
        y = margin + row * (h + gap) + (h - im.height) // 2
        canvas.alpha_composite(im, (x, y))

    canvas.convert('RGB').save(f'{base}traversal_all.png')


build_tree_plot()
build_binary_tree_plot()
build_binary_tree_traversal_plot()
build_binary_heap_plot()
build_heap_sift_steps_plot()
build_traversal_grid()
