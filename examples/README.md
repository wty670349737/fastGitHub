# 两个综合大项目

本目录是《Python + AI 开发 15 天实习冲刺教程》的配套综合项目，源码可直接运行。
两个项目彼此独立，各自带 `README.md`、依赖清单和测试。

| 目录 | 主题 | 技术栈 | 亮点 |
|---|---|---|---|
| `01-jd-taobao-spider` | 京东 / 淘宝商品数据采集 | httpx、BeautifulSoup、SQLite | 适配器模式、重试限速、robots 合规、离线样例、去重、CSV/JSON 导出 |
| `02-ecommerce-platform` | 电商平台全栈开发 | FastAPI、SQLModel、Jinja2、SQLite、Docker | 注册登录、商品/购物车/订单/评价、后台管理、CSRF、事务扣库存、AI 文案、pytest |

## 先跑采集项目（零网络）

```powershell
cd 01-jd-taobao-spider
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 再跑电商平台

```powershell
cd ..\02-ecommerce-platform
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

浏览器打开 http://127.0.0.1:8000 ，用 `admin@example.com / admin123` 或 `demo@example.com / demo123` 登录。

## 合规提醒

采集项目仅用于学习 HTTP、解析与工程化。真实采集必须遵守目标站点 `robots.txt`、服务条款、版权和隐私法规，不得绕过登录、验证码或反爬；商用数据请使用京东联盟、淘宝开放平台等官方授权接口。
