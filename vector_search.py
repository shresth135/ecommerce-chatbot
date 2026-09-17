import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer


class VectorSearch:

    def __init__(self, csv_path="data/products.csv"):
        self.df = pd.read_csv(csv_path)

        # Load embedding model
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # Create searchable text
        self.documents = (
            self.df["name"].fillna("")
            + " "
            + self.df["category"].fillna("")
            + " "
            + self.df["brand"].fillna("")
            + " "
            + self.df["description"].fillna("")
        ).tolist()

        # Convert products into vectors
        embeddings = self.model.encode(
            self.documents,
            convert_to_numpy=True
        )

        # Create FAISS index
        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings.astype("float32"))

    def search(self, query, top_k=5):

        # Convert user query into vector
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        # Search similar products
        distances, indices = self.index.search(
            query_embedding.astype("float32"),
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            product = self.df.iloc[index].copy()

            product["distance"] = float(distance)

            results.append(product)

        return results