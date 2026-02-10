"""Analytics and projections service for BizHub."""
from datetime import datetime, timedelta


class AnalyticsService:
    """Provide analytics, trends, and projections based on sales and inventory."""

    def __init__(self, db_adapter):
        self.db = db_adapter

    def get_date_range(self, period_key: str):
        """Return (start_date, end_date) for a given period key."""
        today = datetime.now().date()
        period_map = {
            "7": 7,
            "30": 30,
            "90": 90,
            "365": 365,
        }
        days = period_map.get(period_key, 7)
        start_date = today - timedelta(days=days - 1)
        return start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), days

    def get_sales_trend(self, start_date: str, end_date: str):
        """Get sales totals grouped by day for charts."""
        return self.db.get_sales_trend_by_day(start_date, end_date)

    def get_sales_summary(self, start_date: str, end_date: str):
        """Get sales summary grouped by item."""
        return self.db.get_sales_summary_by_item(start_date, end_date)

    def get_top_selling_items(self, start_date: str, end_date: str, limit: int = 5):
        """Return top selling items by quantity."""
        rows = self.get_sales_summary(start_date, end_date)
        return rows[:limit]

    def get_reorder_recommendations(self, start_date: str, end_date: str, window_days: int = 7, limit: int = 10):
        """Suggest items to reorder based on recent demand and current stock."""
        sales = self.get_sales_summary(start_date, end_date)
        inventory = self.db.get_all_inventory()
        inventory_map = {row[0]: row[1] for row in inventory}  # item_name -> quantity

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = max(1, (end_dt - start_dt).days + 1)

        recommendations = []
        for item_name, total_qty, total_amount in sales:
            current_qty = inventory_map.get(item_name, 0)
            avg_daily = total_qty / days
            recommended_qty = max(0, int(round(avg_daily * window_days - current_qty)))
            if recommended_qty > 0:
                recommendations.append((item_name, current_qty, avg_daily, recommended_qty))

        recommendations.sort(key=lambda x: x[3], reverse=True)
        return recommendations[:limit]
