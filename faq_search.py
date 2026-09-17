import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer


class FAQSearch:

    def __init__(self, csv_path="data/faqs.csv"):

        self.df = pd.read_csv(csv_path)

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.documents = (
            self.df["question"].fillna("")
            + " "
            + self.df["answer"].fillna("")
            + " "
            + self.df["category"].fillna("")
        ).tolist()

        embeddings = self.model.encode(
            self.documents,
            convert_to_numpy=True
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.index.add(
            embeddings.astype("float32")
        )

    def search(self, query, top_k=3):

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        distances, indices = self.index.search(
            query_embedding.astype("float32"),
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            faq = self.df.iloc[index].copy()

            faq["distance"] = float(distance)

            results.append(faq)

        return results