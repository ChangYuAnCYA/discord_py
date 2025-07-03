from FinMind.data import DataLoader

class TaiwanStock():
    def __init__(self):
        self.api = DataLoader()
        self.api.login_by_token(api_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyMy0xMC0yNSAxNDo0Mzo1MSIsInVzZXJfaWQiOiJzYXRvdXl1dWJhIiwiaXAiOiIxNDAuMTE1LjU0LjEwNiJ9.7GI_HOQ3iTQFkiGELia-vt9JUqYOr4Kxws6_ybABxBk")
        info = self.api.taiwan_stock_info()
        self.stock_info = {i:j for i, j in zip(info.stock_id, info.stock_name)}

    def get_stock(self, stock_id, start_date, end_date):
        df = self.api.taiwan_stock_daily(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date) #'2023-10-25'
        
        return df