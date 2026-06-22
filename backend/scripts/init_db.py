from __future__ import annotations

import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Admin,
    AgentToolCall,
    AiConversation,
    AiMessage,
    Category,
    Faq,
    InventoryAlert,
    Order,
    OrderItem,
    Product,
    ProductSimilarity,
    RecommendResult,
    SalesPrediction,
    SalesStatistic,
    User,
    UserBehavior,
)


CATEGORIES = [
    "数码电子",
    "服饰鞋包",
    "家居生活",
    "美妆个护",
    "食品饮料",
    "运动户外",
]

PRODUCTS = [
    ("数码电子", "轻薄无线蓝牙耳机", "低延迟连接，通勤运动都适合", "199.00", 120),
    ("数码电子", "智能降噪头戴耳机", "沉浸式降噪，长续航", "499.00", 48),
    ("数码电子", "65W 快充充电器", "多协议快充，适合手机和平板", "89.00", 210),
    ("数码电子", "机械键盘青轴版", "清脆手感，办公游戏两用", "269.00", 75),
    ("数码电子", "高清网络摄像头", "1080P 视频会议摄像头", "159.00", 64),
    ("服饰鞋包", "纯棉基础短袖", "柔软透气，日常百搭", "59.00", 300),
    ("服饰鞋包", "轻量运动跑鞋", "缓震鞋底，适合慢跑", "239.00", 95),
    ("服饰鞋包", "通勤双肩背包", "大容量分区，适合电脑出行", "189.00", 86),
    ("服饰鞋包", "防晒轻薄外套", "轻便防晒，夏季户外适用", "129.00", 140),
    ("服饰鞋包", "商务休闲皮带", "简约扣头，日常通勤", "79.00", 110),
    ("家居生活", "人体工学办公椅", "腰背支撑，久坐更舒适", "699.00", 34),
    ("家居生活", "便携保温杯", "316 不锈钢内胆，保温保冷", "69.00", 260),
    ("家居生活", "智能台灯", "多档调光，护眼阅读", "149.00", 78),
    ("家居生活", "收纳整理箱三件套", "透明可叠放，节省空间", "99.00", 180),
    ("家居生活", "床上四件套", "亲肤面料，简约配色", "229.00", 52),
    ("美妆个护", "氨基酸洁面乳", "温和清洁，适合日常使用", "49.00", 220),
    ("美妆个护", "清爽保湿乳液", "补水不黏腻，四季可用", "89.00", 150),
    ("美妆个护", "便携电动牙刷", "高频震动，旅行便携", "129.00", 92),
    ("美妆个护", "防晒霜 SPF50", "轻薄防晒，户外通勤", "79.00", 170),
    ("美妆个护", "香氛沐浴露", "温和留香，泡沫细腻", "59.00", 130),
    ("食品饮料", "精品挂耳咖啡", "中深烘焙，独立包装", "69.00", 240),
    ("食品饮料", "每日坚果礼盒", "混合坚果，营养加餐", "119.00", 105),
    ("食品饮料", "低糖燕麦饼干", "饱腹代餐，低糖配方", "39.00", 190),
    ("食品饮料", "原味气泡水整箱", "无糖无脂，清爽解腻", "49.00", 160),
    ("食品饮料", "花草茶组合装", "多口味茶包，冷热皆宜", "55.00", 125),
    ("运动户外", "瑜伽垫加厚防滑", "加厚缓冲，居家训练", "88.00", 115),
    ("运动户外", "可调节哑铃套装", "多档重量，力量训练", "299.00", 42),
    ("运动户外", "户外折叠露营椅", "轻便收纳，露营钓鱼", "139.00", 70),
    ("运动户外", "速干运动毛巾", "吸水快干，健身必备", "35.00", 260),
    ("运动户外", "骑行防风手套", "防滑耐磨，春秋骑行", "59.00", 98),
]

FAQS = [
    ("怎么退货？", "退货,退款,售后", "商品签收后 7 天内可在我的订单中申请退货，特殊商品以页面说明为准。", "refund"),
    ("怎么换货？", "换货,售后", "如商品存在质量问题，可联系客服提交换货申请。", "refund"),
    ("多久发货？", "发货,物流", "正常订单会在 48 小时内发货，促销期间可能略有延迟。", "logistics"),
    ("在哪里查看物流？", "物流,快递,订单", "登录后进入我的订单，点击订单详情即可查看物流状态。", "logistics"),
    ("可以修改收货地址吗？", "地址,收货", "订单发货前可联系客服尝试修改，已发货订单无法修改地址。", "order"),
    ("商品有保修吗？", "保修,质量", "数码类商品按页面说明提供保修服务，普通商品支持售后质检。", "product"),
    ("下单后可以取消吗？", "取消订单,退款", "未发货订单可以在我的订单中取消，已发货订单需走售后流程。", "order"),
    ("优惠活动怎么参加？", "优惠,活动,促销", "活动商品会在首页和商品详情页展示，按页面规则参与。", "product"),
    ("库存不足怎么办？", "库存,缺货", "库存不足的商品暂时无法购买，可等待补货或选择相似商品。", "product"),
    ("支持哪些支付方式？", "支付,付款", "当前实训版本以模拟下单为主，后续可扩展真实支付。", "order"),
    ("商品图片和实物一致吗？", "图片,实物", "商品图片用于展示，颜色和细节可能因设备显示略有差异。", "product"),
    ("如何联系人工客服？", "人工客服,客服", "AI 客服无法处理的问题会提示转人工处理。", "order"),
]


def get_or_create(session, model, defaults: dict | None = None, **filters):
    instance = session.query(model).filter_by(**filters).one_or_none()
    if instance:
        return instance, False
    data = {**filters, **(defaults or {})}
    instance = model(**data)
    session.add(instance)
    session.flush()
    return instance, True


def seed_accounts(session):
    admin, _ = get_or_create(
        session,
        Admin,
        username="admin",
        defaults={
            "password_hash": hash_password("admin123456"),
            "role": "super_admin",
            "status": "normal",
        },
    )

    users = []
    for index in range(1, 6):
        user, _ = get_or_create(
            session,
            User,
            username=f"user{index}",
            defaults={
                "password_hash": hash_password("user123456"),
                "phone": f"1380000000{index}",
                "email": f"user{index}@example.com",
                "nickname": f"演示用户{index}",
                "avatar_url": "",
                "status": "normal",
            },
        )
        users.append(user)
    return admin, users


def seed_categories(session):
    category_map = {}
    for index, name in enumerate(CATEGORIES, start=1):
        category, _ = get_or_create(
            session,
            Category,
            name=name,
            defaults={"parent_id": 0, "sort_order": index, "status": "enabled"},
        )
        category_map[name] = category
    return category_map


def seed_products(session, category_map):
    products = []
    for index, (category_name, name, subtitle, price, stock) in enumerate(PRODUCTS, start=1):
        product, _ = get_or_create(
            session,
            Product,
            name=name,
            defaults={
                "category_id": category_map[category_name].id,
                "subtitle": subtitle,
                "main_image": f"/images/products/product-{index:03d}.jpg",
                "price": Decimal(price),
                "stock": stock,
                "sales_count": random.randint(5, 120),
                "description": f"{name}，{subtitle}。这是用于项目演示的模拟商品数据。",
                "status": "on_sale",
            },
        )
        products.append(product)
    return products


def seed_faqs(session):
    for question, keywords, answer, category in FAQS:
        get_or_create(
            session,
            Faq,
            question=question,
            defaults={
                "keywords": keywords,
                "answer": answer,
                "category": category,
                "status": "enabled",
            },
        )


def seed_orders_and_behaviors(session, users, products):
    if session.query(Order).count() > 0:
        return

    for user_index, user in enumerate(users, start=1):
        selected = products[(user_index - 1) * 3 : (user_index - 1) * 3 + 3]
        total = Decimal("0.00")
        order = Order(
            order_no=f"DEMO20260622{user_index:04d}",
            user_id=user.id,
            total_amount=total,
            status="completed" if user_index % 2 else "paid",
            receiver_name=f"收货人{user_index}",
            receiver_phone=f"1390000000{user_index}",
            receiver_address=f"演示地址 {user_index} 号",
            remark="演示订单",
        )
        session.add(order)
        session.flush()

        for product in selected:
            quantity = random.randint(1, 3)
            subtotal = Decimal(product.price) * quantity
            total += subtotal
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_image=product.main_image,
                    price=product.price,
                    quantity=quantity,
                    subtotal=subtotal,
                )
            )
            session.add(
                UserBehavior(
                    user_id=user.id,
                    session_id=f"demo-session-{user.id}",
                    product_id=product.id,
                    behavior_type="purchase",
                    weight=5,
                )
            )

        order.total_amount = total

    for user in users:
        for product in random.sample(products, 10):
            session.add(
                UserBehavior(
                    user_id=user.id,
                    session_id=f"demo-session-{user.id}",
                    product_id=product.id,
                    behavior_type=random.choice(["view", "view", "cart"]),
                    weight=random.choice([1, 1, 3]),
                )
            )


def seed_ai_and_sales(session, admin, users, products):
    if session.query(SalesStatistic).count() == 0:
        today = date.today()
        for product in products:
            for days_ago in range(30):
                stat_date = today - timedelta(days=days_ago)
                count = random.randint(0, 12)
                session.add(
                    SalesStatistic(
                        product_id=product.id,
                        stat_date=stat_date,
                        sales_count=count,
                        sales_amount=Decimal(product.price) * count,
                    )
                )

    if session.query(ProductSimilarity).count() == 0:
        for index, product in enumerate(products):
            for similar in products[index + 1 : index + 3]:
                session.add(
                    ProductSimilarity(
                        product_id=product.id,
                        similar_product_id=similar.id,
                        score=Decimal("0.7200"),
                        source="manual",
                    )
                )

    if session.query(RecommendResult).count() == 0:
        user = users[0]
        for product in products[:8]:
            session.add(
                RecommendResult(
                    user_id=user.id,
                    product_id=product.id,
                    scene="home",
                    reason="与你最近浏览的商品相似",
                    score=Decimal("0.8000"),
                )
            )

    if session.query(SalesPrediction).count() == 0:
        tomorrow = date.today() + timedelta(days=1)
        for product in products[:8]:
            predicted_count = random.randint(5, 20)
            session.add(
                SalesPrediction(
                    product_id=product.id,
                    predict_date=tomorrow,
                    predicted_count=predicted_count,
                    method="moving_average",
                    basis="根据最近 7 天平均销量生成的演示预测",
                )
            )

    if session.query(InventoryAlert).count() == 0:
        for product in products[:3]:
            session.add(
                InventoryAlert(
                    product_id=product.id,
                    current_stock=product.stock,
                    predicted_sales=product.stock + 10,
                    risk_level="high",
                    suggestion=f"{product.name} 库存存在风险，建议补货至少 30 件。",
                    status="open",
                )
            )

    if session.query(AiConversation).count() == 0:
        conversation = AiConversation(
            user_id=users[0].id,
            admin_id=None,
            agent_type="customer",
            title="演示客服会话",
        )
        session.add(conversation)
        session.flush()
        session.add_all(
            [
                AiMessage(conversation_id=conversation.id, role="user", content="怎么退货？"),
                AiMessage(conversation_id=conversation.id, role="assistant", content="商品签收后 7 天内可申请退货。"),
                AgentToolCall(
                    conversation_id=conversation.id,
                    agent_type="customer",
                    tool_name="query_faq",
                    input_json={"question": "怎么退货？"},
                    output_json={"matched": True},
                    status="success",
                    duration_ms=12,
                ),
            ]
        )

        admin_conversation = AiConversation(
            user_id=None,
            admin_id=admin.id,
            agent_type="operation",
            title="演示运营分析会话",
        )
        session.add(admin_conversation)


def main():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        admin, users = seed_accounts(session)
        category_map = seed_categories(session)
        products = seed_products(session, category_map)
        seed_faqs(session)
        seed_orders_and_behaviors(session, users, products)
        seed_ai_and_sales(session, admin, users, products)
        session.commit()

    print("Database initialized successfully.")


if __name__ == "__main__":
    main()

