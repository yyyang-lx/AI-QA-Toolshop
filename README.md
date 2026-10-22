# AI-QA-Toolshop

基于 AI 辅助的电商 Web 系统质量保障实践，重点关注测试设计、缺陷分析、风险评估与测试文档交付，并通过少量自动化测试探索核心场景的质量保障方式。

## 1. 项目介绍

本项目以 [Practice Software Testing](https://with-bugs.practicesoftwaretesting.com/) 的 With Bugs 在线演示版本为测试对象，围绕电商 Web 系统的主要业务场景开展测试实践。

项目以测试思维和质量保障为主，自动化测试为辅，重点验证功能表现、异常输入处理、业务状态一致性及页面反馈的合理性。

## 2. 测试范围

| 测试模块 | 主要内容 |
|---|---|
| 商品搜索 | 关键词搜索、无结果搜索、空格输入、关键词切换 |
| 商品分类筛选 | 分类切换、取消筛选、组合筛选 |
| 商品详情 | 页面信息展示、名称与价格一致性、购买数量 |
| 购物车 | 添加商品、重复添加、数量修改、金额计算、删除、刷新后的状态 |
| 注册与登录 | 页面展示、部分异常场景验证 |
| 边界与异常场景 | 数量为 0、负数、小数及非数字输入 |

测试以手工功能测试为主。注册登录模块受测试账号状态影响，尚未完成完整流程验证。

## 3. 测试方法

- 功能测试
- 等价类测试
- 边界值测试
- 异常场景测试
- 页面展示与数据一致性检查
- 状态保持验证
- 基于风险的测试分析

## 4. 项目成果

当前项目已整理以下测试交付物：

- 测试方案与风险分析
- 参考项目调研
- 测试用例及执行记录
- 缺陷记录（BUG-001 至 BUG-006）
- 测试执行摘要
- 测试总结报告

测试过程中记录了多项待进一步确认的异常，包括加入购物车后错误提示与实际状态不一致、购物车行内金额展示异常、删除商品操作无响应、重复添加商品失败等。

上述记录反映的是当前测试环境下观察到的现象，不代表所有问题均已完成根因分析或确认修复状态。

## 5. 项目目录

```text
AI-QA-Toolshop/
├── .github/
│   └── workflows/
│       └── pytest.yml          # API 测试工作流
├── automation/                 # 自动化测试脚本
├── bugs/                       # 缺陷记录
├── docs/                       # 测试方案、风险分析及总结报告
├── reports/                    # 测试执行摘要
├── testcases/                  # 测试用例及设计说明
├── requirements-test.txt       # API 测试依赖
├── requirements-ui.txt         # UI 测试依赖
├── .gitignore
└── README.md
```

## 6. 测试环境

- **测试对象：** Practice Software Testing - With Bugs
- **测试类型：** Web 功能测试、边界值测试、异常场景测试
- **主要方式：** 手工测试
- **自动化工具：** Python、pytest、requests；UI 测试使用 Playwright Chromium

测试网站：[With Bugs 在线演示环境](https://with-bugs.practicesoftwaretesting.com/)

项目源站：[Practice Software Testing GitHub](https://github.com/testsmith-io/practice-software-testing)

## 7. 自动化测试说明

项目包含 `automation/` 目录，用于存放自动化测试脚本。

自动化测试覆盖少量 API 和 UI 核心场景。API 测试适合在 CI 中运行；UI 测试连接在线 With Bugs 演示站，部分断言对应已记录的异常，当前仅供手动执行和查看证据。

### API 自动化测试

环境要求：Python 3.10。安装测试依赖并运行 API 用例：

```bash
python -m pip install -r requirements-test.txt
python -m pytest automation/test_product.py automation/test_login.py -q
```

API 用例会访问在线演示 API，因此运行结果受目标服务和网络状态影响。当前 GitHub Actions 工作流运行这组 API 用例。

### UI 自动化测试

`automation/test_cart_ui.py` 使用 Playwright。安装 UI 测试依赖及 Chromium 浏览器后，可运行：

```bash
python -m pip install -r requirements-ui.txt
python -m playwright install chromium
python -m pytest automation/test_cart_ui.py -q
```

UI 测试默认访问 With Bugs 演示站。可通过 `TOOLSHOP_UI_BASE_URL` 环境变量切换站点地址。商品在规定等待时间内未出现时，测试会以“前置条件/数据未就绪”标记失败；断言失败时会尝试保存一张截图到 `bugs/screenshots/`。UI 用例针对演示站中已记录的异常，部分断言当前预期会失败；执行结果应结合 `bugs/缺陷记录.csv` 和对应执行摘要解读。

## 8. 项目复盘

本项目的重点不只是验证页面能否正常操作，还包括：

1. 通过不同输入和业务场景设计测试用例。
2. 结合实际执行结果识别功能异常。
3. 分析异常可能造成的用户影响与质量风险。
4. 区分已观察现象、待确认问题与已确认缺陷。
5. 使用测试文档记录测试过程，提高结果的可追溯性。

后续将继续完善自动化测试、缺陷分析及项目交付材料。
