#!/usr/bin/env python3
"""
扫描各分组下的知识库目录，生成 data.json 与各分组 .xmind。

- 只收录 {分组}/{SCOPE_SUBDIR} 下的内容
- 目录无限递归，不预设层级
- .md 文件读取正文，供前端全文搜索
- 复习进度：最底层知识点目录（不含子目录，排除 RESOURCE_DIR）下存在 .md 即算已复习
- 生成 {分组}-{XMIND_SUFFIX}.xmind（可用 XMind 软件打开），已复习/未复习用任务标记区分

data.json 与 xmind/ 均为部署时生成的产物，不提交回仓库（见 .gitignore）。
"""

import io
import json
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ===== 可调配置 =====
# 分组下要扫描的子目录；设为 "" 表示直接扫描分组目录本身（适合接入已有树）
SCOPE_SUBDIR = "知识库"
XMIND_SUFFIX = "知识图谱"
RESOURCE_DIR = "resource"
SKIP_DIRS = {
    ".git", ".github", "scripts", "assets", "xmind",
    "node_modules", "dist", "build", "venv", "__pycache__",
}
# 扫描时整体跳过的目录名，例如 {"真题", "答案", "归档"}
EXCLUDE_DIRS = set()
# 排序表：键为父目录名，"__root__" 表示各分组下第一层。未列出的按名称排在后面
ORDER_MAP = {
    "__root__": [
        "数据结构与算法", "计算机组成原理", "操作系统", "计算机网络",
        "数据库系统", "编程语言与编译原理", "软件工程与系统设计",
        "分布式与云计算", "信息安全",
        "数学基础", "机器学习", "深度学习", "自然语言处理", "计算机视觉",
        "强化学习", "大语言模型", "AI 系统与工程", "AI 安全与伦理",
    ],
    "数据结构与算法": [
        "复杂度分析", "线性表", "栈与队列", "树与二叉树", "堆与优先队列",
        "哈希表", "图", "排序与查找", "分治与回溯", "动态规划", "贪心算法", "字符串算法",
    ],
    "计算机组成原理": [
        "数据的机器表示", "指令系统", "CPU 与流水线", "存储层次结构",
        "总线与输入输出", "并行与多核", "性能分析与优化",
    ],
    "操作系统": [
        "进程与线程", "CPU 调度", "同步与互斥", "死锁", "内存管理",
        "虚拟内存", "文件系统", "输入输出与设备管理",
    ],
    "计算机网络": [
        "网络体系结构", "数据链路层", "IP 与路由", "TCP 与 UDP",
        "DNS 与 HTTP", "无线网络", "网络性能与排障", "网络安全",
    ],
    "数据库系统": [
        "关系模型与 SQL", "数据库设计", "存储引擎", "索引与查询优化",
        "事务与并发控制", "NoSQL 与 NewSQL", "备份恢复与高可用",
    ],
    "编程语言与编译原理": [
        "类型系统", "内存模型", "函数式与面向对象", "并发编程",
        "词法与语法分析", "中间代码与优化", "运行时与垃圾回收",
    ],
    "软件工程与系统设计": [
        "需求与架构", "设计模式", "API 设计", "测试与质量保障",
        "持续集成与持续交付", "可观测性", "系统设计", "性能优化",
    ],
    "分布式与云计算": [
        "分布式一致性", "分布式事务", "消息队列", "缓存系统", "负载均衡",
        "微服务与服务网格", "容器与 Kubernetes", "云原生架构",
    ],
    "信息安全": [
        "密码学基础", "身份认证与访问控制", "安全协议", "Web 安全",
        "系统与网络安全", "隐私保护", "安全运营",
    ],
    "数学基础": ["线性代数", "概率论与数理统计", "微积分与最优化", "信息论", "数值计算", "随机过程"],
    "机器学习": [
        "监督学习", "无监督学习", "特征工程", "模型评估与选择",
        "集成学习", "概率图模型", "因果推断", "可解释机器学习",
    ],
    "深度学习": [
        "神经网络基础", "反向传播与优化", "正则化与泛化", "卷积神经网络",
        "循环神经网络", "Transformer", "生成模型", "自监督与对比学习", "图神经网络",
    ],
    "自然语言处理": ["文本表示", "语言模型", "序列标注", "机器翻译", "问答与信息检索", "文本生成", "情感与语义分析"],
    "计算机视觉": ["图像分类", "目标检测", "图像分割", "视觉 Transformer", "视频理解", "多模态视觉", "三维视觉"],
    "强化学习": [
        "马尔可夫决策过程", "动态规划与蒙特卡洛", "时序差分学习", "策略梯度",
        "深度强化学习", "离线强化学习", "多智能体强化学习",
    ],
    "大语言模型": [
        "预训练与缩放定律", "指令微调", "对齐与 RLHF", "提示工程", "检索增强生成",
        "Agent 与工具调用", "上下文与记忆", "模型压缩与推理加速", "大模型评测",
    ],
    "AI 系统与工程": ["数据工程", "训练框架", "分布式训练", "GPU 与 CUDA", "推理服务", "MLOps", "向量数据库", "边缘 AI"],
    "AI 安全与伦理": ["鲁棒性与对抗攻击", "幻觉与事实性", "数据隐私", "公平性与偏见", "内容安全", "模型治理与合规", "AI 伦理"],
}

MD_EXTS = {".md", ".markdown"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def is_hidden(name: str) -> bool:
    return name.startswith(".")


def sort_key(parent_key: str):
    """返回排序函数：优先按排序表，未列出的按名称排在其后。"""
    order = ORDER_MAP.get(parent_key, [])

    def key(p: Path):
        name = p.stem if p.is_file() else p.name
        idx = order.index(name) if name in order else len(order)
        return (idx, name)

    return key


def scan_dir(dir_path: Path, base: Path, is_root: bool = False) -> list:
    """递归扫描目录，返回子节点列表（目录在前，文件在后）。"""
    nodes = []
    parent_key = "__root__" if is_root else dir_path.name
    key = sort_key(parent_key)

    subdirs = sorted(
        [
            d
            for d in dir_path.iterdir()
            if d.is_dir() and not is_hidden(d.name) and d.name not in EXCLUDE_DIRS
        ],
        key=key,
    )
    files = sorted(
        [f for f in dir_path.iterdir() if f.is_file() and not is_hidden(f.name)],
        key=key,
    )

    for sd in subdirs:
        children = scan_dir(sd, base)
        # 空目录（仅含隐藏文件）也保留为节点，用于进度统计与脑图展示
        nodes.append({"type": "dir", "name": sd.name, "children": children})

    for f in files:
        ext = f.suffix.lower()
        node = {
            "type": "file",
            "name": f.name,
            "ext": ext,
            "path": f.relative_to(base).as_posix(),
            "size": f.stat().st_size,
        }
        if ext in MD_EXTS:
            try:
                node["content"] = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                node["content"] = ""
        nodes.append(node)

    return nodes


# ===== 复习进度统计 =====
def is_knowledge_leaf(node: dict) -> bool:
    """知识点叶子：是目录、不含任何子目录、且不是资源目录。"""
    if node.get("type") != "dir":
        return False
    if node["name"] == RESOURCE_DIR:
        return False
    return not any(c.get("type") == "dir" for c in node.get("children", []))


def walk_leaves(node: dict, acc: list) -> None:
    if is_knowledge_leaf(node):
        acc.append(node)
        return
    for c in node.get("children", []):
        walk_leaves(c, acc)


def leaf_has_md(node: dict) -> bool:
    return any(
        c.get("type") == "file" and c.get("ext") in MD_EXTS
        for c in node.get("children", [])
    )


def progress_of(node: dict) -> dict:
    leaves = []
    walk_leaves(node, leaves)
    total = len(leaves)
    done = sum(1 for l in leaves if leaf_has_md(l))
    return {"total": total, "done": done}


def module_progress(root: dict) -> list:
    """返回一级模块的进度列表。"""
    out = []
    for m in root.get("children", []):
        if m.get("type") == "dir":
            p = progress_of(m)
            out.append({"name": m["name"], "total": p["total"], "done": p["done"]})
    return out


# ===== 生成 xmind =====
def to_topic(node: dict) -> dict:
    leaf = is_knowledge_leaf(node)
    done = leaf and leaf_has_md(node)
    topic = {"id": new_id(), "title": node["name"]}
    if leaf:
        topic["markers"] = [{"markerId": "task-done" if done else "task-todo"}]
    children = [c for c in node.get("children", []) if c.get("type") == "dir"]
    if children:
        topic["children"] = {"attached": [to_topic(c) for c in children]}
    return topic


def build_xmind(scope: str, root: dict) -> bytes:
    sheet = {
        "id": new_id(),
        "class": "sheet",
        "title": f"{scope}-{XMIND_SUFFIX}",
        "rootTopic": {
            "id": new_id(),
            "title": f"{scope} · {XMIND_SUFFIX}",
            "structureClass": "org.xmind.ui.logic.right",
            "children": {"attached": [to_topic(c) for c in root.get("children", [])]},
        },
    }
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="json" ContentType="application/json"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '</Types>'
    )
    manifest = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
        '<manifest:file-entry manifest:media-type="application/json" manifest:full-path="content.json"/>'
        '<manifest:file-entry manifest:media-type="application/json" manifest:full-path="metadata.json"/>'
        "</manifest:manifest>"
    )
    metadata = json.dumps(
        {"creator": {"name": "TreeKnowledgeSite"}, "version": "1.0.0"},
        ensure_ascii=False,
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("META-INF/manifest.xml", manifest)
        z.writestr("metadata.json", metadata)
        z.writestr("content.json", json.dumps([sheet], ensure_ascii=False))
    return buf.getvalue()


# ===== 主流程 =====
def build() -> dict:
    scopes = []
    for scope_dir in sorted(ROOT.iterdir()):
        if not scope_dir.is_dir() or is_hidden(scope_dir.name):
            continue
        if scope_dir.name in SKIP_DIRS:
            continue
        scan_root = scope_dir / SCOPE_SUBDIR if SCOPE_SUBDIR else scope_dir
        if not scan_root.is_dir():
            continue
        children = scan_dir(scan_root, ROOT, is_root=True)
        root_name = SCOPE_SUBDIR or scope_dir.name
        root = {"type": "dir", "name": root_name, "children": children}
        p = progress_of(root)
        scopes.append({
            "name": scope_dir.name,
            "root_name": root_name,
            "root": root,
            "progress": {**p, "modules": module_progress(root)},
        })
        xmind_dir = ROOT / "xmind"
        xmind_dir.mkdir(exist_ok=True)
        (xmind_dir / f"{scope_dir.name}-{XMIND_SUFFIX}.xmind").write_bytes(
            build_xmind(scope_dir.name, root)
        )

    if not scopes:
        print(f"⚠️ 未找到可扫描的分组。请创建 {{分组}}/{SCOPE_SUBDIR or ''} 目录。")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root_name": SCOPE_SUBDIR,
        "mindmap_suffix": XMIND_SUFFIX,
        "provinces": scopes,
    }


def main():
    data = build()
    out = ROOT / "data.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(s["progress"]["total"] for s in data["provinces"])
    done = sum(s["progress"]["done"] for s in data["provinces"])
    print(f"✅ data.json  分组:{len(data['provinces'])}  知识点:{done}/{total}")
    for s in data["provinces"]:
        print(
            f"   {s['name']}: {s['progress']['done']}/{s['progress']['total']}"
            f"  → xmind/{s['name']}-{XMIND_SUFFIX}.xmind"
        )


if __name__ == "__main__":
    main()
