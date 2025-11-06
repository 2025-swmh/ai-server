"""
Knowledge base loader service
Clean Architecture - Frameworks & Drivers Layer
"""
import re
from pathlib import Path
from typing import List, Optional
from src.core.config.settings import KNOWLEDGE_BASE_MAP, settings
from src.core.exceptions.handlers import KnowledgeBaseNotFoundException
import logging

logger = logging.getLogger(__name__)


class KnowledgeLoader:
    """
    Knowledge base file loader and processor
    Handles loading, compression, and chunking of knowledge base files
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent.parent
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
        # Check if it's a direct filename
        if filename_or_template.endswith('.md'):
            filename = filename_or_template
        else:
            # Try to get from mapping
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

        # Remove code blocks (content between ```)
        compressed = re.sub(r'```[\s\S]*?```', '[코드 예시]', knowledge)
        
        # Remove excessive whitespace
        compressed = re.sub(r'\n\s*\n', '\n', compressed)
        compressed = re.sub(r' +', ' ', compressed)
        
        # Remove unnecessary characters
        compressed = compressed.strip()

        # Limit to maximum length
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
            
            # Try to split at natural boundaries
            if end < len(knowledge):
                # Find nearest newline
                newline_pos = knowledge.rfind('\n', start, end)
                if newline_pos > start:
                    end = newline_pos
                else:
                    # Find nearest space
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


# Singleton instance
knowledge_loader = KnowledgeLoader()