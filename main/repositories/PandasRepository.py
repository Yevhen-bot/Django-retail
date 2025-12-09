import pandas as pd
from main.repositories import *


class PandasRepository:
    def pandas_get_profit_per_store(self, min_total=1000):
        sr = StoreRepository()
        stores = sr.get_all().values("id", "name")
        oh_repo = OperationHistoryRepository()
        operations = oh_repo.get_all().values("store_id", "price")
        
        stores_df = pd.DataFrame(stores)
        ops_df = pd.DataFrame(operations)
        
        income_df = ops_df.groupby("store_id")["price"].sum().reset_index()
        income_df.columns = ["id", "total_income"]
        
        result = stores_df.merge(income_df, on="id", how="left")
        result["total_income"] = result["total_income"].fillna(0)
        result = result[result["total_income"] >= min_total].sort_values("total_income", ascending=False)
        
        return result if not result.empty else None

    def pandas_get_top_items(self):
        ir = ItemRepository()
        items = ir.get_all().values("id", "name")
        oh_repo = OperationHistoryRepository()
        operations = oh_repo.get_all().values("item_id", "price")
        
        items_df = pd.DataFrame(items)
        ops_df = pd.DataFrame(operations)
        
        income_df = ops_df.groupby("item_id")["price"].sum().reset_index()
        income_df.columns = ["id", "total_income"]
        
        result = items_df.merge(income_df, on="id", how="left")
        result = result[result["total_income"].notna()].sort_values("total_income", ascending=False)
        
        return result if not result.empty else None

    def pandas_get_avg_price_for_operation(self):
        orp = OperationRepository()
        operations = orp.get_all().values("id", "operation")
        oh_repo = OperationHistoryRepository()
        op_history = oh_repo.get_all().values("operation_id", "price")
        
        ops_df = pd.DataFrame(operations)
        oh_df = pd.DataFrame(op_history)
        
        avg_df = oh_df.groupby("operation_id")["price"].mean().reset_index()
        avg_df.columns = ["id", "avg_price"]
        
        result = ops_df.merge(avg_df, on="id", how="left")
        result = result[result["avg_price"].notna()].sort_values("avg_price", ascending=False)
        
        return result if not result.empty else None

    def pandas_get_client_activity(self):
        cr = ClientRepository()
        clients = cr.get_all().values("id", "first_name", "last_name")
        oh_repo = OperationHistoryRepository()
        operations = oh_repo.get_all().values("client_id", "price")
        
        clients_df = pd.DataFrame(clients)
        ops_df = pd.DataFrame(operations)
        
        activity_df = ops_df.groupby("client_id").agg(
            operations_count=("client_id", "count"),
            total_spent=("price", "sum")
        ).reset_index()
        activity_df.columns = ["id", "operations_count", "total_spent"]
        
        result = clients_df.merge(activity_df, on="id", how="left")
        result = result[result["operations_count"] >= 1].sort_values("total_spent", ascending=False)
        
        return result if not result.empty else None

    def pandas_get_estimates_by_store(self):
        sr = StoreRepository()
        stores = sr.get_all().values("id", "name")
        wr = WorkerRepository()
        workers = wr.get_all().values("store_id", "id")
        er = EstimateRepository()
        estimates = er.get_all().values("worker_id")
        
        stores_df = pd.DataFrame(stores)
        workers_df = pd.DataFrame(workers)
        estimates_df = pd.DataFrame(estimates)
        
        worker_estimates = workers_df.merge(estimates_df, left_on="id", right_on="worker_id", how="left")
        store_estimates = worker_estimates.groupby("store_id").size().reset_index(name="estimates_count")
        store_estimates.columns = ["id", "estimates_count"]
        
        result = stores_df.merge(store_estimates, on="id", how="left")
        result["estimates_count"] = result["estimates_count"].fillna(0)
        result = result[result["estimates_count"] > 0].sort_values("estimates_count", ascending=False)
        
        return result if not result.empty else None

    def pandas_get_max_operation_by_city(self):
        oh_repo = OperationHistoryRepository()
        operations = oh_repo.get_all().select_related("store").values(
            "id", "price", "date", "info", "client_id", "item_id", "operation_id", "store_id", "store__city"
        )
        
        ops_df = pd.DataFrame(operations)
        ops_df.columns = ["id", "price", "date", "info", "client_id", "item_id", "operation_id", "store_id", "city"]
        
        result = ops_df.loc[ops_df.groupby("city")["price"].idxmax()]
        result = result.reset_index(drop=True)
        
        return result if not result.empty else None