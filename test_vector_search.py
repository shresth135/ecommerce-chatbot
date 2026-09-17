from vector_search import VectorSearch


search_engine = VectorSearch()


query = "wireless headphones for music"


results = search_engine.search(
    query,
    top_k=5
)


print("\n🔎 Search:", query)
print("\nRelevant products:\n")


for product in results:

    print(
        f"🛍️ {product['name']}\n"
        f"Brand: {product['brand']}\n"
        f"Price: ₹{product['price']}\n"
        f"Rating: ⭐ {product['rating']}\n"
        f"Description: {product['description']}\n"
        f"Distance: {product['distance']:.4f}\n"
    )