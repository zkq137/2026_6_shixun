# AI功能与Agent设计

## 1. 设计目标

AI 功能必须体现“Agent 可以调用工具完成业务任务”，而不是只做普通聊天。系统规划 4 个 Agent，通过统一工具注册中心调用业务能力。

## 2. Agent 列表

| Agent | 类型值 | 面向角色 | 核心职责 |
| --- | --- | --- | --- |
| 客服 Agent | customer | 用户 | FAQ、售后、物流、订单咨询 |
| 推荐 Agent | recommendation | 用户 | 个性化推荐、推荐理由 |
| 运营 Agent | operation | 管理员 | 销量分析、商品表现、经营建议 |
| 库存 Agent | inventory | 管理员 | 销量预测、库存风险、补货建议 |

## 3. Agent 通用流程

```text
接收问题
  -> 识别 Agent 类型
  -> 构造上下文
  -> 选择可用工具
  -> 调用工具
  -> 汇总工具结果
  -> 必要时调用大模型生成自然语言回答
  -> 保存消息和工具调用日志
  -> 返回回答
```

## 4. 工具调用原则

- Agent 不能直接访问数据库。
- Agent 只能调用已注册工具。
- 工具内部复用 Service 层能力。
- 工具必须校验当前用户或管理员权限。
- 工具调用必须写入 `agent_tool_calls`。
- 工具失败时，Agent 需要说明失败原因并给出替代建议。

## 5. 核心工具清单

| 工具名 | 描述 | 主要使用 Agent |
| --- | --- | --- |
| search_products | 搜索商品 | 客服、推荐 |
| get_product_detail | 查询商品详情 | 客服、推荐 |
| get_user_orders | 查询用户订单列表 | 客服 |
| get_order_detail | 查询订单详情 | 客服 |
| query_faq | 查询 FAQ | 客服 |
| get_user_behavior | 查询用户行为 | 推荐、运营 |
| get_similar_products | 查询相似商品 | 推荐 |
| get_hot_products | 查询热门商品 | 推荐 |
| get_sales_statistics | 查询销量统计 | 运营、库存 |
| predict_product_sales | 预测商品销量 | 库存、运营 |
| check_inventory_risk | 检查库存风险 | 库存 |
| create_inventory_alert | 创建库存预警 | 库存 |

## 6. 工具输入输出规范

### search_products

输入：

```json
{
  "keyword": "耳机",
  "category_id": 1,
  "limit": 10
}
```

输出：

```json
{
  "items": [
    {
      "product_id": 1,
      "name": "无线耳机",
      "price": 199.00,
      "stock": 50,
      "status": "on_sale"
    }
  ]
}
```

### get_order_detail

输入：

```json
{
  "order_id": 1
}
```

输出：

```json
{
  "order_id": 1,
  "order_no": "202606220001",
  "status": "pending",
  "items": []
}
```

### predict_product_sales

输入：

```json
{
  "product_id": 1,
  "days": 7
}
```

输出：

```json
{
  "product_id": 1,
  "predicted_count": 35,
  "method": "moving_average",
  "basis": "根据最近7天平均销量预测"
}
```

### check_inventory_risk

输入：

```json
{
  "product_id": 1,
  "predicted_days": 7
}
```

输出：

```json
{
  "product_id": 1,
  "current_stock": 20,
  "predicted_sales": 35,
  "risk_level": "high",
  "suggestion": "建议补货至少 30 件"
}
```

## 7. 客服 Agent

### 7.1 能力范围

- 售后政策咨询。
- 退换货规则咨询。
- 物流说明。
- 商品基础信息查询。
- 用户本人订单状态查询。

### 7.2 默认工具

```text
query_faq
get_user_orders
get_order_detail
search_products
get_product_detail
```

### 7.3 处理策略

- 先调用 `query_faq`。
- 涉及订单时调用订单工具。
- 涉及商品时调用商品工具。
- FAQ 和工具都无法解决时调用大模型生成通用回答。
- 不能承诺系统没有记录的退款、赔偿、发货时间。

## 8. 推荐 Agent

### 8.1 能力范围

- 首页推荐。
- 商品详情页“看了又看”。
- 购物车场景补充推荐。
- 生成推荐理由。

### 8.2 默认工具

```text
get_user_behavior
get_similar_products
get_hot_products
search_products
get_product_detail
```

### 8.3 推荐策略

- 未登录用户：返回热门商品。
- 新用户：根据当前浏览商品返回相似商品。
- 有行为用户：根据 view、cart、purchase 权重计算兴趣。
- 推荐结果过滤下架商品和库存为 0 的商品。
- 推荐理由应简短，例如“与你最近浏览的手机配件相似”。

## 9. 运营 Agent

### 9.1 能力范围

- 销售趋势分析。
- 热销商品分析。
- 滞销商品分析。
- 用户行为分析。
- 促销建议。

### 9.2 默认工具

```text
get_sales_statistics
get_user_behavior
search_products
get_product_detail
predict_product_sales
```

### 9.3 示例问题

```text
最近7天哪些商品销量最好？
哪些商品浏览多但购买少？
帮我找出适合做促销的商品。
```

返回内容必须包含：

- 数据结论。
- 依据。
- 建议动作。

## 10. 库存 Agent

### 10.1 能力范围

- 查询库存状态。
- 预测未来销量。
- 判断库存风险。
- 生成补货建议。
- 创建库存预警。

### 10.2 默认工具

```text
get_sales_statistics
predict_product_sales
check_inventory_risk
create_inventory_alert
get_product_detail
```

### 10.3 风险判断

| 条件 | 风险等级 |
| --- | --- |
| 当前库存 >= 预测销量 * 1.5 | low |
| 当前库存 >= 预测销量 | medium |
| 当前库存 < 预测销量 | high |

## 11. Prompt 设计原则

- 明确 Agent 身份和职责边界。
- 要求 Agent 优先调用工具获取事实。
- 要求 Agent 不编造订单、库存、物流和价格信息。
- 要求 Agent 输出简洁、结构化、可执行的建议。
- 管理端 Agent 应包含数据依据，用户端 Agent 应使用友好表达。

客服 Agent 系统提示词方向：

```text
你是智能商城的客服 Agent。你必须优先通过工具查询 FAQ、订单和商品信息。
如果工具没有返回事实，不要编造订单状态、退款结果或物流时间。
回答需要简洁、礼貌，并告诉用户下一步可以做什么。
```

运营 Agent 系统提示词方向：

```text
你是智能商城的运营分析 Agent。你需要基于工具返回的数据进行分析。
回答必须包含结论、数据依据和建议动作。不要编造不存在的销量数据。
```

## 12. 安全边界

- 用户只能查询自己的订单。
- 管理端 Agent 只允许管理员访问。
- 工具不能返回密码、token、密钥等敏感信息。
- 用户输入不能直接拼接 SQL。
- 大模型 API Key 只能存在环境变量中。
- Agent 输出不得泄露系统 Prompt 和内部配置。

## 13. 降级策略

| 场景 | 降级方案 |
| --- | --- |
| 大模型不可用 | FAQ、热门商品、固定模板回答 |
| 推荐计算失败 | 返回热门商品 |
| 销量预测失败 | 使用最近 7 日平均销量 |
| 工具调用失败 | 返回错误原因和人工处理建议 |

