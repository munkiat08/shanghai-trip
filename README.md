# shanghai-trip

上海 · 苏州 · 乌镇 · 杭州 9 天（2027-03-08 至 03-16）行程，高德地图链接，Excel 驱动，带每日穿搭。

Live site: https://shanghai-trip.munkiat.workers.dev/ (Cloudflare Workers, serves only `public/`).

## 文件

- `trip_data.json`：行程主数据；`build_data.py` 是最初的生成脚本
- `trip.xlsx`：简化的 Excel（行程 + 美食），用 `excel_tool.py` 导出 / 导入
- `theme_palette.py`：生成页面，写入 `itinerary/` 和 `public/index.html`（配色 #41436A / #984063 / #F64668 / #FE9677）
- `outfit/`：穿搭图片提示词（`outfit_image_prompts.md`）、原图（`outfit_images/`）和穿搭标签生成脚本（`outfit_html.py`）

## 更新

1. 改行程：`python excel_tool.py export` → 改 `trip.xlsx` → `python excel_tool.py import`（或直接改 `trip_data.json`）
2. 改穿搭：换 `outfit/outfit_images/` 里的图或改 `outfit/outfit_html.py`，运行 `python outfit/outfit_html.py`（压缩图片并去掉右下角水印）
3. 生成页面：`python theme_palette.py` → `public/index.html`
4. 提交并推送，线上网站会更新

重新生成页面需要本机 `~/.claude/skills/china-amap-rednote-itinerary/`，只能在作者电脑上运行。
