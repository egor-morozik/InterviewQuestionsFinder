import requests
import json
from config import Config

def view_questions(technology: str = None, limit: int = 10):
    """Показывает вопросы из Qdrant"""
    config = Config()
    
    if not config.QDRANT_URL or not config.QDRANT_API_KEY:
        print("❌ Qdrant не настроен")
        return
    
    payload = {
        "limit": limit,
        "with_payload": True
    }
    
    if technology:
        payload["filter"] = {
            "must": [{
                "key": "technology",
                "match": {"value": technology}
            }]
        }
    
    try:
        url = f"{config.QDRANT_URL}/collections/{config.COLLECTION_NAME}/points/scroll"
        response = requests.post(
            url,
            headers={
                "api-key": config.QDRANT_API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            points = data.get("result", {}).get("points", [])
            
            if not points:
                print("📭 В базе нет вопросов")
                return
            
            print(f"\n📚 Вопросы из базы ({len(points)} шт.):")
            print("=" * 80)
            
            for i, point in enumerate(points, 1):
                payload_data = point.get("payload", {})
                
                print(f"\n{i}. 📝 {payload_data.get('technology', 'Unknown')}")
                print(f"   ❓ {payload_data.get('question', 'No question')}")
                print(f"   💡 {payload_data.get('answer', 'No answer')[:150]}...")
                print(f"   📅 {payload_data.get('created_at', 'Unknown date')}")
                print("-" * 80)
        
        else:
            print(f"❌ Ошибка Qdrant: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def count_questions():
    """Считает количество вопросов по технологиям"""
    config = Config()
    
    if not config.QDRANT_URL or not config.QDRANT_API_KEY:
        print("❌ Qdrant не настроен")
        return
    
    try:
        url = f"{config.QDRANT_URL}/collections/{config.COLLECTION_NAME}"
        response = requests.get(
            url,
            headers={"api-key": config.QDRANT_API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = data.get("result", {}).get("points_count", 0)
            print(f"\n📊 Всего вопросов в базе: {count}")
            
            print("\n📈 Распределение по технологиям:")
            print("-" * 30)
            
            for tech in config.TECHNOLOGIES:
                payload = {
                    "filter": {
                        "must": [{
                            "key": "technology",
                            "match": {"value": tech}
                        }]
                    },
                    "limit": 1
                }
                
                search_url = f"{config.QDRANT_URL}/collections/{config.COLLECTION_NAME}/points/scroll"
                response = requests.post(
                    search_url,
                    headers={
                        "api-key": config.QDRANT_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get("result", {}).get("points", []))
                    print(f"  {tech}: {count} вопросов")
        
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Просмотр вопросов из базы")
    parser.add_argument("--tech", help="Фильтр по технологии")
    parser.add_argument("--limit", type=int, default=10, help="Лимит вывода")
    parser.add_argument("--count", action="store_true", help="Показать статистику")
    
    args = parser.parse_args()
    
    if args.count:
        count_questions()
    else:
        view_questions(args.tech, args.limit)
