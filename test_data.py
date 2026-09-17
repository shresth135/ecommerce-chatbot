import pandas as pd

df = pd.read_csv("data/products.csv")

# Products under ₹60,000
results = df[df["price"] <= 60000]

print("Products under ₹60,000:\n")

for _, product in results.iterrows():
    print(
        f"{product['name']} - "
        f"₹{product['price']} - "
        f"Rating: {product['rating']}"
    )