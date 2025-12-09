from django.db.models import Sum, Avg, Count, Max
from main.repositories import *


class AggregationRepository:
    def get_profit_per_store(self, min_total=1000):
        sr = StoreRepository()
        qs = (
            sr.get_all()
            .annotate(total_income=Sum('operationhistory__price'))
            .filter(total_income__gte=min_total)
            .order_by("-total_income")
            .values("id", "name", "total_income")
        )
        return list(qs)

    def get_top_items(self):
        ir = ItemRepository()
        qs = (
            ir.get_all()
            .annotate(total_income=Sum("operationhistory__price"))
            .filter(total_income__isnull=False)
            .order_by("-total_income")
            .values("id", "name", "total_income")
        )
        return list(qs)

    def get_avg_price_for_operation(self):
        orp = OperationRepository()
        qs = (
            orp.get_all()
            .annotate(avg_price=Avg("operationhistory__price"))
            .filter(avg_price__isnull=False)
            .order_by("-avg_price")
            .values("id", "operation", "avg_price")
        )
        return list(qs)

    def get_client_activity(self):
        cr = ClientRepository()
        qs = (
            cr.get_all()
            .annotate(
                operations_count=Count("operationhistory"),
                total_spent=Sum("operationhistory__price")
            )
            .filter(operations_count__gte=1)
            .order_by("-total_spent")
            .values("id", "first_name", "last_name", "operations_count", "total_spent")
        )
        return list(qs)

    def get_estimates_by_store(self):
        sr = StoreRepository()
        qs = (
            sr.get_all()
            .annotate(estimates_count=Count("worker__estimate"))
            .filter(estimates_count__gt=0)
            .order_by("-estimates_count")
            .values("id", "name", "estimates_count")
        )
        return list(qs)

    def get_max_operation_by_city(self):
        oh_repo = OperationHistoryRepository()
        grouped = (
            oh_repo.get_all()
            .values("store__city")
            .annotate(max_price=Max("price"))
        )

        result = []
        for row in grouped:
            city = row["store__city"]
            max_price = row["max_price"]
            op = (
                oh_repo.get_all()
                .filter(store__city=city, price=max_price)
                .select_related("store", "item", "client", "operation")
                .first()
            )
            if op:
                result.append({
                    "city": city,
                    "id": op.id,
                    "price": op.price,
                    "date": op.date,
                    "info": op.info,
                    "client_id": op.client_id,
                    "item_id": op.item_id,
                    "operation_id": op.operation_id,
                    "store_id": op.store_id,
                })
        return result