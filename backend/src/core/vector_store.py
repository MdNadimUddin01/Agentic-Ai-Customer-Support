"""Vector store operations for semantic search."""
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from pymongo.collection import Collection
from config import settings, logger
from src.core.database import get_collection
from src.core.exceptions import VectorStoreException
from src.core.constants import COLLECTION_KNOWLEDGE_BASE, VECTOR_SEARCH_TOP_K


class VectorStore:
    """Handles vector embeddings and semantic search."""

    def __init__(self):
        """Initialize vector store with embedding model."""
        self._model: Optional[SentenceTransformer] = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Load the embedding model."""
        try:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(settings.embedding_model)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise VectorStoreException(f"Model initialization failed: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.

        Args:
            text: Input text

        Returns:
            List of floats representing the embedding
        """
        try:
            if not self._model:
                raise VectorStoreException("Embedding model not initialized")

            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise VectorStoreException(f"Embedding generation failed: {e}")

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embeddings
        """
        try:
            if not self._model:
                raise VectorStoreException("Embedding model not initialized")

            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise VectorStoreException(f"Batch embedding generation failed: {e}")

    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        collection_name: str = COLLECTION_KNOWLEDGE_BASE
    ) -> str:
        """
        Add a document to the vector store.

        Args:
            content: Document content
            metadata: Document metadata
            collection_name: Collection to store in

        Returns:
            Document ID
        """
        try:
            # Generate embedding
            embedding = self.generate_embedding(content)

            # Prepare document
            document = {
                "content": content,
                "embedding": embedding,
                "metadata": metadata
            }

            # Insert into database
            collection = get_collection(collection_name)
            result = collection.insert_one(document)

            logger.info(f"Document added to {collection_name}: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise VectorStoreException(f"Document addition failed: {e}")

    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]],
        collection_name: str = COLLECTION_KNOWLEDGE_BASE
    ) -> List[str]:
        """
        Add multiple documents to the vector store.

        Args:
            documents: List of documents with 'content' and 'metadata'
            collection_name: Collection to store in

        Returns:
            List of document IDs
        """
        try:
            # Extract contents and generate embeddings
            contents = [doc["content"] for doc in documents]
            embeddings = self.generate_embeddings_batch(contents)

            # Prepare documents with embeddings
            docs_to_insert = []
            for doc, embedding in zip(documents, embeddings):
                docs_to_insert.append({
                    "content": doc["content"],
                    "embedding": embedding,
                    "metadata": doc.get("metadata", {})
                })

            # Insert into database
            collection = get_collection(collection_name)
            result = collection.insert_many(docs_to_insert)

            logger.info(f"Added {len(result.inserted_ids)} documents to {collection_name}")
            return [str(id_) for id_ in result.inserted_ids]

        except Exception as e:
            logger.error(f"Error adding documents batch: {e}")
            raise VectorStoreException(f"Batch document addition failed: {e}")

    def similarity_search(
        self,
        query: str,
        top_k: int = VECTOR_SEARCH_TOP_K,
        filter_criteria: Optional[Dict[str, Any]] = None,
        collection_name: str = COLLECTION_KNOWLEDGE_BASE
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_criteria: MongoDB filter criteria
            collection_name: Collection to search in

        Returns:
            List of matching documents with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            query_vector = np.array(query_embedding)

            # Get collection
            collection = get_collection(collection_name)

            # Build filter
            match_filter = filter_criteria if filter_criteria else {}

            # Fetch documents (in production, use MongoDB Atlas Vector Search)
            documents = list(collection.find(match_filter))

            if not documents:
                logger.warning(f"No documents found in {collection_name}")
                return []

            # Calculate cosine similarity
            results = []
            for doc in documents:
                if "embedding" not in doc:
                    continue

                doc_vector = np.array(doc["embedding"])
                similarity = self._cosine_similarity(query_vector, doc_vector)

                results.append({
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "score": float(similarity),
                    "id": str(doc["_id"])
                })

            # Sort by similarity and return top k
            results.sort(key=lambda x: x["score"], reverse=True)
            top_results = results[:top_k]

            logger.info(f"Found {len(top_results)} similar documents for query: {query[:50]}...")
            return top_results

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise VectorStoreException(f"Similarity search failed: {e}")

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def delete_documents(
        self,
        filter_criteria: Dict[str, Any],
        collection_name: str = COLLECTION_KNOWLEDGE_BASE
    ) -> int:
        """
        Delete documents matching criteria.

        Args:
            filter_criteria: MongoDB filter criteria
            collection_name: Collection to delete from

        Returns:
            Number of documents deleted
        """
        try:
            collection = get_collection(collection_name)
            result = collection.delete_many(filter_criteria)

            logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")
            return result.deleted_count

        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise VectorStoreException(f"Document deletion failed: {e}")


# Global vector store instance
vector_store = VectorStore()


# Convenience functions
def search_knowledge_base(query: str, top_k: int = VECTOR_SEARCH_TOP_K, industry: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search knowledge base for relevant documents.

    Args:
        query: Search query
        top_k: Number of results
        industry: Filter by industry

    Returns:
        List of relevant documents
    """
    filter_criteria = {}
    if industry:
        filter_criteria["metadata.industry"] = industry

    return vector_store.similarity_search(query, top_k=top_k, filter_criteria=filter_criteria)


def add_knowledge_entry(content: str, category: str, industry: str = "saas") -> str:
    """
    Add entry to knowledge base.

    Args:
        content: Content text
        category: Category (e.g., 'authentication', 'billing')
        industry: Industry type

    Returns:
        Document ID
    """
    metadata = {
        "category": category,
        "industry": industry,
        "source": "manual"
    }
    return vector_store.add_document(content, metadata)
