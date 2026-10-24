# Yizhao Wang — 个人主页（GitHub Pages 静态站）

版式参照 **<https://shuoyang-1998.github.io/>** 这类经典 jemdoc 学术简历页：

- 灰底（`#eeeeee`）上居中一张 960px 白色卡片，Georgia 衬线正文
- 卡片顶部左右两栏：左栏是姓名／职位／单位／邮箱／图标／**头像**，右栏是各章节
- 章节标题 `h2` 加灰色下边框；列表用方块符号；链接蓝灰 `#224b8d`
- 论文按 `[会议 年份] 标题 / 作者（本人加粗斜体）/ [Paper] [Code]` 的紧凑格式排列
- 页脚灰色小字：`© Yizhao Wang | Last update: ...`

技术上是**纯静态**：只有 HTML / CSS / JS，没有构建步骤、没有 npm、没有外部 CDN 或第三方字体。

```
index.html            全部内容都在这里（唯一需要改内容的文件）
404.html              GitHub Pages 自定义 404 页
css/style.css         全部样式（jemdoc 风格 + 响应式 + 打印样式）
js/main.js            只管一件事：头像缺失时降级为姓名占位块
assets/favicon.svg    站点图标
assets/photo.jpg      ← 需要你自己放进来（当前缺失，见第 4 节）
tools/check_site.py   上线前自检脚本
.nojekyll             让 Pages 跳过 Jekyll 处理
```

---

## 1. 本地预览

直接双击 `index.html` 即可。想用本地服务器（行为与线上一致）：

```powershell
conda run -n deeplearn python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

### 上线前自检（推荐）

```powershell
conda run -n deeplearn python tools\check_site.py .
```

检查 HTML 标签闭合、CSS 括号、JS 语法、本地引用是否都存在；全通过时输出
`--- failures --- none`，退出码 0。因为头像还没上传，会有一条 warning，属正常。

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

| 章节 | 内容来源 |
| --- | --- |
| 左栏 | 姓名、Undergraduate Researcher、B.Eng./单位/城市、邮箱、GitHub / Scholar / Email 图标、头像 |
| Short Bio | 两段简介 + 一行 Research interests（由简历改写） |
| Selected Publications | CalibGS (WACV 2027)、Nexus (ACCV 2026) |
| Preprints | 4 篇占位（见第 4 节） |
| Research Projects | 4 个项目，含全部量化指标 |
| Education | 河南科技学院，2023 – 2027，WAM 83.05 / 专业课 88.9 |
| Honors and Awards | 4 项 |

---

## 4. 待补数据（必须处理）

1. **头像**。参考站在左栏放了照片，位置已经留好：把照片存成 `assets/photo.jpg`
   （竖版 4:5 左右最合适，如 600×750，单张 < 300 KB）即可。
   在照片就位之前，页面会自动显示一个虚线框的「YW / add assets/photo.jpg」占位块
   —— **不会出现破图**，但上线前请务必换成真实照片。
2. **4 篇预印本占位**。`index.html` 中 `Preprints` 下的 4 条黄色高亮条目对应
   `publications.bib` 里只有 key、没有标题的论文：

   | bib key | 缺什么 |
   | --- | --- |
   | `wang2026beyond` | 标题、全部作者、arXiv 编号/年份 |
   | `wang2026tpflow` | 同上 |
   | `wang2026fusion` | 同上 |
   | `wang2026visibility` | 同上 |

   替换方法：照着上面两条正式条目的写法把 `<li class="todo">` 改成普通 `<li>`
   （去掉 `class="todo"` 就没黄色底色了）；区块上方的 HTML 注释里有说明。
3. **作者列表**：CalibGS / Nexus 两条现在写的是 `Yizhao Wang, et al.`，请补全合作者。
   本人姓名在页面上是加粗斜体（对应参考站的 `<b><i>Shuo Yang</i></b>` 写法）。
4. **论文链接**：参考站每条都带 `[Paper] [Code]`。等链接公开后，按
   `<p>[<a href="URL">Paper</a>] [<a href="URL">Code</a>]</p>` 加在作者行下面。
5. **页脚日期**：`Last update: October 2026` 是写死的，改内容时顺手更新。
6. **中文名（可选）**：参考站标题是 `Shuo Yang 杨朔`。想加中文名的话，改
   `<title>` 和第 32 行的 `<h1>`（现在的标题只有英文名——我没有你的中文名，没有替你编）。

---

## 5. 常见修改速查

| 想改什么 | 去哪里 |
| --- | --- |
| 姓名 / 职位 / 单位 / 邮箱 | `index.html` 左栏 `.identity` 区块 |
| 图标链接（GitHub / Scholar / Email） | 左栏 `.links` 里的三个 `<a>` |
| 简介与研究方向 | `Short Bio` 两段 `<p>` + `.interests` 一行 |
| 论文条目 | `Selected Publications` 的 `<ul class="pubs">` |
| 项目条目 | `Research Projects` 的 `<ul class="projects">`（子列表是 `<li>` 里的嵌套 `<ul>`） |
| 教育 / 奖项 | 对应章节的 `<ul>` |
| 主色、链接色、字号、卡片宽度 | `css/style.css` 的 `html`、`body`、`a`、`h1/h2/h3` 规则 |
| 想加一条「开放合作/招生」红字提示 | `Short Bio` 下方有一段注释掉的示例 `<p style="color:#b00...">`，取消注释即可 |

---

## 6. 比起上一版做了什么改动

上一版是一套卡片式、带顶部导航和深色模式的设计。为了贴合参考站，本版：

- 改成 jemdoc 单页版式：**去掉了顶部导航栏和深色模式切换**（参考站没有这两样）；
  需要的话可以再加回来。
- 论文从卡片改成 `[会议 年份] 标题` 紧凑列表，本人姓名加粗斜体。
- 项目从卡片改成方块符号列表（项目标题 + 一句 tagline + 缩进子条目）。
- 「Download CV (PDF)」按钮去掉了（参考站没有）。想保留的话，把你的 LaTeX 简历
  编译成 `assets/cv.pdf`，然后在左栏 `.links` 里加一行
  `<a href="assets/cv.pdf">CV</a>` 就行。
- 新增 `js/main.js` 的头像降级逻辑。

---

## 7. 无障碍与兼容性

- 语义化标签、`aria-label`、图片 `alt` 均已处理，键盘可完整操作。
- 头像占位块带 `role="img"` 与 `aria-label`，读屏不会读到空元素。
- 响应式：宽度 ≤ 720px 时左右两栏自动变成上下单栏（参考站用的是表格，手机上会挤压，
  这里改成了 CSS grid 以保证窄屏可读）。
- 目标浏览器：Chrome / Edge / Safari / Firefox 近两年版本。
