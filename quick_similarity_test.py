#!/usr/bin/env python3
"""
Quick similarity test for optimized RAG system
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.external_services.vector_db_service import vector_db_service

def test_similarity_scores():
    """Test similarity scores with optimized system"""
    
    print("🚀 Testing optimized similarity scores...")
    
    # Test queries
    test_queries = [
        "RESTful API 설계 원칙",
        "API 설계",
        "REST API",
        "HTTP 엔드포인트 디자인"
    ]
    
    knowledge_base_id = "backend"
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Get similarity scores
        results = vector_db_service.search_similar_chunks(
            knowledge_base_id=knowledge_base_id,
            query=query,
            top_k=3
        )
        
        if results:
            print(f"  📊 Top {len(results)} results:")
            for i, result in enumerate(results, 1):
                similarity = result.get('similarity', 0)
                content_preview = result.get('content', '')[:80] + "..."
                print(f"    {i}. [유사도: {similarity:.3f}] {content_preview}")
        else:
            print("  ❌ No results found")
    
    print("\n✅ Similarity testing completed!")

if __name__ == "__main__":
    try:
        test_similarity_scores()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()