# CI 运行记录

## 配置内容

- 工作流：`.github/workflows/pytest.yml`
- 触发条件：`push` 和 `pull_request`
- 运行环境：GitHub-hosted `ubuntu-latest`，Python 3.10
- 安装依赖：从仓库根目录的 `requirements-test.txt` 安装固定版本的 `pytest`（测试运行器）和 `requests`（API 客户端）
- 测试范围：仅 `automation/test_product.py` 与 `automation/test_login.py`；未纳入 Playwright UI 测试
- API 地址：`https://api-with-bugs.practicesoftwaretesting.com`
- 代理：`automation/config.py` 将 `requests.Session.trust_env` 设为 `False`，因此测试不会读取环境代理；GitHub runner 需能直连目标 API
- 外部依赖：测试向在线 API 发出真实 GET/POST 请求，服务、DNS 或网络不可用时会导致测试连接失败

工作流通过 `requirements-test.txt` 安装测试依赖，并使用 pip 缓存减少重复安装时间。工作流只授予 `contents: read` 权限，并设置 10 分钟作业超时。UI 测试仍未纳入工作流，因为它们针对 With Bugs 演示站中已知异常的断言当前会失败；不能将这些预期失败作为必须全绿的 CI 门禁。

依赖文件还包括 `requirements-ui.txt`，用于在本地安装 UI 自动化依赖；CI 当前仅安装 API 测试依赖。

## 本地执行记录

- 执行日期：2026-10-21（本地环境）
- 仓库 HEAD：`78161ce36fb713c096723ff6e29b26c1a2b871ec`
- 执行命令：`python -m pytest automation/test_product.py automation/test_login.py -q`
- 环境：Python 3.10.0，pytest 8.3.4，requests 2.32.3
- 结果：共 8 项，通过 0，失败 8，跳过 0
- 错误分类：8 项均在建立 HTTPS 连接时失败，底层为 Windows `WinError 10013`（套接字访问被拒绝），pytest 报告为 `requests.exceptions.ConnectionError`
- 处理结果：此运行环境阻止了外部套接字连接，无法据此判断 API 产品行为；未删除断言、跳过测试或伪造通过结果。需在允许访问目标 API 的环境重新运行。

### 最近一次本地验证

- 执行日期：2026-10-22（用户反馈）
- 执行范围：商品 API 与登录 API 自动化测试
- 结果：8 项通过
- 环境详情：未记录
- 说明：该结果为用户在可访问目标 API 的环境中运行后提供；不代表 GitHub Actions 已运行成功。

## GitHub Actions 状态

- 最新状态：成功
- 工作流：`API tests`，由 push 事件触发
- 分支与提交：`feature/test-docs`，`bd31aba1c789b6498d168861554608810b808030`
- 执行时间：2026-10-22 11:16（Asia/Shanghai）
- 结果：作业和 `Run API tests` 步骤均成功；该步骤运行商品及登录 API 测试命令。
- 运行记录：[GitHub Actions run 39715942330](https://github.com/yyyang-lx/AI-QA-Toolshop/actions/runs/39715942330)
- 说明：此结果只覆盖 API 工作流，不代表未纳入 CI 的 Playwright UI 用例通过。
