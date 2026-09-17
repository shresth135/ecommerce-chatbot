import os
import re

from dotenv import load_dotenv
from google import genai

from vector_search import VectorSearch
from faq_search import FAQSearch


load_dotenv()


class EcommerceRAG:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.search_engine = VectorSearch()

        self.faq_search = FAQSearch()

        self.df = self.search_engine.df

    # ======================================================
    # BUDGET EXTRACTION
    # ======================================================

    def extract_budget(self, query):

        query = query.lower()

        patterns = [
            r"under\s*[₹rs.]*\s*(\d+(?:,\d+)*)",
            r"below\s*[₹rs.]*\s*(\d+(?:,\d+)*)",
            r"less than\s*[₹rs.]*\s*(\d+(?:,\d+)*)",
            r"budget\s*(?:of|is)?\s*[₹rs.]*\s*(\d+(?:,\d+)*)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                query
            )

            if match:

                return float(
                    match.group(1).replace(
                        ",",
                        ""
                    )
                )

        return None

    # ======================================================
    # PRODUCT RANKING
    # ======================================================

    def rank_products(
        self,
        products,
        budget=None
    ):

        ranked = []

        for product in products:

            score = 0

            distance = float(
                product["distance"]
            )

            score += 1 / (
                1 + distance
            )

            score += (
                float(product["rating"])
                * 0.2
            )

            if int(product["stock"]) > 0:

                score += 0.2

            if budget:

                price = float(
                    product["price"]
                )

                if price <= budget:

                    score += 1.0

                    score += (
                        price / budget
                    ) * 0.5

                else:

                    score -= 1.0

            ranked.append(
                (score, product)
            )

        ranked.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            product
            for score, product
            in ranked
        ]

    # ======================================================
    # PRODUCT RETRIEVAL
    # ======================================================

    def retrieve_products(
        self,
        query,
        top_k=8
    ):

        products = self.search_engine.search(
            query,
            top_k=top_k
        )

        budget = self.extract_budget(
            query
        )

        products = self.rank_products(
            products,
            budget
        )

        return products[:5]

    # ======================================================
    # PRODUCT CONTEXT
    # ======================================================

    def build_product_context(
        self,
        products
    ):

        context = ""

        for product in products:

            context += f"""
Product ID: {product['product_id']}
Name: {product['name']}
Category: {product['category']}
Brand: {product['brand']}
Price: ₹{product['price']}
Rating: {product['rating']}
Stock: {product['stock']}
Description: {product['description']}
"""

        return context

    # ======================================================
    # FAQ CONTEXT
    # ======================================================

    def build_faq_context(
        self,
        faqs
    ):

        context = ""

        for faq in faqs:

            context += f"""
FAQ Category: {faq['category']}
Question: {faq['question']}
Answer: {faq['answer']}
"""

        return context

    # ======================================================
    # FIND PRODUCTS FOR COMPARISON
    # ======================================================

    def find_products_for_comparison(
        self,
        query
    ):

        query_lower = query.lower()

        matches = []

        for _, product in self.df.iterrows():

            product_name = (
                product["name"]
                .lower()
            )

            if product_name in query_lower:

                matches.append(product)

        return matches

    # ======================================================
    # PRODUCT COMPARISON
    # ======================================================

    def compare_products(
        self,
        query,
        history=""
    ):

        products = (
            self.find_products_for_comparison(
                query
            )
        )

        if len(products) < 2:

            products = self.search_engine.search(
                query,
                top_k=5
            )

        products = products[:4]

        context = self.build_product_context(
            products
        )

        prompt = f"""
You are an e-commerce product comparison assistant.

Conversation history:
{history}

Current customer request:
{query}

Product information:
{context}

Compare only the products provided.

Include:
- Product name
- Brand
- Price
- Rating
- Stock
- Available specifications

Rules:
- Never invent information.
- Never invent specifications.
- Never invent prices.
- Use only the supplied product data.
- Clearly state when information is unavailable.

Give a concise comparison.
"""

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text, products

    # ======================================================
    # FAQ RESPONSE
    # ======================================================

    def answer_faq(
        self,
        query,
        history=""
    ):

        faqs = self.faq_search.search(
            query,
            top_k=3
        )

        context = self.build_faq_context(
            faqs
        )

        prompt = f"""
You are an e-commerce customer support assistant.

Conversation history:
{history}

Customer question:
{query}

Store FAQ information:
{context}

Answer the customer's question using
the FAQ information.

Rules:
- Do not invent store policies.
- Do not invent delivery times.
- Do not invent refund periods.
- Do not invent warranty terms.
- If the FAQ does not contain enough
  information, say that the information
  is not available.

Give a concise and helpful answer.
"""

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text, faqs

    # ======================================================
    # NORMAL PRODUCT RAG
    # ======================================================

    def ask(
        self,
        query,
        history=""
    ):

        products = self.retrieve_products(
            query,
            top_k=8
        )

        context = self.build_product_context(
            products
        )

        prompt = f"""
You are an AI shopping assistant.

Conversation history:
{history}

Current customer request:
{query}

Available products:
{context}

Answer using only the product information.

Rules:
1. Never invent products.
2. Never invent prices.
3. Never invent specifications.
4. Respect the customer's budget.
5. Prefer highly rated products.
6. Consider the conversation history.
7. If information is unavailable, say so.
8. Keep the answer concise.

Answer the customer.
"""

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text, products

    # ======================================================
    # INTENT DETECTION
    # ======================================================

    def detect_intent(
        self,
        query
    ):

        text = query.lower()

        comparison_words = [
            "compare",
            "comparison",
            "difference",
            "vs",
            "versus"
        ]

        faq_words = [
            "shipping",
            "delivery",
            "return",
            "refund",
            "payment",
            "warranty",
            "cancel",
            "order",
            "support",
            "track my order"
        ]

        if any(
            word in text
            for word in comparison_words
        ):

            return "comparison"

        if any(
            word in text
            for word in faq_words
        ):

            return "faq"

        return "product"

    # ======================================================
    # MAIN CHAT FUNCTION
    # ======================================================

    def chat(
        self,
        query,
        history=""
    ):

        intent = self.detect_intent(
            query
        )

        if intent == "comparison":

            return self.compare_products(
                query,
                history
            )

        if intent == "faq":

            return self.answer_faq(
                query,
                history
            )

        return self.ask(
            query,
            history
        )