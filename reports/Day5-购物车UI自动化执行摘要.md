# Day 5：购物车 UI 自动化执行摘要

## 执行信息

- 执行日期与时间：2026-10-21 15:04（Asia/Shanghai）
- 测试对象：With Bugs 在线演示站
- 自动化工具：Python、pytest、Playwright Chromium
- 执行命令：`python -m pytest automation/test_cart_ui.py -q`
- 最终完整运行结果：5 项用例，2 项通过，3 项失败

本摘要记录的是 2026-10-21 当次执行。后续 UI 脚本已调整环境配置、前置条件提示和金额断言；这些改动尚未重新运行，当前结果不能代表更新后脚本的最新状态。

## 用例结果

| 用例 | 结果 | 观察结果 |
|---|---|---|
| 首页打开并显示内容 | 通过 | 首页收到正常响应，标题及可见内容存在 |
| 加入商品并查看购物车 | 通过 | Combination Pliers 加入后购物车数量为 1；购物车商品行和数量 1 均可见 |
| 加入商品后不显示错误提示 | 失败 | 点击 Add to cart 后显示 `Oeps, something went wrong.`；购物车数量仍增加为 1。关联 BUG-001 |
| 购物车行金额与单价、数量一致 | 失败 | 单价为 $14.15、数量为 1，行金额显示 $00.00，底部总价为 $14.15。关联 BUG-002 |
| 删除购物车商品 | 失败 | 点击商品行末尾红色 × 后，商品仍在购物车中，数量仍为 1。关联 BUG-003 |

## 缺陷及截图

截图由失败用例保存到 `bugs/screenshots/`，文件名含执行时间：

- BUG-001：`cart-ui-20261021-150423-378133.png`
- BUG-002：`cart-ui-20261021-150429-368031.png`
- BUG-003：`cart-ui-20261021-150435-206748.png`

三项现象均已关联到现有 `bugs/缺陷记录.csv` 条目，没有重复新建记录。2026-10-21 执行时状态为待人工验证；用户于 2026-10-22 人工复核确认三种行为均不符合预期，当前状态为“已确认，待修复”。BUG-003 的后续独立重跑未加载出商品列表，属于环境/页面数据未就绪，不能当作第二次有效复现。

## 失败分析与复核结论

- BUG-001：商品成功加入且计数正确，但同时出现错误提示；用户已确认该反馈不符合预期。
- BUG-002：商品行金额未按单价与数量计算；用户已确认该展示不符合预期。
- BUG-003：点击删除后商品仍留在清单中；用户已确认该行为不符合预期。
- 一次独立删除场景重跑中，首页打开后未出现 Combination Pliers，脚本等待商品定位超时。该次未执行删除动作，归类为站点/页面数据未就绪，不计入上述 5 项完整运行结果。

## 自动化文件

购物车与首页测试位于 `automation/test_cart_ui.py`。每项用例使用独立浏览器上下文；断言失败时自动尝试保存一张页面截图。目标商品在等待期内未出现时会标记为“前置条件/数据未就绪”，不会报告为购物车操作结果。站点地址可通过 `TOOLSHOP_UI_BASE_URL` 配置；金额断言依据页面当前单价和数量计算，不依赖固定价格。

## BUG-001：前端源码定位补充

### 缺陷信息与复现

- **标题 / 编号：** 加入购物车后页面显示错误提示，但购物车状态已更新（BUG-001）。
- **测试环境：** Practice Software Testing - Toolshop v5.0 With Bugs 在线演示站；浏览器 Network 与 Application 面板。既有自动化使用 Playwright Chromium。
- **复现步骤：** 打开商品详情页；点击 Add to cart；观察页面提示和购物车数量；在 Network 的 All 分类检查新增请求，并在 Application → Session Storage 检查 `cart`。
- **预期：** 加购成功时应显示成功反馈，购物车状态与页面反馈一致。
- **实际：** 用户确认 `sessionStorage` 在点击后变化；页面显示 `Oeps, something went wrong.`；Network 对比中收藏操作出现新增请求，而加入购物车操作未出现新增请求。用户还确认收藏请求成功后也出现同一条 `Oeps` toast。

### 发现过程与证据链

1. **页面现象：** 既有自动化截图 `bugs/screenshots/cart-ui-20261021-150423-378133.png` 显示加购错误提示；同次执行购物车数量变为 1，商品及数量 1 可在购物车中看到。用户后续确认当前页面实际显示 `Oeps`。
2. **Network 对比：** 用户观察到收藏新增请求、加购无新增请求。该观察与下列源码调用链一致；本报告未另行采集 HAR 或网络日志。
3. **Session Storage：** 用户确认点击加购时购物车 `sessionStorage` 发生变化。
4. **源码调用链：** 在公开上游仓库的 `sprint5-with-bugs` 版本中，商品详情模板分别将按钮绑定到 `addToFavorites(product)` 与 `addToCart(product)`（[detail.component.html](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5-with-bugs/UI/src/app/products/detail/detail.component.html#L84)）。`DetailComponent.addToFavorites` 构造 `product_id` 后调用 FavoriteService；`FavoriteService.addFavorite` 通过 `HttpClient.post` 请求 `API_URL + '/favorites'`（[detail.component.ts](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5-with-bugs/UI/src/app/products/detail/detail.component.ts#L86)、[favorite.service.ts](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5-with-bugs/UI/src/app/_services/favorite.service.ts#L14)）。
5. `DetailComponent.addToCart` 组装商品对象并调用 `CartService.addItem(item)`，随后直接显示错误 toast；`CartService.addItem` 将购物车写入 `sessionStorage` 并发出 `storageSub` 变更通知，未调用购物车 API（[detail.component.ts](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5-with-bugs/UI/src/app/products/detail/detail.component.ts#L117)、[cart.service.ts](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5-with-bugs/UI/src/app/_services/cart.service.ts#L16)）。
6. 同一组件中，`addToFavorites` 的 `next` 成功回调也显示 `Oeps, something went wrong.`；错误回调则分别处理重复收藏与未授权情况（[detail.component.ts](https://github.com/testsmith-io/practice-software-testing/blob/main/sprint5-with-bugs/UI/src/app/products/detail/detail.component.ts#L86)）。因此，这条 toast 来自组件的操作回调，不是购物车 API 的异常响应。

### 定位结论与判断边界

- **已确认现象：** 页面显示 `Oeps`，加购后本地购物车状态变化；收藏成功后也显示同一条错误 toast。用户已在浏览器确认以上行为。
- **源码支持的定位结论：** 加购处理路径只更新前端 `sessionStorage`，而收藏处理路径发送 `POST /favorites`。两者调用的服务和状态持久化方式不同。加购的错误 toast 在本地状态更新后直接调用；收藏的错误 toast 位于 `next` 成功回调中。
- **证据支持的根因判断：** BUG-001 的错误提示来自前端成功路径中的 toast 调用，与加购本地状态更新并行发生；源码未显示加购请求失败。收藏成功后出现相同 toast，进一步支持提示逻辑被错误地放在成功路径这一判断。
- **仍待验证：** 公开上游 `main` 源码与演示站当前实际部署 bundle 的版本对应关系；Network 请求完整 URL、状态码及响应体；收藏操作之后端数据是否确实持久化；提示是否还会被其他全局逻辑覆盖。当前没有本地被测网站源码、HAR 或后端日志。
- **影响：** 用户可能把成功操作误认为失败并重复点击；这也使收藏和加购的用户反馈都不可信。加购目前使用浏览器会话存储，刷新/新会话后的持久化行为不由本次证据覆盖。

### 修复方向与回归点

- **建议修复方向：** 将成功 toast 放在真实成功分支并使用成功文案；失败提示只在失败分支触发。加购当前是本地状态操作，应在状态更新后显示成功反馈，不应复用错误提示。收藏则应根据 HTTP 成功/失败结果分别反馈。
- **修复后回归：** (1) 加购后 `cart` sessionStorage、购物车徽标及购物车行一致；(2) 加购成功不显示错误 toast；(3) 收藏成功产生预期 POST 并显示成功反馈；(4) 重复收藏、未授权等失败响应显示对应错误且不误报成功；(5) Network 请求过滤与状态变化检查相互印证。

### 截图与自动化覆盖

- **已有证据截图：** `cart-ui-20261021-150423-378133.png`（BUG-001 页面状态）；目录中还保留 BUG-002 截图 `cart-ui-20261021-150429-368031.png` 和 BUG-003 截图 `cart-ui-20261021-150435-206748.png`。本次排查未伪造新截图。
- **现有覆盖：** `test_add_product_and_open_cart` 检查购物车数量和商品行；`test_add_to_cart_does_not_show_error` 检查错误提示。两者原先分开验证，没有在同一用例中先确认状态变化再断言无错误提示。
- **本次最小补充：** 在错误提示测试中先断言购物车徽标为 1，再检查错误提示；这样能明确建立“状态已更新但反馈错误”的关联，同时保留“成功操作不应出现错误提示”的严格预期。该回归用例在缺陷修复前会按预期失败。本次未运行测试；既有执行记录仍是 2026-10-21 的结果，不能视为本次测试结果。
