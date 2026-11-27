# 计算机与 AI 复习知识库

## 🔗 访问地址

**https://wby3321-eng.github.io/ProgramReview/**


## 🚀 工作流（全自动）

```
本地新增/修改文件
      ↓
git commit + git push
      ↓
GitHub Actions 自动触发
      ├─ 运行 scripts/gen-data.py
      │     ├─ 扫描各分组「知识库」→ 生成 data.json（含 md 正文，供搜索）
      │     └─ 按目录生成 xmind/{分组}-知识图谱.xmind
      └─ 部署到 GitHub Pages
      ↓
https://wby3321-eng.github.io/ProgramReview/
```

> `data.json` 与 `xmind/` 均为部署时生成，**不提交回仓库**（见 `.gitignore`），避免推送冲突。

### 新增笔记（日常高频操作）

只需两步：

```bash
# 1. 把 .md 笔记放到对应知识点目录
cp 我的笔记.md "人工智能/知识库/大语言模型/提示工程/"

# 2. 提交推送 —— 完事
git add -A
git commit -m "归纳：提示工程"
git push
```

等待约 30 秒，网站自动更新：该知识点变为「已复习」，进度条前进，搜索可命中正文。

### 新增知识点目录

```bash
mkdir -p "人工智能/知识库/大语言模型/新知识点"
touch "人工智能/知识库/大语言模型/新知识点/.gitkeep"   # 空目录需占位才会被 git 保留
git add -A && git commit -m "新增知识点：新知识点" && git push
```

### 新增模块或分组

直接建目录即可，前端无需改动；想固定排序就把名称补进 `scripts/gen-data.py` 的 `ORDER_MAP`。

## 🧪 本地调试

```bash
python3 scripts/gen-data.py          # 生成 data.json 与 xmind/
python3 -m http.server 8080          # 启动本地服务
open http://localhost:8080
```

### Pages 设置（一次性）

1. 打开 https://github.com/wby3321-eng/ProgramReview/settings/pages
2. Source 选择 **GitHub Actions**
3. 保存即可（后续全自动）

## 📁 目录结构

```text
ProgramReview/
├── index.html                    # 站点入口
├── assets/
│   ├── style.css
│   └── app.js                    # 树、搜索、脑图、导出
├── scripts/gen-data.py           # 扫描目录生成 data.json 与 xmind
├── .github/workflows/deploy-pages.yml
├── 计算机科学/知识库/...
└── 人工智能/知识库/...
```

## ⚙️ 可调配置

| 文件 | 配置 | 作用 |
| --- | --- | --- |
| `scripts/gen-data.py` | `SCOPE_SUBDIR` | 扫描根目录名，默认 `知识库` |
| `scripts/gen-data.py` | `XMIND_SUFFIX` | 导出文件名后缀 |
| `scripts/gen-data.py` | `RESOURCE_DIR` | 图片资源目录名，不计入知识点 |
| `scripts/gen-data.py` | `EXCLUDE_DIRS` | 扫描时整体跳过的目录 |
| `scripts/gen-data.py` | `ORDER_MAP` | 目录排序表 |
| `assets/app.js` | `EMOJI` / `PALETTE` | 模块图标与配色 |
| `index.html` | 标题与 logo | 站点名称、图标与副标题 |

## 📊 进度口径

- 叶子知识点 = 目录下没有任何子目录，且目录名不是 `resource`
- 叶子目录中存在 `.md` 即视为「已复习」
- 进度 = 已完成叶子数 / 总叶子数
- 图片、PDF 等非 `.md` 文件不计入进度

## ⚠️ 注意事项

- 空目录必须放 `.gitkeep`，否则 git 不保留，页面也不会出现该节点
- 以 `.` 开头的文件或目录在扫描时被忽略
- Markdown 引用图片用相对路径，图片放同目录或 `resource/`
