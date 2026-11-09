# 项目全局规则（AGENTS.md）

> 本文件是项目的全局指令，对所有 AI 会话、代码生成与提交生效。优先级高于个人习惯；如与临时指令冲突，以用户最新明确指令为准。

## 1. 语言规则：必须使用中文

- 所有 AI 问答、解释、方案、总结、报错分析、提交信息，一律使用**简体中文**回答。
- 代码中的标识符、命令、库名、API 名等技术专有名词可保留英文，但说明文字必须是中文。
- 不得用英文整段回复；确需引用英文原文时，应附中文解释。

## 2. 注释规则：所有代码必须有注释

- 所有新增或修改的代码都必须带注释，包括但不限于 Python、JavaScript/TypeScript、Shell、SQL、YAML、Dockerfile、HTML 模板。
- 每个模块、类、函数必须有说明用途的文档字符串（docstring）或等价注释。
- 关键业务逻辑、边界条件、易错点、安全相关处理，必须有行内注释解释“做什么、为什么”。
- 注释统一使用中文；禁止无意义的复述式注释（例如 `i += 1  # i 加 1`）。
- 配置文件中的非直观字段、魔法值、环境变量，同样需要中文注释说明。

## 3. 验证规则：写完必须编译/测试通过

- 任何代码写完后，必须实际运行验证，确保**编译通过、无语法错误、可正常导入/启动、测试通过**，不能只凭经验判断“应该没问题”。
- Python 项目的最低验证：
  - 语法检查：`python -m compileall <目录>` 或 `python -m py_compile <文件>`
  - 有测试：`pytest -q`
  - 有入口：实际运行一次启动命令，确认无异常
- 其他语言按项目标准命令验证（如 `npm run build`、`tsc --noEmit`、`go build ./...`）。
- 如果环境限制导致无法运行验证，必须在结果中明确说明：未验证的原因、可能的风险、建议的验证命令；不得默认为通过。

## 4. 本仓库的快速验证命令

```powershell
# 采集示例
cd examples/01-jd-taobao-spider
python -m compileall .
pytest -q
python main.py

# 电商平台示例
cd examples/02-ecommerce-platform
python -m compileall app
pytest -q
python -c "from app.main import app; print(app.title)"
```

> 提交前至少保证：语法检查通过 + `pytest -q` 全绿；新增代码注释齐全；回复为中文。
