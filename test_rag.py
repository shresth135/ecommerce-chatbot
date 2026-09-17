from rag import EcommerceRAG


rag = EcommerceRAG()


questions = [
    "I need a laptop for programming under 60000",
    "Which smartphone is good?",
    "Show me wireless headphones",
]


for question in questions:

    print("\n" + "=" * 60)

    print("USER:")
    print(question)

    answer, products = rag.ask(question)

    print("\nBOT:")
    print(answer)

    print("\nRETRIEVED PRODUCTS:")

    for product in products:
        print(
            f"- {product['name']} "
            f"(₹{product['price']})"
        )