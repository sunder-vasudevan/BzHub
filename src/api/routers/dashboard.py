"""Dashboard router — KPIs and trend data."""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.deps import get_inventory_service, get_pos_service, get_crm_service
from src.services import InventoryService, POSService
from src.services.crm_service import CRMService

router = APIRouter()


@router.get("/kpis")
def get_kpis(
    inv_svc: InventoryService = Depends(get_inventory_service),
    pos_svc: POSService = Depends(get_pos_service),
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Return key performance indicators for the dashboard."""
    all_items = inv_svc.get_all_items()
    inventory_value = sum(
        (row[2] or 0) * (row[4] or 0)  # quantity * cost_price
        for row in all_items
    )
    low_stock = [r for r in all_items if (r[2] or 0) <= (r[3] or 0) and (r[3] or 0) > 0]

    today = datetime.now().strftime("%Y-%m-%d")
    today_sales = pos_svc.db.get_sales_by_date(today)
    today_total = sum(row[5] for row in today_sales) if today_sales else 0.0

    all_sales = pos_svc.get_all_sales()
    all_total = sum(row[5] for row in all_sales) if all_sales else 0.0

    # Simple growth: compare last 7 days vs prior 7 days
    now = datetime.now()
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    two_weeks_ago = (now - timedelta(days=14)).strftime("%Y-%m-%d")
    week_sales = pos_svc.db.get_sales_between(week_ago, now.strftime("%Y-%m-%d"))
    prior_week_sales = pos_svc.db.get_sales_between(two_weeks_ago, week_ago)
    week_total = sum(r[5] for r in week_sales) if week_sales else 0.0
    prior_total = sum(r[5] for r in prior_week_sales) if prior_week_sales else 0.0
    growth_pct = 0.0
    if prior_total > 0:
        growth_pct = round(((week_total - prior_total) / prior_total) * 100, 1)

    days_count = max(len({str(r[1])[:10] for r in all_sales}), 1)
    avg_daily = round(all_total / days_count, 2)

    pipeline_value = crm_svc.get_pipeline_value()
    conversion = crm_svc.get_conversion_rate()

    return {
        "today_sales": round(today_total, 2),
        "inventory_value": round(inventory_value, 2),
        "low_stock_count": len(low_stock),
        "total_items": len(all_items),
        "avg_daily_sales": avg_daily,
        "growth_pct": growth_pct,
        "pipeline_value": round(pipeline_value, 2),
        "conversion_rate": conversion,
    }


@router.get("/trend")
def get_trend(
    days: Optional[int] = 30,
    pos_svc: POSService = Depends(get_pos_service),
):
    """Return daily sales trend for the last N days."""
    now = datetime.now()
    start = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    trend = pos_svc.db.get_sales_trend_by_day(start, end)
    return [
        {"date": row[0], "total": round(row[1], 2)}
        for row in trend
    ]
