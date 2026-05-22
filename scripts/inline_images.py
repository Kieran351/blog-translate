#!/usr/bin/env python3
"""把 HTML 里引用的本地图片转成 base64 data URI，产出真正的单文件。

为什么需要它：HTML 用相对路径引用图片时，文件和图片文件夹必须一起移动，
一旦分离就会破图。把图片内嵌进 HTML 后，整个页面是自包含的——转发、
换设备、离线打开都不会断图。

用法：
    python3 inline_images.py page.html                # 原地覆盖
    python3 inline_images.py page.html -o output.html # 写到新文件

只处理本地图片；已经是 data: 的、或 http(s) 远程图片会原样保留。
退出码非 0 表示有本地图片找不到文件（需要排查）。
"""
import argparse
import base64
import pathlib
import re
import sys
import urllib.parse

MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
    ".bmp": "image/bmp", ".avif": "image/avif", ".ico": "image/x-icon",
}

# 匹配 <img ...> 标签里的 src="..." 或 src='...'
IMG_SRC = re.compile(
    r'(?P<head><img\b[^>]*?\ssrc=)(?P<q>["\'])(?P<src>.*?)(?P=q)',
    re.IGNORECASE | re.DOTALL,
)


def main():
    ap = argparse.ArgumentParser(
        description="把 HTML 中的本地图片内嵌为 base64，做成自包含单文件。")
    ap.add_argument("html", help="HTML 文件路径")
    ap.add_argument("-o", "--output", help="输出路径（默认原地覆盖）")
    args = ap.parse_args()

    html_path = pathlib.Path(args.html).resolve()
    if not html_path.is_file():
        sys.exit(f"找不到文件：{html_path}")

    base_dir = html_path.parent
    html = html_path.read_text(encoding="utf-8")
    done, skipped, missing = [], [], []

    def repl(m):
        src = m.group("src")
        if src.startswith(("data:", "http://", "https://", "//")):
            skipped.append(src)
            return m.group(0)
        # 本地路径：还原 URL 编码字符，相对 HTML 所在目录解析
        img_path = (base_dir / urllib.parse.unquote(src)).resolve()
        if not img_path.is_file():
            missing.append(src)
            return m.group(0)
        mime = MIME.get(img_path.suffix.lower(), "application/octet-stream")
        b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
        done.append(src)
        return f'{m.group("head")}{m.group("q")}data:{mime};base64,{b64}{m.group("q")}'

    new_html = IMG_SRC.sub(repl, html)

    out_path = pathlib.Path(args.output).resolve() if args.output else html_path
    out_path.write_text(new_html, encoding="utf-8")

    for s in done:
        print(f"  内嵌   {s}")
    for s in skipped:
        print(f"  跳过   {s}（远程或已内嵌）")
    for s in missing:
        print(f"  缺失   {s}（找不到文件，已原样保留）")
    size_kb = out_path.stat().st_size // 1024
    print(f"\n内嵌 {len(done)}，跳过 {len(skipped)}，缺失 {len(missing)}")
    print(f"已写入：{out_path}  （{size_kb} KB）")

    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
