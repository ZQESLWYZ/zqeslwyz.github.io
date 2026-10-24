# Yizhao Wang — 个人主页（GitHub Pages 静态站）

基于 CleanCV 版 LaTeX 简历内容搭建的**纯静态**个人主页：只有 HTML / CSS / JS，
没有构建步骤、没有 npm、没有外部 CDN 或第三方字体，克隆下来就能直接上线。

```
index.html            # 全部内容都在这里（唯一需要改内容的文件）
404.html              # GitHub Pages 自定义 404 页
css/style.css         # 全部样式：浅色/深色主题、响应式、打印样式
js/main.js            # 主题切换、移动端菜单、导航高亮、页脚年份
assets/favicon.svg    # 站点图标
assets/cv.pdf         # ← 需要你自己放进来（当前缺失，见下文）
.nojekyll             # 让 Pages 跳过 Jekyll 处理
tools/check_site.py   # 上线前自检脚本（HTML 标签 / CSS 括号 / JS 语法 / 本地引用）
```

---

## 1. 本地预览

直接双击 `index.html` 即可。若想用本地服务器（推荐，行为与线上一致）：

```powershell
# 在本目录执行
python -m http.server 8000
# 然后浏览器打开 http://localhost:8000
```

（本机 Python 请用 conda 的 `deeplearn` 环境：`conda run -n deeplearn python -m http.server 8000`）

### 上线前自检（可选）

仓库里带了一个零依赖的静态检查脚本，推送前跑一遍可以挡住最常见的低级错误
（标签没闭合、CSS 括号不匹配、JS 语法错、引用了不存在的本地文件）：

```powershell
conda run -n deeplearn python tools\check_site.py .
```

全部通过时输出 `--- failures --- none`；退出码为 0。若报出缺失文件，修好再推。

---

## 2. 部署到 GitHub Pages

### 目标地址

仓库必须叫 `zqeslwyz.github.io`，站点地址就是 `https://zqeslwyz.github.io/`。

### 方式 A：分支部署（最简单，推荐）

```powershell
cd <本目录>
git init -b main
git add .
git commit -m "Add personal homepage"
git remote add origin https://github.com/zqeslwyz/zqeslwyz.github.io.git
git push -u origin main
```

推送后在仓库里点 **Settings → Pages**：

- **Source**：`Deploy from a branch`
- **Branch**：`main`，目录选 `/ (root)`
- Save，等 1–2 分钟，访问 `https://zqeslwyz.github.io/`

### 方式 B：仓库名不是 zqeslwyz.github.io

那站点会挂在 `https://zqeslwyz.github.io/<仓库名>/` 二级路径下。

- 当前 `index.html` 用的都是**相对路径**（`css/style.css`、`assets/favicon.svg`），二级路径下同样可用，无需改动。
- 只有 `404.html` 里的 `/assets/...`、`/css/...`、`/` 是绝对路径，二级路径部署时把它们改成 `/仓库名/...`。

### 每次更新

```powershell
git add . ; git commit -m "Update homepage" ; git push
```

---

## 3. 待补数据（重要，必须处理）

`index.html` 里现在有 4 处**黄色警示占位块**（标着 `TODO` 徽章），它们对应
`publications.bib` 里我只能看到 key、没有标题的 4 篇预印本：

| bib key                | 需要的字段                     |
| ---------------------- | ------------------------------ |
| `wang2026beyond`       | 标题、全部作者、arXiv 编号/年份 |
| `wang2026tpflow`       | 同上                           |
| `wang2026fusion`       | 同上                           |
| `wang2026visibility`   | 同上                           |

`index.html` 的 `Publications → Preprints` 区块上方有一段 HTML 注释，里面写好了
替换模板：把每条 `<li class="pub" data-todo="...">` 换成注释里的格式，
并**删掉 `data-todo` 属性**（去掉黄色警示样式，换成 `pub-badge-pre` 徽章）。

另外两处**建议核对**（我按 CV 里的措辞写的，没有原始 bib 可对照）：

- CalibGS 条目的作者列表写的是 `Yizhao Wang, et al.`，建议补全合作者。
- Nexus 条目同上；`WACV 2027` / `ACCV 2026` 的会议全称已展开，如果官方名称不同请改。

## 4. 还需要放进来的文件

- **`assets/cv.pdf`**：`index.html` 里有两处链接指向它（顶部导航 `CV PDF`、首屏 `Download CV (PDF)`）。
  用你的 LaTeX 简历（`%!TEX TS-program = lualatex`）编译出 PDF 后放到这个路径；
  如果没有，把这两处 `<a>` 删掉即可。
- 链接预览图（可选）：想自定义社交分享缩略图时，加 `assets/preview.png`（1200×630），
  并在 `<head>` 里补 `<meta property="og:image" content="https://zqeslwyz.github.io/assets/preview.png">`。

---

## 5. 常见修改速查

| 想改什么 | 去哪里 |
| --- | --- |
| 姓名、邮箱、GitHub、Scholar、所在地 | `index.html` 首屏 `hero` 区块 + `<head>` 里的 meta |
| 一句话简介 / 标签 | `hero-tagline`、`hero-eyebrow` |
| 研究方向四张卡片 | `<section id="about">` 里的 `.interest-card` |
| 项目条目 | `<section id="projects">` 里每个 `<article class="project">` |
| 奖项 | `<section id="awards">` 里每个 `<li class="award">` |
| 主色、圆角、页面宽度 | `css/style.css` 顶部 `:root` 变量（`--accent`、`--radius`、`--wrap`） |
| 深色配色 | `css/style.css` 里 `[data-theme="dark"]` 变量块 |

- 新增/删除章节后，记得同步顶部导航 `<nav id="site-nav">` 里的 `<a href="#...">`。
- 导航高亮是 `js/main.js` 里用 `IntersectionObserver` 自动处理的，不需要额外配置。
- 用浏览器「打印 → 另存为 PDF」时，页头、按钮、页脚链接会自动隐藏，只留正文。

---

## 6. 无障碍与兼容性

- 语义化标签（`header`/`nav`/`main`/`section`/`article`/`footer`）、`skip-link`、可见焦点样式、
  `aria-label` / `aria-expanded` 均已处理，键盘可完整操作。
- 主题按钮遵循系统 `prefers-color-scheme`，手动切换后用 `localStorage` 记住；无 JS 时默认浅色，内容照常可读。
- 目标浏览器：Chrome / Edge / Safari / Firefox 近两年版本（用到 `color-mix()`、`clamp()`、CSS 变量）。
