#!/usr/bin/env python3
"""
Simple test script for RAG functionality
"""
import asyncio
import sys
import os

# Add the source directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.external_services.knowledge_loader import knowledge_loader


async def test_rag_functionality():
    """Test RAG functionality with knowledge base"""
    
    print("🧪 Testing RAG functionality...")
    
    # Test 1: Initialize knowledge base vectors
    print("\n1. Testing knowledge base vector initialization...")
    template_id = "backend"
    
    try:
        success = knowledge_loader.initialize_knowledge_base_vectors(template_id)
        if success:
            print(f"✅ Successfully initialized vectors for {template_id}")
        else:
            print(f"❌ Failed to initialize vectors for {template_id}")
            return
    except Exception as e:
        print(f"❌ Error initializing vectors: {e}")
        return
    
    # Test 2: Search for relevant content
    print("\n2. Testing semantic search...")
    
    test_queries = [
        "RESTful API 설계 원칙",
        "데이터베이스 최적화 방법", 
        "마이크로서비스 아키텍처",
        "Python 성능 최적화"
    ]
    
    for query in test_queries:
        print(f"\n검색 쿼리: '{query}'")
        
        try:
            # Search for similar chunks
            results = knowledge_loader.search_knowledge(
                template_id=template_id,
                query=query,
                top_k=3
            )
            
            if results:
                print(f"  📄 Found {len(results)} relevant chunks:")
                for i, result in enumerate(results, 1):
                    similarity = result.get('similarity', 0)
                    content_preview = result.get('content', '')[:100] + "..."
                    print(f"    {i}. [유사도: {similarity:.3f}] {content_preview}")
            else:
                print("  ❌ No relevant chunks found")
                
        except Exception as e:
            print(f"  ❌ Error searching: {e}")
    
    # Test 3: Get relevant context for RAG
    print("\n3. Testing RAG context retrieval...")
    
    test_rag_query = "백엔드 개발자 면접에서 API 설계에 대해 질문하고 싶다"
    
    try:
        context = knowledge_loader.get_relevant_context_rag(
            template_id=template_id,
            query=test_rag_query,
            max_tokens=1000
        )
        
        if context:
            print(f"✅ Retrieved RAG context ({len(context)} characters):")
            print(f"📝 Context preview: {context[:200]}...")
        else:
            print("❌ No context retrieved")
            
    except Exception as e:
        print(f"❌ Error retrieving RAG context: {e}")
    
    # Test 4: List available knowledge bases
    print("\n4. Testing knowledge base listing...")
    
    try:
        available_kbs = knowledge_loader.vector_db.list_knowledge_bases()
        print(f"📚 Available knowledge bases: {available_kbs}")
    except Exception as e:
        print(f"❌ Error listing knowledge bases: {e}")
    
    print("\n🎉 RAG testing completed!")


if __name__ == "__main__":
    # Run the test
    try:
        asyncio.run(test_rag_functionality())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()