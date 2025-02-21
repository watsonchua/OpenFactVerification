from .google_retriever import GoogleEvidenceRetriever
from .serper_retriever import SerperEvidenceRetriever
from .wikipedia_retriever import WikipediaEvidenceRetriever


retriever_map = {
    "google": GoogleEvidenceRetriever,
    "serper": SerperEvidenceRetriever,
    "wikipedia": WikipediaEvidenceRetriever
}


def retriever_mapper(retriever_name: str):
    if retriever_name not in retriever_map:
        raise NotImplementedError(f"Retriever {retriever_name} not found!")
    return retriever_map[retriever_name]
