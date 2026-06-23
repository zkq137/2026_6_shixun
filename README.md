# AI智能商城系统

AI智能商城系统是一个面向实训项目的轻量电商平台。系统覆盖商品展示、搜索、购物车、下单、订单管理、后台商品管理等基础业务，并以多 Agent 与工具调用作为核心亮点，展示 AI 在客服、推荐、运营分析和库存预测中的实际应用。

## 技术栈

- 后端：Python、FastAPI、SQLAlchemy 2.x、Pydantic、Uvicorn
- 前端：Vue3、Vite、Pinia、Vue Router、Element Plus
- 数据库：MySQL
- 缓存：Redis，可选，用于热点商品、推荐结果、会话缓存
- AI：多 Agent 架构、工具调用、大模型 API 适配层
- 测试：pytest、httpx、前端组件测试或手工验收

## 项目目标

本项目不是单纯的商品管理系统，而是一个具备智能化能力的电商业务系统。开发完成后应支持：

- 用户浏览、搜索、购买商品。
- 管理员维护商品、分类、订单和库存。
- 系统记录用户浏览、加购、购买等行为。
- 推荐 Agent 根据用户行为推荐商品并生成推荐理由。
- 客服 Agent 通过 FAQ 和工具调用回答售后、物流、订单问题。
- 运营 Agent 分析热销、滞销、销售趋势和用户行为。
- 库存 Agent 根据销量预测库存风险并给出补货建议。

## AI 亮点

系统固定规划 4 个 Agent：

| Agent | 面向角色 | 主要职责 |
| --- | --- | --- |
| 客服 Agent | 用户 | 回答 FAQ、退换货、物流、订单状态等问题 |
| 推荐 Agent | 用户 | 结合用户行为和商品相似度生成推荐 |
| 运营 Agent | 管理员 | 分析销量、热销商品、滞销商品、用户行为 |
| 库存 Agent | 管理员 | 预测销量、识别库存风险、生成补货建议 |

Agent 统一通过工具工作，不能直接访问数据库。核心工具包括：

```text
search_products
get_product_detail
get_user_orders
get_order_detail
query_faq
get_user_behavior
get_similar_products
get_hot_products
get_sales_statistics
predict_product_sales
check_inventory_risk
create_inventory_alert
```

## 文档目录

- [需求规格说明书](docs/01-需求规格说明书.md)
- [系统架构设计](docs/02-系统架构设计.md)
- [数据库设计](docs/03-数据库设计.md)
- [接口设计](docs/04-接口设计.md)
- [AI功能与Agent设计](docs/05-AI功能与Agent设计.md)
- [前端页面设计](docs/06-前端页面设计.md)
- [开发计划](docs/07-开发计划.md)
- [测试与验收方案](docs/08-测试与验收方案.md)
- [部署运行说明](docs/09-部署运行说明.md)

## 推荐开发顺序

1. 搭建 FastAPI 后端、Vue3 前端和 MySQL 数据库。
2. 完成用户、商品、分类、购物车、订单等电商基础业务。
3. 完成后台管理，包括商品、订单、库存和用户管理。
4. 增加用户行为记录，为推荐和运营分析提供数据。
5. 实现 FAQ 客服、热门推荐、看了又看等基础 AI 功能。
6. 实现多 Agent 编排和工具调用日志。
7. 完成销量预测、库存预警和后台 AI 运营助手。
8. 准备演示数据、测试用例和答辩说明。


## 2026-06-23 更新：商品图片上传

后台商品管理已支持管理员上传、预览、替换、清空商品主图。上传接口为：

```text
POST /api/admin/uploads/product-image
```

上传文件保存到：

```text
backend/uploads/products/
```

生产环境需要配置 Nginx 暴露 `/uploads/`，详见 `docs/09-部署运行说明.md` 和 `docs/12-服务器更新维护指南.md`。
