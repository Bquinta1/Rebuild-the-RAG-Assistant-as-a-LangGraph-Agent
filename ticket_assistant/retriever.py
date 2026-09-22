
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_aws import BedrockEmbeddings
from functools import lru_cache
from . import config
from pathlib import Path


DOCUMENTS_DIR = Path(__file__).resolve().parent.parent / "documents"


def load_document_chunks() -> list[Document]:
    """ read documents/*.md and split each by its "#" and "##" headings """

    splitter = MarkdownHeaderTextSplitter(
        [("#", "title"), ("##", "section")],
        strip_headers=False    
    )

    chunks: list[Document] = []
    for path in sorted(DOCUMENTS_DIR.glob("*.md")):
        for chunk in splitter.split_text(path.read_text(encoding="utf-8")):
            chunk.metadata["source"] = path.name
            chunks.append(chunk)

    return chunks


class ScoreThresholdRetriever(BaseRetriever):
    store: InMemoryVectorStore
    k: int = 4
    threshold: float = 0.25

    model_config = {"arbitrary_types_allowed": True}

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        hits = self.store.similarity_search_with_score(query, k=self.k)
    
        return [doc for doc, score in hits if score >= self.threshold]


@lru_cache(maxsize=1)
def build_local_retriever(k: int = 4, threshold: float = 0.25) -> BaseRetriever:

    chunks = load_document_chunks()

    embeddings = BedrockEmbeddings(
        model_id=config.EMBED_MODEL_ID,
        region_name=config.AWS_REGION
    )

    store = InMemoryVectorStore.from_documents(chunks, embeddings)
    return ScoreThresholdRetriever(store=store, k=k, threshold=threshold)


def get_retriever(k: int = 4) -> BaseRetriever:
    return build_local_retriever(k=k)

