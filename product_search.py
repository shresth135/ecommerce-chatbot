import pandas as pd


class ProductSearch:

    def __init__(self, csv_path="data/products.csv"):
        self.df = pd.read_csv(csv_path)

    def search(
        self,
        category=None,
        brand=None,
        max_price=None,
        min_rating=None,
        keyword=None
    ):
        results = self.df.copy()

        # Category filter
        if category:
            results = results[
                results["category"].str.contains(
                    category,
                    case=False,
                    na=False
                )
            ]

        # Brand filter
        if brand:
            results = results[
                results["brand"].str.contains(
                    brand,
                    case=False,
                    na=False
                )
            ]

        # Price filter
        if max_price:
            results = results[
                results["price"] <= max_price
            ]

        # Rating filter
        if min_rating:
            results = results[
                results["rating"] >= min_rating
            ]

        # Keyword search
        if keyword:
            mask = (
                results["name"].str.contains(
                    keyword, case=False, na=False
                )
                |
                results["description"].str.contains(
                    keyword, case=False, na=False
                )
            )

            results = results[mask]

        return results