# blog-translate

把网页博客 / 文章翻译成**保留原排版的中文 HTML 单文件**的 Claude Code 技能（Skill）。

给一个博客链接，输出一个自包含的 `.html`：中文译文、图片 base64 内嵌、链接可跳转、复刻原文的阅读排版。

## 特性

- **单文件自包含** —— 图片以 base64 内嵌，转发 / 换设备 / 离线打开都不断图
- **保留原排版** —— 标题、列表、引用块、代码块、配图按原文结构逐块还原
- **复刻博客阅读体验** —— 窄阅读栏、定义块 callout、图注、代码块、移动端响应式
- **配图点击放大** —— 内置 lightbox，点图在页内放大查看，不跳转外部
- **链接可跳转** —— 正文链接保留，并在新标签打开
- **任意外语 → 中文**

## 安装

这是一个 Claude Code 技能。把本仓库克隆为技能目录即可：

```bash
# 用户级（所有项目可用）
git clone https://github.com/Kieran351/blog-translate.git ~/.claude/skills/blog-translate

# 或项目级（仅当前项目）
git clone https://github.com/Kieran351/blog-translate.git .claude/skills/blog-translate
```

## 使用

在 Claude Code 里直接给出链接：

```
把 https://example.com/某篇文章 转成中文版
```

技能会自动：抓取正文 → 翻译 → 套用模板生成 HTML → 内嵌图片 → 渲染验证 → 输出到 `outputs/`。

## 仓库结构

```
blog-translate/
├── SKILL.md               技能说明 + 8 步工作流
├── scripts/
│   └── inline_images.py   把本地图片转 base64，做成自包含单文件
└── assets/
    └── template.html      复刻博客排版的 HTML 骨架（含 lightbox）
```

## 工作流

1. 拿到文章 URL
2. 通过 web-access 技能用浏览器 CDP 抓取正文（结构化提取）
3. 抓取配图（滚动触发懒加载，只取正文区块）
4. 保留原排版逐块翻译
5. 套用 `template.html` 生成 HTML
6. 用 `inline_images.py` 把图片内嵌成单文件
7. 渲染验证
8. 输出到 `outputs/`，清理临时文件

详见 [SKILL.md](SKILL.md)。

## 依赖

- **Claude Code**
- **web-access 技能** —— 负责浏览器 CDP 抓取（博客平台多需登录态 / 反爬）
- **Python 3** —— `inline_images.py` 仅使用标准库，无需额外安装
- **Chrome** —— 开启 remote debugging，供 CDP 连接

## 单独使用内嵌脚本

`inline_images.py` 也可独立用于任意 HTML 文件：

```bash
python3 scripts/inline_images.py page.html              # 原地覆盖
python3 scripts/inline_images.py page.html -o out.html  # 输出到新文件
```

它会把 HTML 里引用本地图片的 `<img>` 全部转成 base64 data URI，远程图片和已内嵌的会自动跳过。
