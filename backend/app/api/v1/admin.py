from datetime import date

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models import Admin
from app.schemas.admin import AdminLogin, AdminLoginResult, AdminPublic, AdminUserPublic, DashboardStats
from app.schemas.ai import AgentToolCallPublic
from app.schemas.analytics import (
    InventoryAlertPublic,
    SalesPredictRequest,
    SalesPredictionPublic,
    SalesStatisticPublic,
)
from app.schemas.common import ApiResponse, PageResponse
from app.schemas.order import OrderItemPublic, OrderSummary
from app.schemas.product import (
    CategoryCreate,
    CategoryPublic,
    CategoryUpdate,
    ProductCreate,
    ProductDetail,
    ProductUpdate,
    StatusUpdate,
)
from app.schemas.upload import UploadResult
from app.services import admin_auth_service, admin_service, ai_service
from app.services.upload_service import save_product_image
from app.repositories import order_repository

router = APIRouter(prefix="/admin")


@router.post("/auth/login", response_model=ApiResponse[AdminLoginResult])
def login_admin(payload: AdminLogin, db: Session = Depends(get_db)) -> ApiResponse[AdminLoginResult]:
    token, admin = admin_auth_service.login_admin(db, username=payload.username, password=payload.password)
    return ApiResponse(data=AdminLoginResult(access_token=token, admin=AdminPublic.model_validate(admin)))


@router.post("/uploads/product-image", response_model=ApiResponse[UploadResult])
async def upload_product_image(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin),
) -> ApiResponse[UploadResult]:
    return ApiResponse(data=await save_product_image(file))


@router.get("/dashboard", response_model=ApiResponse[DashboardStats])
def dashboard(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[DashboardStats]:
    return ApiResponse(data=admin_service.dashboard(db))


@router.get("/products", response_model=ApiResponse[PageResponse[ProductDetail]])
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    status: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[ProductDetail]]:
    items, total = admin_service.list_admin_products(db, page, page_size, keyword, status)
    return ApiResponse(
        data=PageResponse(
            items=[ProductDetail.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/products", response_model=ApiResponse[ProductDetail])
def create_product(
    payload: ProductCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[ProductDetail]:
    return ApiResponse(data=ProductDetail.model_validate(admin_service.create_product(db, payload)))


@router.put("/products/{product_id}", response_model=ApiResponse[ProductDetail])
def update_product(
    product_id: int,
    payload: ProductUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[ProductDetail]:
    return ApiResponse(data=ProductDetail.model_validate(admin_service.update_product(db, product_id, payload)))


@router.put("/products/{product_id}/status", response_model=ApiResponse[ProductDetail])
def update_product_status(
    product_id: int,
    payload: StatusUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[ProductDetail]:
    return ApiResponse(
        data=ProductDetail.model_validate(admin_service.update_product_status(db, product_id, payload.status))
    )


@router.delete("/products/{product_id}", response_model=ApiResponse[ProductDetail])
def delete_product(
    product_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[ProductDetail]:
    return ApiResponse(data=ProductDetail.model_validate(admin_service.update_product_status(db, product_id, "off_sale")))


@router.get("/categories", response_model=ApiResponse[list[CategoryPublic]])
def list_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[list[CategoryPublic]]:
    return ApiResponse(data=[CategoryPublic.model_validate(item) for item in admin_service.list_categories(db)])


@router.post("/categories", response_model=ApiResponse[CategoryPublic])
def create_category(
    payload: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[CategoryPublic]:
    return ApiResponse(data=CategoryPublic.model_validate(admin_service.create_category(db, payload)))


@router.put("/categories/{category_id}", response_model=ApiResponse[CategoryPublic])
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[CategoryPublic]:
    return ApiResponse(data=CategoryPublic.model_validate(admin_service.update_category(db, category_id, payload)))


@router.put("/categories/{category_id}/status", response_model=ApiResponse[CategoryPublic])
def update_category_status(
    category_id: int,
    payload: StatusUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[CategoryPublic]:
    return ApiResponse(
        data=CategoryPublic.model_validate(admin_service.update_category_status(db, category_id, payload.status))
    )


def _order_summary(db: Session, order) -> OrderSummary:
    items = order_repository.list_order_items(db, order_id=order.id)
    return OrderSummary(
        id=order.id,
        order_no=order.order_no,
        total_amount=order.total_amount,
        status=order.status,
        receiver_name=order.receiver_name,
        receiver_phone=order.receiver_phone,
        receiver_address=order.receiver_address,
        remark=order.remark,
        created_at=order.created_at,
        items=[OrderItemPublic.model_validate(item) for item in items],
    )


@router.get("/orders", response_model=ApiResponse[PageResponse[OrderSummary]])
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[OrderSummary]]:
    items, total = admin_service.list_admin_orders(db, page, page_size, status)
    return ApiResponse(
        data=PageResponse(
            items=[_order_summary(db, item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/orders/{order_id}", response_model=ApiResponse[OrderSummary])
def get_order(
    order_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[OrderSummary]:
    return ApiResponse(data=_order_summary(db, admin_service.get_admin_order(db, order_id)))


@router.put("/orders/{order_id}/status", response_model=ApiResponse[OrderSummary])
def update_order_status(
    order_id: int,
    payload: StatusUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[OrderSummary]:
    return ApiResponse(data=_order_summary(db, admin_service.update_order_status(db, order_id, payload.status)))


@router.get("/users", response_model=ApiResponse[PageResponse[AdminUserPublic]])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    status: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[AdminUserPublic]]:
    items, total = admin_service.list_users(db, page, page_size, keyword, status)
    return ApiResponse(
        data=PageResponse(
            items=[AdminUserPublic.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.put("/users/{user_id}/status", response_model=ApiResponse[AdminUserPublic])
def update_user_status(
    user_id: int,
    payload: StatusUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminUserPublic]:
    return ApiResponse(data=AdminUserPublic.model_validate(admin_service.update_user_status(db, user_id, payload.status)))


@router.get("/inventory/alerts", response_model=ApiResponse[PageResponse[InventoryAlertPublic]])
def list_inventory_alerts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[InventoryAlertPublic]]:
    items, total = admin_service.list_inventory_alerts(db, page, page_size, status)
    return ApiResponse(
        data=PageResponse(
            items=[InventoryAlertPublic.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.put("/inventory/alerts/{alert_id}/status", response_model=ApiResponse[InventoryAlertPublic])
def update_inventory_alert_status(
    alert_id: int,
    payload: StatusUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[InventoryAlertPublic]:
    return ApiResponse(
        data=InventoryAlertPublic.model_validate(admin_service.update_inventory_alert_status(db, alert_id, payload.status))
    )


@router.get("/sales/statistics", response_model=ApiResponse[list[SalesStatisticPublic]])
def list_sales_statistics(
    product_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[list[SalesStatisticPublic]]:
    return ApiResponse(
        data=[
            SalesStatisticPublic.model_validate(item)
            for item in admin_service.list_sales_statistics(db, product_id, start_date, end_date)
        ]
    )


@router.post("/sales/predict", response_model=ApiResponse[SalesPredictionPublic])
def predict_sales(
    payload: SalesPredictRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[SalesPredictionPublic]:
    return ApiResponse(data=SalesPredictionPublic.model_validate(admin_service.predict_sales(db, payload.product_id, payload.days)))


@router.get("/ai/tool-calls", response_model=ApiResponse[PageResponse[AgentToolCallPublic]])
def list_agent_tool_calls(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[AgentToolCallPublic]]:
    items, total = ai_service.list_tool_calls(db, page=page, page_size=page_size)
    return ApiResponse(
        data=PageResponse(
            items=[AgentToolCallPublic.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )
