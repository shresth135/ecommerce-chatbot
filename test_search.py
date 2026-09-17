from product_search import ProductSearch


search_engine = ProductSearch()


results = search_engine.search(
    min_rating=4.6
)


print("\n🔎 Laptops under ₹60,000:\n")


for _, product in results.iterrows():

    print(
        f"🛍️ {product['name']}\n"
        f"Brand: {product['brand']}\n"
        f"Price: ₹{product['price']}\n"
        f"Rating: ⭐ {product['rating']}\n"
        f"{product['description']}\n"
    )