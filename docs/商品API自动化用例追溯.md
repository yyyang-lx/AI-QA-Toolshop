# 商品 API 自动化用例追溯

## 目的与范围

本文将 `automation/test_product.py` 中的 API 自动化用例追溯到 `testcases/Toolshop_测试用例.xlsx` 的手工测试用例。追溯表示场景相关，不表示 API 与 UI 的执行结果可以互相替代。执行状态应以实际测试记录为准。

## 追溯矩阵

| 手工用例 | 手工场景 | 自动化用例 | 覆盖情况 | 说明 |
|---|---|---|---|---|
| TC001 | 输入可匹配商品的关键词 | `test_search_products_by_keyword` | 已覆盖 | 校验状态码、商品结构及名称包含关键词 |
| TC002 | 输入不存在的关键词 | `test_search_products_with_unmatched_keyword` | 已覆盖 | 校验 `data` 及 `total` 为空/为 0 |
| TC003 | 搜索框输入为空 | `test_search_products_with_empty_keyword` | 部分覆盖 | API 验证空字符串请求返回商品；尚未验证 UI 输入框清空、按 Enter/Search 后的页面行为。预期需以实际产品规则为准 |
| TC004 | 搜索关键词前后带空格 | `test_search_products_with_spaces_keyword` | API 场景已覆盖 | 对比首尾带空格与标准 `pliers` 查询的商品 ID 集合，并校验结果商品名称 |
| TC005 | 更换关键词再次搜索 | `test_search_products_with_different_keyword` | API 场景已覆盖 | 同一用例连续查询 `pliers` 和 `hammer`，分别校验结果符合当前关键词且商品集合不同；这验证 API 连续请求行为，不替代 UI 输入框交互检查 |
| TC006 | 点击商品进入详情页 | `test_product_detail_matches_search_result` | API 补充覆盖 | 通过搜索结果取得商品 ID 并请求详情接口，校验详情数据结构；没有验证浏览器页面跳转和可见信息 |
| TC007 | 核对列表与详情页商品名称 | `test_product_detail_matches_search_result` | API 补充覆盖 | 比较搜索接口与详情接口的商品名称；页面渲染一致性仍需 UI 验证 |
| TC008 | 核对商品价格 | `test_product_detail_matches_search_result` | API 补充覆盖 | 比较搜索接口与详情接口的价格；页面格式与显示一致性仍需 UI 验证 |
| — | 纯空格关键词搜索 | `test_search_products_with_whitespace_keyword` | 自动化补充 | 用例表没有单独对应项；作为 API 探索性/补充场景维护 |
| — | 商品列表响应结构与商品字段类型 | `test_product_list_api_returns_json`, `test_product_list_contains_products` | 自动化补充 | 属于 API 契约/数据形状检查，当前手工用例表没有完全对应场景 |
| — | 商品字段校验函数接受有效对象、拒绝无效对象 | `test_product_shape_valid`, `test_product_shape_invalid` | 单元级补充 | 这是测试脚本自身校验逻辑的测试，不是对线上 API 的验证 |
| — | 大小写不敏感搜索 | `test_search_products_by_uppercase_keyword`, `test_search_products_by_mixed_case_keyword` | 自动化补充 | 需确认大小写不敏感是否属于被测系统的明确规则；否则应标为探索性观察 |

测试函数的 docstring 也使用相同的 `[TC编号]` 或 `[自动化补充·类型]` 标识，便于从代码直接定位到本表。辅助函数（如 `get_products`、`assert_product_shape`）是测试工具，不单独对应业务用例。

## 当前范围外的商品相关用例

`test_product.py` 当前聚焦 API，不验证浏览器页面交互。TC006 的页面跳转和 TC007/TC008 的页面展示一致性仍应由 UI 用例确认。TC009（调整商品数量）目前也没有对应的数量修改断言；购物车 UI 脚本现有的行金额用例只检查初始数量。TC010 的加入购物车及购物车内容已有 `automation/test_cart_ui.py` 中的 UI 用例覆盖，但执行结果应单独记录。

## 当前完整度结论

`test_product.py` 已覆盖商品列表结构、商品详情查询及与搜索数据的一致性、关键词搜索、无结果、空关键词、纯空格、有效关键词首尾空格、连续更换关键词及大小写搜索，作为当前范围内的 API 自动化基础已经比较充实。空关键词处理和大小写搜索规则仍应与产品预期确认；详情 API 场景不代表详情页 UI 已覆盖。

另外，测试文件里的 `assert_product_shape` 及其有效/无效对象用例是在验证本地校验函数，不会请求服务端；报告 API 覆盖时应与接口测试分开统计。

## 推荐补齐顺序

1. 确认 TC003 和大小写搜索是否属于明确产品规则，再决定使用稳定断言或作为探索性检查。
2. 为详情页补 UI 校验，并为 TC009 增加实际修改数量后金额更新的验证。
3. 在用例表或本文记录自动化覆盖状态，手工 UI 用例的执行状态仍独立维护。
4. 每次行为或用例发生变化时同步更新追溯矩阵，确保测试用例编号、代码和执行记录能互相定位。
