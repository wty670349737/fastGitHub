# 大项目一：京东 / 淘宝商品数据采集

> 教学用途的采集框架：统一的商品模型、可插拔站点适配器、重试与限流、robots.txt 合规、SQLite 去重、CSV/JSON 导出。
>
> **重要合规声明**：本项目只用于学习 HTTP、HTML/JSON 解析和工程化组织。真实采集必须遵守目标站点 `robots.txt`、服务条款、版权与《个人信息保护法》等法规，控制频率，不得绕过登录、验证码、付费墙或反爬。商用数据请走京东联盟 / 淘宝开放平台等官方授权 API。仓库内置 HTML 样例，默认离线运行，不需要也不应该对真实站点施压。

## 功能

- 站点适配器：`jd`（服务端渲染列表）、`taobao`（内嵌 JSON + HTML 兜底）
- 统一 `Product` 模型：站点、SKU、标题、价格、店铺、销量、评价数、URL、图片
- HTTP 层：超时、指数退避重试、随机请求间隔、可配置代理
- 合规层：抓取前检查 `robots.txt`
- 存储层：SQLite，`UNIQUE(site, sku)` 天然去重
- 导出：CSV（Excel 友好，`utf-8-sig`）/ JSON
- CLI：`crawl` / `export` / `stats`
- 离线样例：`fixtures/`，零网络也能跑通与测试

## 目录结构

```text
01-jd-taobao-spider/
├─ adapters/            # 站点适配器
│  ├─ base.py           # 抽象基类
│  ├─ jd.py             # 京东
│  └─ taobao.py         # 淘宝
├─ net/
│  ├─ http_client.py    # 重试 / 限速 / 超时
│  └─ robots.py         # robots.txt 检查
├─ utils/text.py        # 价格 / 数字 / 文本清洗
├─ fixtures/            # 离线 HTML 样例
├─ tests/               # pytest
├─ config.py            # 环境变量配置
├─ models.py            # Product / CrawlResult
├─ storage.py           # SQLite 存储
├─ pipeline.py          # 采集流水线
├─ export.py            # CSV / JSON 导出
└─ main.py              # 命令行入口
```

## 快速开始

```powershell
cd examples/01-jd-taobao-spider
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 零配置离线演示（推荐先跑这个）
python main.py

# 只跑京东 / 淘宝
python main.py crawl --site jd --keyword 手机 --offline
python main.py crawl --site taobao --keyword 手机 --offline

# 导出与统计
python main.py export --format csv --site jd
python main.py stats

# 测试
pytest -q
```

真实模式下去掉 `--offline` 即可，但请先阅读上面的合规声明，并把 `SPIDER_DELAY_MIN` 调到 1 秒以上。

## Docker 运行

```powershell
copy .env.example .env
docker compose up --build
# 查看结果
docker compose run --rm spider stats
```

镜像基于 `python:3.12-slim`，以非 root 用户运行，数据保存在命名卷 `spider-data`。
详细步骤见仓库根目录 [`docs/01-项目部署环境过程-Docker.md`](../../docs/01-项目部署环境过程-Docker.md)。

## 运行效果（离线演示）

```text
[jd] 关键词=手机 抓取页=1 解析=3 新增入库=3 跳过=0
数据库累计 3 条，其中 jd 3 条
[taobao] 关键词=手机 抓取页=1 解析=3 新增入库=3 跳过=0
数据库累计 6 条，其中 taobao 3 条
```

## 如何新增一个站点

1. 在 `adapters/` 新建 `xxx.py`，继承 `BaseAdapter`。
2. 实现 `build_search_url(keyword, page)` 和 `parse(html, keyword)`，把字段映射到 `Product`。
3. 在 `adapters/__init__.py` 的 `ADAPTERS` 注册。
4. 在 `fixtures/` 放一份脱敏 HTML 样例，补一个解析测试。

## 真实世界会遇到的坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 返回登录页 / 空列表 | 需要登录或触发风控 | 停止采集；改用官方 API 或授权数据 |
| 页面没有商品 | 列表由 JS 异步渲染 | 优先找内嵌 JSON / 官方接口，必要时用浏览器渲染 |
| 401 / 403 / 429 | 鉴权或限流 | 降低频率、加退避；不要尝试绕过 |
| 选择器失效 | 站点改版 | 适配器隔离了变化，只改一个文件 |
| 重复数据 | 同一商品多页出现 | `UNIQUE(site, sku)` + `INSERT OR IGNORE` |

## 面试话术（3 句话）

1. 我把采集拆成「HTTP 客户端 / 站点适配器 / 解析 / 存储」四层，站点改版只改适配器。
2. 工程上做了超时、指数退避、随机限速、robots 检查和唯一键去重，单页失败不影响整体。
3. 我更强调合规：只采公开且授权允许的数据，商用走官方开放平台，不绕过登录和反爬。
