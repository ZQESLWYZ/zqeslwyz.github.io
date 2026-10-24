# Yizhao Wang — 个人主页（GitHub Pages 静态站）

版式参照 **<https://shuoyang-1998.github.io/>** 这类经典 jemdoc 学术简历页：

- 灰底（`#eeeeee`）上居中一张 960px 白色卡片，Georgia 衬线正文
- 卡片顶部左右两栏：左栏是姓名 / 职位 / 单位 / 邮箱 / 图标 / **头像**，右栏是各章节
- 章节标题 `h2` 加灰色下边框；列表用方块符号；链接蓝灰 `#224b8d`
- 论文按 `[会议 年份] 标题 / 作者（本人加粗斜体）` 的紧凑格式排列
- 页脚灰色小字：`© Yizhao Wang | Last update: ...`

技术上是**纯静态**：只有 HTML / CSS / JS，没有构建步骤、没有 npm、没有外部 CDN 或第三方字体。

```
index.html               全部内容都在这里（唯一需要改内容的文件）
404.html                 GitHub Pages 自定义 404 页
css/style.css            全部样式（jemdoc 风格 + 响应式 + 打印样式）
js/main.js               只管一件事：头像加载失败时降级为姓名占位块
assets/photo.jpg         头像（248×256）
assets/favicon.svg       站点图标
tools/check_site.py      上线前自检：HTML 标签 / CSS 括号 / JS 语法 / 本地引用（零依赖）
tools/render_check.py    渲染检查：真实浏览器里核对版式、溢出、头像、论文条目
tools/make_preview.py    生成整页预览截图（桌面 / 手机）
.nojekyll                让 Pages 跳过 Jekyll 处理
```

---

## 1. 本地预览与自检

直接双击 `index.html` 即可。想用本地服务器（行为与线上一致）：

```powershell
conda run -n deeplearn python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

改完内容推之前，建议跑一遍自检：

```powershell
# 1) 静态检查（零依赖，随时可跑）
conda run -n deeplearn python tools\check_site.py .

# 2) 渲染检查（需要 websocket-client + Pillow，用本机 Edge/Chrome 无头模式）
conda run -n deeplearn python tools\render_check.py .

# 3) 想看一眼整页效果，生成截图到指定目录
conda run -n deeplearn python tools\make_preview.py . C:\temp\preview
```

`check_site.py` 与 `render_check.py` 全绿时输出 `--- failures --- none`，退出码 0。
`render_check.py` 会核对：样式确实生效、桌面两栏 / 手机单栏、无横向溢出、头像正常加载、
论文 6 条齐全且没有遗留占位、控制台无报错。

---

## 2. 部署到 GitHub Pages

仓库名必须是 `zqeslwyz.github.io`，站点地址即 `https://zqeslwyz.github.io/`。

```powershell
cd C:\Users\Administrator\Documents\zqeslwyz.github.io
git remote add origin https://github.com/zqeslwyz/zqeslwyz.github.io.git
git push -u origin main
```

推送后在仓库 **Settings → Pages**：Source 选 `Deploy from a branch`，Branch 选 `main`、
目录选 `/ (root)`，保存后等 1–2 分钟即可访问。

> 如果仓库名不是 `zqeslwyz.github.io`，站点会挂在 `https://zqeslwyz.github.io/<仓库名>/`。
> `index.html` 用的是相对路径，无需改动；只有 `404.html` 里的 `/css/...`、`/assets/...`、`/`
> 是绝对路径，需要改成 `/仓库名/...`。

之后每次更新：`git add . ; git commit -m "Update homepage" ; git push`

---

## 3. 内容结构

| 章节 | 内容 |
| --- | --- |
| 左栏 | 姓名、Undergraduate Researcher、B.Eng./单位/城市、邮箱、GitHub / Scholar / Email 图标、头像 |
| Short Bio | 两段简介 + 一行 Research interests（由简历改写） |
| Selected Publications | CalibGS (WACV 2027)、Nexus (ACCV 2026) |
| Preprints | 4 篇 arXiv 2026 预印本 |
| Research Projects | 4 个项目，含全部量化指标 |
| Education | 河南科技学院，2023 – 2027，WAM 83.05 / 专业课 88.9 |
| Honors and Awards | 4 项 |

**论文标题与作者已按你给的 `publications.bib` 逐条核对**：

- `wang2026calibgs` → CalibGS: Calibrated Selective Geometric Completion **for 3D Gaussian Splatting**（WACV，2027，唯一作者）
- `wang2026nexus` → Nexus: Structured Synergy for Efficient Text-to-Image Generation **using Rectified Flow Model**（ACCV，2026，唯一作者）
- `wang2026beyond` / `wang2026tpflow` / `wang2026fusion` / `wang2026visibility` → 4 篇预印本，作者列表照 bib 原样填写

`.bib` 里 `note={\textcolor{red}{\textbf{CORE A/B}}}` 是给你自己记的 CORE 等级标注，
**没有**放进网页。

---

## 4. 还可以补的东西（都不阻塞上线）

1. **论文链接**。参考站每条都带 `[Paper] [Code]`。`publications.bib` 里还没有 arXiv 号，
   所以现在没有外链；等号码公开后，在对应条目的作者行下面加一行即可：
   ```html
   <p>[<a href="https://arxiv.org/abs/XXXX.XXXXX">Paper</a>] [<a href="https://github.com/...">Code</a>]</p>
   ```
2. **换一张高清头像（建议）**。现在这张是 248×256、8 KB，显示宽度约 260px，勉强够用但偏糊。
   有更大原图（比如 600×620 以上、< 300 KB）直接覆盖 `assets/photo.jpg` 即可，
   顺手把第 61–62 行 `<img>` 的 `width` / `height` 改成新图的真实像素。
3. **页脚日期**：`Last update: October 2026` 是写死的，改内容时顺手更新。
4. **中文名（可选）**：参考站标题是 `Shuo Yang 杨朔`。想加中文名就改 `<title>` 和第 32 行的 `<h1>`
   （现在只有英文名 —— 我没有你的中文名，没有替你编）。
5. **「开放合作」红字提示（可选）**：`Short Bio` 下方有一段注释掉的示例 `<p style="color:#b00...">`，
   取消注释即可。

---

## 5. 常见修改速查

| 想改什么 | 去哪里 |
| --- | --- |
| 姓名 / 职位 / 单位 / 邮箱 | `index.html` 左栏 `.identity` 区块 |
| 图标链接（GitHub / Scholar / Email） | 左栏 `.links` 里的三个 `<a>` |
| 头像 | 替换 `assets/photo.jpg`（+ 第 61–62 行宽高） |
| 简介与研究方向 | `Short Bio` 两段 `<p>` + `.interests` 一行 |
| 论文条目 | `Selected Publications` 和 `Preprints` 的 `<ul class="pubs">` |
| 项目条目 | `Research Projects` 的 `<ul class="projects">`（子列表是 `<li>` 里的嵌套 `<ul>`） |
| 教育 / 奖项 | 对应章节的 `<ul>` |
| 主色、链接色、字号、卡片宽度 | `css/style.css` 的 `html`、`body`、`a`、`h1/h2/h3` 规则 |

---

## 6. 变更记录

**本版（jemdoc 简历式改造 + 真实论文数据）**

- 按参考站改成 jemdoc 单页版式，**去掉了顶部导航栏和深色模式切换**（参考站没有这两样）。
- 论文从卡片改成 `[会议 年份] 标题` 紧凑列表，本人姓名加粗斜体。
- 项目从卡片改成方块符号列表（项目标题 + 一句 tagline + 缩进子条目）。
- 去掉「Download CV (PDF)」按钮；想保留就把简历编译成 `assets/cv.pdf`，在左栏 `.links`
  里加一行 `<a href="assets/cv.pdf">CV</a>`。
- 新增头像：`assets/photo.jpg` + `js/main.js` 的加载失败降级逻辑。
- 论文标题 / 作者按 `publications.bib` 修正（此前两篇正式论文写的是 `et al.`，实际为唯一作者）。
- 清理了此前误提交进仓库的临时文件，并加了 `.gitignore`。

**上一版**：卡片式设计 + 顶部导航 + 深色模式（已被本版替换）。

---

## 7. 无障碍与兼容性

- 语义化标签、`aria-label`、图片 `alt` 均已处理，键盘可完整操作。
- 头像若缺失，`js/main.js` 会换成带 `role="img"` 与 `aria-label` 的占位块，不会出现破图。
- 响应式：宽度 ≤ 720px 时左右两栏自动变成上下单栏（参考站用的是表格，手机上会挤压，
  这里改成 CSS grid 以保证窄屏可读）。
- 目标浏览器：Chrome / Edge / Safari / Firefox 近两年版本。
