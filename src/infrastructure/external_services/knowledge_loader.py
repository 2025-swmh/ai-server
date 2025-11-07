"""
Knowledge base loader service with RAG functionality
Clean Architecture - Frameworks & Drivers Layer
"""
import re
from pathlib import Path
from typing import List, Optional
from src.core.config.settings import KNOWLEDGE_BASE_MAP, settings
from src.core.exceptions.handlers import KnowledgeBaseNotFoundException
from src.infrastructure.external_services.vector_db_service import vector_db_service
import logging

logger = logging.getLogger(__name__)


class KnowledgeLoader:
    """
    Knowledge base file loader and processor with RAG functionality
    Handles loading, compression, chunking, and semantic search of knowledge base files
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent.parent
        self.vector_db = vector_db_service
        logger.info(f"Knowledge loader initialized with base path: {self.base_path}")

    def load_knowledge_base(self, filename_or_template: str) -> str:
        """
        Load knowledge base file for given template or filename

        Args:
            filename_or_template: Template identifier or filename

        Returns:
            Knowledge base content

        Raises:
            KnowledgeBaseNotFoundException: When knowledge base file is not found
        """
        if filename_or_template.endswith('.md'):
            filename = filename_or_template
        else:
            filename = KNOWLEDGE_BASE_MAP.get(filename_or_template)
            if not filename:
                logger.error(f"No knowledge base mapping found for template: {filename_or_template}")
                raise KnowledgeBaseNotFoundException(f"template: {filename_or_template}")

        file_path = self.base_path / filename

        if not file_path.exists():
            logger.error(f"Knowledge base file not found: {file_path}")
            raise KnowledgeBaseNotFoundException(str(file_path))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Loaded knowledge base: {filename} ({len(content)} chars)")
                return content
        except Exception as e:
            logger.error(f"Error reading knowledge base file {file_path}: {str(e)}")
            raise KnowledgeBaseNotFoundException(str(file_path))

    def compress_knowledge(
        self, 
        knowledge: str, 
        max_length: int = None
    ) -> str:
        """
        Compress knowledge base content to reduce token usage

        Args:
            knowledge: Original knowledge base content
            max_length: Maximum length for compressed content

        Returns:
            Compressed knowledge base content
        """
        max_length = max_length or settings.KNOWLEDGE_BASE_MAX_LENGTH

        logger.debug(f"Compressing knowledge from {len(knowledge)} chars")

        compressed = re.sub(r'```[\s\S]*?```', '[코드 예시]', knowledge)
        
        compressed = re.sub(r'\n\s*\n', '\n', compressed)
        compressed = re.sub(r' +', ' ', compressed)
        
        compressed = compressed.strip()

        if len(compressed) > max_length:
            compressed = compressed[:max_length]
            logger.warning(f"Knowledge truncated to {max_length} chars")

        logger.info(f"Knowledge compressed to {len(compressed)} chars")
        return compressed

    def chunk_knowledge(
        self, 
        knowledge: str, 
        chunk_size: int = None, 
        overlap: int = None
    ) -> List[str]:
        """
        Split knowledge base into chunks for RAG processing

        Args:
            knowledge: Original knowledge base content
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of knowledge chunks
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        overlap = overlap or settings.CHUNK_OVERLAP

        if len(knowledge) <= chunk_size:
            logger.info("Knowledge fits in single chunk")
            return [knowledge]
        
        chunks = []
        start = 0
        
        while start < len(knowledge):
            end = start + chunk_size
            
            if end < len(knowledge):
                newline_pos = knowledge.rfind('\n', start, end)
                if newline_pos > start:
                    end = newline_pos
                else:
                    space_pos = knowledge.rfind(' ', start, end)
                    if space_pos > start:
                        end = space_pos
            
            chunk = knowledge[start:end].strip()
            if chunk:
                chunks.append(chunk)
                logger.debug(f"Created chunk {len(chunks)}: {len(chunk)} chars")
            
            start = end - overlap if end < len(knowledge) else end
            
        logger.info(f"Knowledge split into {len(chunks)} chunks")
        return chunks

    def get_available_templates(self) -> List[str]:
        """Get list of available knowledge base templates"""
        return list(KNOWLEDGE_BASE_MAP.keys())

    def validate_template(self, template_id: str) -> bool:
        """Check if template has valid knowledge base mapping"""
        return template_id in KNOWLEDGE_BASE_MAP

    def initialize_knowledge_base_vectors(self, template_id: str) -> bool:
        """
        Initialize knowledge base vectors in ChromaDB
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            content = self.load_knowledge_base(template_id)
            
            metadata = {
                "template_id": template_id,
                "source_file": KNOWLEDGE_BASE_MAP.get(template_id, f"{template_id}.md"),
                "content_length": len(content)
            }
            
            self.vector_db.store_knowledge_base(
                knowledge_base_id=template_id,
                content=content,
                metadata=metadata
            )
            
            logger.info(f"Successfully initialized vectors for knowledge base: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vectors for {template_id}: {e}")
            return False

    def get_relevant_context_rag(
        self, 
        template_id: str, 
        query: str, 
        max_tokens: int = 2000
    ) -> str:
        """
        Get relevant context using RAG (Retrieval-Augmented Generation)
        
        Args:
            template_id: Knowledge base template ID
            query: User query or question
            max_tokens: Maximum tokens in returned context
            
        Returns:
            Relevant context from knowledge base
        """
        try:
            if not self._is_knowledge_base_initialized(template_id):
                logger.info(f"Initializing knowledge base vectors for {template_id}")
                if not self.initialize_knowledge_base_vectors(template_id):
                    logger.warning(f"Failed to initialize {template_id}, falling back to full content")
                    return self._fallback_to_full_content(template_id, max_tokens)
            
            context = self.vector_db.get_relevant_context(
                knowledge_base_id=template_id,
                query=query,
                max_tokens=max_tokens
            )
            
            if not context:
                logger.warning(f"No relevant context found for query in {template_id}, falling back")
                return self._fallback_to_full_content(template_id, max_tokens)
            
            logger.info(f"Retrieved RAG context for {template_id}: {len(context)} chars")
            return context
            
        except Exception as e:
            logger.error(f"Error in RAG context retrieval for {template_id}: {e}")
            return self._fallback_to_full_content(template_id, max_tokens)

    def _is_knowledge_base_initialized(self, template_id: str) -> bool:
        """Check if knowledge base is already initialized in vector DB"""
        try:
            available_kbs = self.vector_db.list_knowledge_bases()
            return template_id in available_kbs
        except Exception as e:
            logger.error(f"Error checking if {template_id} is initialized: {e}")
            return False

    def _fallback_to_full_content(self, template_id: str, max_tokens: int) -> str:
        """Fallback to compressed full content when RAG fails"""
        try:
            content = self.load_knowledge_base(template_id)
            
            max_chars = max_tokens * 4
            
            compressed = self.compress_knowledge(content, max_length=max_chars)
            logger.info(f"Using fallback compressed content for {template_id}")
            return compressed
            
        except Exception as e:
            logger.error(f"Fallback failed for {template_id}: {e}")
            return "Knowledge base content is temporarily unavailable."

    def search_knowledge(
        self, 
        template_id: str, 
        query: str, 
        top_k: int = 5
    ) -> List[dict]:
        """
        Search for relevant chunks in knowledge base
        
        Args:
            template_id: Knowledge base template ID
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant chunks with similarity scores
        """
        try:
            if not self._is_knowledge_base_initialized(template_id):
                if not self.initialize_knowledge_base_vectors(template_id):
                    return []
            
            return self.vector_db.search_similar_chunks(
                knowledge_base_id=template_id,
                query=query,
                top_k=top_k
            )
            
        except Exception as e:
            logger.error(f"Error searching knowledge base {template_id}: {e}")
            return []

    def reinitialize_all_knowledge_bases(self) -> dict:
        """
        Reinitialize all knowledge bases in vector database
        
        Returns:
            Dictionary with initialization results
        """
        results = {}
        
        for template_id in self.get_available_templates():
            try:
                success = self.initialize_knowledge_base_vectors(template_id)
                results[template_id] = "success" if success else "failed"
            except Exception as e:
                results[template_id] = f"error: {str(e)}"
        
        logger.info(f"Knowledge base initialization results: {results}")
        return results


knowledge_loader = KnowledgeLoader()