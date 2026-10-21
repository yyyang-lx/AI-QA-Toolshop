# CI 运行记录

## 配置内容

- 工作流：`.github/workflows/pytest.yml`
- 触发条件：`push` 和 `pull_request`
- 运行环境：GitHub-hosted `ubuntu-latest`，Python 3.10
- 安装依赖：`pytest`（测试运行器）和 `requests`（API 客户端）
- 测试范围：仅 `automation/test_product.py` 与 `automation/test_login.py`；未纳入 Playwright UI 测试
- API 地址：`https://api-with-bugs.practicesoftwaretesting.com`
- 代理：`automation/config.py` 将 `requests.Session.trust_env` 设为 `False`，因此测试不会读取环境代理；GitHub runner 需能直连目标 API
- 外部依赖：测试向在线 API 发出真实 GET/POST 请求，服务、DNS 或网络不可用时会导致测试连接失败

项目没有现有依赖清单，因此工作流直接安装这两个测试所需的 Python 包；未修改现有测试代码。

## 本地执行记录

- 执行日期：2026-10-21（本地环境）
- 仓库 HEAD：`78161ce36fb713c096723ff6e29b26c1a2b871ec`
- 执行命令：`python -m pytest automation/test_product.py automation/test_login.py -q`
- 环境：Python 3.10.0，pytest 8.3.4，requests 2.32.3
- 结果：共 8 项，通过 0，失败 8，跳过 0
- 错误分类：8 项均在建立 HTTPS 连接时失败，底层为 Windows `WinError 10013`（套接字访问被拒绝），pytest 报告为 `requests.exceptions.ConnectionError`
- 处理结果：此运行环境阻止了外部套接字连接，无法据此判断 API 产品行为；未删除断言、跳过测试或伪造通过结果。需在允许访问目标 API 的环境重新运行。

## GitHub Actions 状态

- 状态：待验证
- 本次检查时分支为 `feature/test-docs`，相对 `origin/feature/test-docs` 超前 3 个提交；工作树已有用户改动。本次未提交或推送。
- 本机未安装 GitHub CLI（`gh` 命令不可用），未能读取 Actions 执行记录或链接。
- 后续验证：先检查并提交本次新增的 `.github/workflows/pytest.yml` 和本记录，再将目标分支推送到 GitHub；在仓库 Actions 页面检查 `API tests` 工作流的 push 运行结果。创建 PR 时也会由 `pull_request` 触发。运行后将实际结论和运行链接补入本节。
