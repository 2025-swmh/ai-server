"""
Vector Database Service using ChromaDB
Clean Architecture - Frameworks & Drivers Layer
"""
import os
import logging
import math
from typing import List, Dict, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tiktoken

from src.core.config.settings import settings

logger = logging.getLogger(__name__)


class VectorDBService:
    """
    Vector database service using ChromaDB for RAG functionality
    Handles document embedding, storage, and semantic search
    """

    def __init__(self):
        """Initialize ChromaDB client and embedding model"""
        self.data_path = Path(__file__).parent.parent.parent.parent / "data" / "chromadb"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.data_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self.use_openai_embeddings = settings.USE_OPENAI_EMBEDDINGS
        
        if not self.use_openai_embeddings:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Initialized SentenceTransformer model: {self.embedding_model_name}")
        else:
            self.embedding_model = None
            logger.info(f"Configured to use OpenAI embeddings: {self.embedding_model_name}")
        
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
            
        logger.info(f"Vector DB initialized with data path: {self.data_path}")

    def _get_embedding_function(self):
        """Get the appropriate embedding function based on configuration"""
        if self.use_openai_embeddings:
            return chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name=self.embedding_model_name
            )
        else:
            return chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model_name
            )

    def get_or_create_collection(self, collection_name: str):
        """Get or create a ChromaDB collection"""
        embedding_function = self._get_embedding_function()
        
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
            logger.info(f"Retrieved existing collection: {collection_name}")
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            return len(text) // 4

    def chunk_text_by_tokens(
        self, 
        text: str, 
        max_tokens: int = 300,
        overlap_tokens: int = 75
    ) -> List[str]:
        """
        Chunk text by token count with overlap
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Token overlap between chunks
            
        Returns:
            List of text chunks
        """
        if self.tokenizer is None:
            max_chars = max_tokens * 4
            overlap_chars = overlap_tokens * 4
            return self._chunk_text_by_chars(text, max_chars, overlap_chars)

        paragraphs = text.split('\n\n')
        sentences = []
        for para in paragraphs:
            if para.strip():
                lines = para.split('\n')
                sentences.extend([line.strip() for line in lines if line.strip()])
        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_tokens = len(self.tokenizer.encode(sentence))
            
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                chunks.append(chunk_text)
                
                overlap_sentences = []
                overlap_tokens_count = 0
                
                for i in range(len(current_chunk) - 1, -1, -1):
                    sent_tokens = len(self.tokenizer.encode(current_chunk[i]))
                    if overlap_tokens_count + sent_tokens <= overlap_tokens:
                        overlap_sentences.insert(0, current_chunk[i])
                        overlap_tokens_count += sent_tokens
                    else:
                        break
                
                current_chunk = overlap_sentences + [sentence]
                current_tokens = overlap_tokens_count + sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append(chunk_text)

        logger.info(f"Created {len(chunks)} chunks from text ({len(text)} chars)")
        return chunks

    def _chunk_text_by_chars(self, text: str, max_chars: int, overlap_chars: int) -> List[str]:
        """Fallback character-based chunking"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chars
            
            if end < len(text):
                for boundary in ['. ', '.\n', '? ', '! ']:
                    boundary_pos = text.rfind(boundary, start, end)
                    if boundary_pos > start:
                        end = boundary_pos + len(boundary)
                        break
                else:
                    space_pos = text.rfind(' ', start, end)
                    if space_pos > start:
                        end = space_pos
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap_chars if end < len(text) else end
            
        return chunks

    def store_knowledge_base(
        self, 
        knowledge_base_id: str, 
        content: str, 
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Store knowledge base content in vector database
        
        Args:
            knowledge_base_id: Unique identifier for knowledge base
            content: Knowledge base content to store
            metadata: Additional metadata for the knowledge base
        """
        collection_name = f"knowledge_{knowledge_base_id}"
        collection = self.get_or_create_collection(collection_name)
        
        try:
            collection.delete()
            collection = self.get_or_create_collection(collection_name)
        except Exception as e:
            logger.warning(f"Could not clear collection {collection_name}: {e}")
        
        chunks = self.chunk_text_by_tokens(content, max_tokens=300, overlap_tokens=75)
        
        if not chunks:
            logger.warning(f"No chunks created for knowledge base {knowledge_base_id}")
            return
        
        documents = []
        metadatas = []
        ids = []
        
        base_metadata = metadata or {}
        base_metadata.update({
            "knowledge_base_id": knowledge_base_id,
            "total_chunks": len(chunks)
        })
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                "chunk_id": i,
                "chunk_text_length": len(chunk),
                "chunk_tokens": self.count_tokens(chunk)
            })
            
            documents.append(chunk)
            metadatas.append(chunk_metadata)
            ids.append(f"{knowledge_base_id}_chunk_{i}")
        
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Stored {len(chunks)} chunks for knowledge base {knowledge_base_id}")
        except Exception as e:
            logger.error(f"Error storing knowledge base {knowledge_base_id}: {e}")
            raise

    def _preprocess_query(self, query: str) -> str:
        """Preprocess and expand query for better semantic matching"""
        query = query.strip()
        
        expansions = {
            'RESTful API': 'RESTful API REST 웹 서비스 HTTP 엔드포인트',
            'API 설계': 'API 설계 디자인 아키텍처 구조 원칙',
            '데이터베이스': '데이터베이스 DB 쿼리 최적화 성능',
            '마이크로서비스': '마이크로서비스 MSA 아키텍처 분산 시스템',
            '성능': '성능 최적화 튜닝 개선 속도',
        }
        
        for key, expansion in expansions.items():
            if key in query:
                query += ' ' + expansion
                
        return query

    def search_similar_chunks(
        self, 
        knowledge_base_id: str, 
        query: str, 
        top_k: int = 5,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar chunks in knowledge base
        
        Args:
            knowledge_base_id: Knowledge base to search in
            query: Search query
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar chunks with metadata
        """
        collection_name = f"knowledge_{knowledge_base_id}"
        
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self._get_embedding_function()
            )
        except Exception as e:
            logger.error(f"Collection {collection_name} not found: {e}")
            return []
        
        enhanced_query = self._preprocess_query(query)
        
        try:
            results = collection.query(
                query_texts=[enhanced_query],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            chunks = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                raw_similarity = 1 - distance
                enhanced_similarity = 1 / (1 + math.exp(-10 * (raw_similarity - 0.5)))
                similarity = max(raw_similarity, enhanced_similarity * 0.7 + raw_similarity * 0.3)
                
                if similarity >= min_similarity:
                    chunks.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity': similarity,
                        'rank': i + 1
                    })
            
            logger.info(f"Found {len(chunks)} similar chunks for query in {knowledge_base_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error searching in {knowledge_base_id}: {e}")
            return []

    def get_relevant_context(
        self, 
        knowledge_base_id: str, 
        query: str, 
        max_tokens: int = 2000,
        top_k: int = 10
    ) -> str:
        """
        Get relevant context for a query from knowledge base
        
        Args:
            knowledge_base_id: Knowledge base to search in
            query: Search query
            max_tokens: Maximum tokens in returned context
            top_k: Number of chunks to consider
            
        Returns:
            Concatenated relevant context
        """
        similar_chunks = self.search_similar_chunks(
            knowledge_base_id, query, top_k=top_k
        )
        
        if not similar_chunks:
            logger.warning(f"No relevant chunks found for query in {knowledge_base_id}")
            return ""
        
        context_parts = []
        current_tokens = 0
        
        for chunk in similar_chunks:
            chunk_content = chunk['content']
            chunk_tokens = self.count_tokens(chunk_content)
            
            if current_tokens + chunk_tokens <= max_tokens:
                context_parts.append(f"[관련도: {chunk['similarity']:.2f}]\n{chunk_content}")
                current_tokens += chunk_tokens
            else:
                break
        
        context = "\n\n---\n\n".join(context_parts)
        logger.info(f"Built context with {current_tokens} tokens from {len(context_parts)} chunks")
        
        return context

    def list_knowledge_bases(self) -> List[str]:
        """List all available knowledge bases"""
        collections = self.client.list_collections()
        knowledge_bases = [
            col.name.replace('knowledge_', '') 
            for col in collections 
            if col.name.startswith('knowledge_')
        ]
        return knowledge_bases

    def delete_knowledge_base(self, knowledge_base_id: str) -> bool:
        """Delete a knowledge base collection"""
        collection_name = f"knowledge_{knowledge_base_id}"
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted knowledge base: {knowledge_base_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting knowledge base {knowledge_base_id}: {e}")
            return False


vector_db_service = VectorDBService()