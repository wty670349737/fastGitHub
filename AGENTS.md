# 项目全局规则（AGENTS.md）

> 适用范围：本仓库所有 AI 会话、代码生成、测试与提交。
>
> 优先级：用户最新明确指令 > 本文件 > 个人习惯。若规则与安全/法律冲突，优先安全/法律。
>
> 工作原则：先读后改、小步提交、每步可验证、失败可回滚。

## 0. 硬性红线（不满足不得交付）

1. 代码必须通过语法检查与现有测试；不能只凭经验说“应该没问题”。
2. 新增/修改的代码必须有中文注释（见第 2 节）。
3. 不得提交密钥、`.env`、数据库、虚拟环境、缓存、大文件（见第 9 节）。
4. 不得删除或覆盖用户未提交的改动；不得执行破坏性命令（`rm -rf`、`git reset --hard`、`drop table` 等），除非用户明确要求。
5. 不得擅自 `commit` / `push` / 改写 Git 历史。
6. 采集必须合规：遵守 `robots.txt`、服务条款与授权范围，限频，不绕过登录、验证码、付费墙或反爬。

## 1. 语言与沟通

- 所有问答、解释、方案、总结、报错分析、提交信息使用**简体中文**；代码标识符、命令、库名、API 名可保留英文。
- 先给结论，再给证据与步骤；报错按“根因 → 最小修复 → 验证命令”回答。
- 不臆造 API、参数、版本、文件路径；不确定时先读代码、依赖或官方文档。
- 大改动先给计划、影响文件、验证方式；确认后再实施。
- 引用代码使用 `文件路径:行号`，便于定位。

## 2. 注释与文档

- 每个模块、类、函数必须有说明用途的 docstring 或等价注释；公共函数写清参数、返回、异常。
- 关键业务逻辑、边界条件、易错点、安全处理、事务、幂等、并发必须有行内注释解释“做什么、为什么”。
- 注释统一中文；禁止复述式注释（如 `i += 1  # i 加 1`）。
- 配置中的非直观字段、魔法值、环境变量必须有中文说明。
- 新增环境变量同步更新 `.env.example`；新增接口/命令同步更新 `README.md` 或 `docs/`。
- Markdown 文档改动后检查代码围栏成对、相对链接可达；流程图/架构图优先用 `mermaid` 代码块。
- 破坏性变更在提交脚注标注 `BREAKING CHANGE:`，说明用中文。

## 3. Python 编码规范（Python 3.12）

- 缩进 4 空格；新增代码行宽建议 ≤ 100 字符；存量代码不强制大规模重排。
- 命名：模块/函数/变量 `snake_case`；类 `PascalCase`；常量 `UPPER_CASE`；私有成员加 `_` 前缀。
- 导入顺序：标准库 → 第三方 → 本地，分组空行；禁止 `from x import *`；避免循环导入。
- 公共函数必须类型注解；优先 `str | None`、`list[str]`、`dict[str, Any]`，不用 `Optional` / `List` 旧写法。
- 字符串优先 f-string；路径用 `pathlib.Path`；文件/连接用 `with` 确保释放。
- 禁止可变默认参数（`def f(x=[])`）；需要时用 `None` 并在函数内初始化。
- 异常：只捕获具体异常；禁止裸 `except:` 和静默 `pass`；重新抛出用 `raise ... from exc`。
- 日志：库代码用 `logging`，不要用 `print`；CLI 面向用户的输出可用 `print`；日志必须脱敏。
- 函数保持单一职责，建议 ≤ 50 行；深层嵌套用早返回。
- 数据优先 `dataclass` / `SQLModel` / Pydantic 模型，避免到处传裸 `dict`。
- 时间使用 timezone-aware；存储用 UTC，展示时再本地化。
- 金额精确计算新代码优先 `Decimal`；存量 `float` 不强制重构，改动需评估兼容性。
- 依赖最小化，优先标准库；引入新依赖必须说明理由并更新 `requirements.txt`。
- 不提交调试代码：`print`、`breakpoint()`、临时 TODO 必须清理或明确标注。

## 4. 项目结构与分层

### 4.1 采集项目 `examples/01-jd-taobao-spider`

- `adapters/`：站点解析；`net/`：HTTP 与 robots；`utils/`：纯函数；`storage.py`：持久化；`pipeline.py`：编排；`main.py`：CLI。
- 新增站点：新建 `adapters/xxx.py` → 在 `adapters/__init__.py` 的 `ADAPTERS` 注册 → 加 fixture → 补测试；不要改 `pipeline.py` 的通用流程。
- 页面结构变化只改对应 adapter，不动存储与 CLI。

### 4.2 电商平台 `examples/02-ecommerce-platform`

- `routers/`：参数、鉴权、响应；`services/`：业务逻辑；`models.py`：数据模型；`security.py` / `deps.py`：认证与权限；`templates/`：展示；`config.py`：配置。
- 新增页面：路由 + 模板 + 导航；新增写操作：CSRF 隐藏字段 + 服务端校验 + 归属校验 + 测试。
- 不在模板写业务逻辑；不在路由写裸 SQL；不跨层直接修改其他模块的内部实现。

### 4.3 通用约定

- 配置只从环境变量 / `.env` 读取，默认值集中在 `config.py`。
- 数据库会话使用 FastAPI 依赖注入，不全局共享 `Session`。
- 列表接口要考虑分页；新增查询避免 N+1 和全表加载。
- 新增文件放在对应层，不要把所有逻辑堆在 `main.py`。

## 5. 安全与合规

- 密钥、Token、密码只从环境变量读取；不写死、不打印、不提交。
- 密码使用 PBKDF2 / bcrypt / argon2 加盐哈希；禁止明文、MD5、SHA1。
- SQL 全部参数化；禁止字符串拼接 SQL。
- 所有写操作校验 CSRF；订单、购物车等资源查询必须校验 `user_id` 归属。
- 输入做类型、长度、范围校验；文件名不直接拼路径；上传限制类型和大小。
- 错误响应不泄露堆栈和内部路径；日志脱敏手机号、邮箱、身份证、银行卡。
- 容器以非 root 运行；镜像和依赖来源可信；遵循最小权限。
- 采集遵守 `robots.txt`、服务条款和授权范围；不绕过登录、验证码、付费墙；不采个人隐私；商用走官方 API。
- 不把公司代码、客户数据、密钥发给公共模型。

## 6. 测试规范

- 新增功能必须补 pytest；修 Bug 先写能复现的失败用例。
- 覆盖正常、边界、异常三类路径；测试名描述行为。
- 用 `tmp_path` / `tempfile` 隔离文件和数据库；测试不依赖真实网络或第三方服务。
- 测试之间不共享可变状态；fixture 负责准备和清理。
- 关键链路必须有测试：采集 → 入库 → 导出；注册 → 加购 → 下单 → 扣库存 → 越权拦截。
- 运行 `pytest -q`；定位用 `pytest -q -x -vv` 或 `--lf`。
- 不为追求覆盖率写无意义断言。

## 7. 编译、运行与验证

- 语法检查用 `compileall` 指定目录/文件，避免扫描 `.venv`。
- 导入检查：`python -c "import 模块"`；Web 项目：`python -c "from app.main import app"`。
- 采集先跑 `--offline`；电商先跑 `pytest` 再启动 `uvicorn`。
- 命令示例兼容 Windows PowerShell 5.1：不用 `&&`，用 `;` 或 `if ($?) { ... }`。
- YAML/JSON 改动后做语法校验（如 `docker compose config`、`python -m json.tool`）。
- Docker 变更：能运行时执行 `docker compose config` / `docker compose up --build`；不能运行时说明原因。
- 验证失败先修复，不带错误交付；确实无法验证时必须说明风险和建议命令。

## 8. 依赖与配置

- 每个项目独立 `.venv`；依赖写入 `requirements.txt`。
- 不随意升级大版本；升级必须跑测试并说明影响。
- 新增环境变量：改 `config.py`、补 `.env.example`、更新 README。
- 敏感配置只放 `.env`，不提交；仓库只保留 `.env.example`。
- 数据库、日志、导出文件、缓存不提交。

## 9. Git 与提交

- 只有用户明确要求才 `commit` / `push`。
- 提交前检查 `git status`、`git diff`，只暂存预期文件；排除 `.env`、`.venv`、`data/`、`__pycache__`。
- 严格遵循强制规则 [`.kilo/rules/git-commit.md`](.kilo/rules/git-commit.md)（与 [`提交规范.txt`](提交规范.txt) 一致）：
  - 格式：`<类型>(<范围>): <简短描述>`
  - 类型：`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `chore` / `ci` / `revert`
  - 简短描述用中文，不超过 50 字，不以句号结尾
  - 正文以 `-` 开头，每行不超过 72 字，说明“做了什么、为什么”
  - 破坏性变更在脚注写 `BREAKING CHANGE:`，说明用中文
- 不强制推送、不改写历史、不跳过 hooks（除非用户明确要求）。
- 一个提交只做一件事；不提交生成物、大文件和密钥。

## 10. AI 协作规则

- 先读相关代码、测试、依赖，再修改；最小 diff，不做无关重构。
- 不假设库已安装；先查 `requirements.txt` 和现有 import；新增依赖说明理由。
- 不臆造接口、字段、命令；以代码和文档为准。
- 修改后立即运行对应验证；失败先修复再继续。
- 大改动先列计划与影响文件；涉及数据迁移、安全、破坏性变更必须先说明风险。
- 不覆盖用户未提交的改动；不删除未知文件；不执行破坏性命令。
- 不修改 `.kilo/agent-manager.json`；不使用 `.kilocode/` / `.opencode/`；新命令/代理放 `.kilo/`。
- 回复给出关键文件路径与行号；不主动 commit / push。

## 11. 本仓库快速命令

```powershell
# 采集项目
cd examples/01-jd-taobao-spider
python -m compileall -q adapters net utils config.py models.py storage.py pipeline.py export.py main.py conftest.py
python -c "import main, pipeline, storage; print('imports ok')"
pytest -q
python main.py

# 电商平台
cd examples/02-ecommerce-platform
python -m compileall -q app tests
python -c "from app.main import app; print(app.title)"
pytest -q
uvicorn app.main:app --reload

# Docker（本机安装 Docker 时）
cd examples/02-ecommerce-platform
docker compose config
docker compose up -d --build
```

## 12. 提交前检查清单

- [ ] 语法检查通过
- [ ] `pytest -q` 全绿
- [ ] 入口可导入/启动
- [ ] 新增/修改代码有中文注释与 docstring
- [ ] 新增/修改测试已补齐
- [ ] 无密钥、`.env`、数据库、缓存、大文件
- [ ] `.env.example`、README/docs 已同步
- [ ] 提交信息符合 `.kilo/rules/git-commit.md`（强制规则）
