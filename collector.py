
import json
import requests
import hashlib
from datetime import datetime
from typing import List, Dict
from config import Config

class SimpleInterviewCollector:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 InterviewCollector/1.0"
        })
    
    def search_questions(self, technology: str) -> List[str]:
        """Ищет вопросы в интернете (упрощенный поиск)"""
        questions = []
        
        queries = self.config.SEARCH_QUERIES.get(technology, [
            f"{technology} собеседование вопросы",
            f"{technology} технические вопросы интервью"
        ])
        
        for query in queries[:2]:  
            try:
                url = f"https://html.duckduckgo.com/html/?q={query}"
                response = self.session.get(url, timeout=10)
                
                import re
                patterns = [
                    r'[^.!?]*\?[^.!?]*[.!?]',
                    r'Вопрос[^.!?]*:[^.!?]*[.!?]',
                    r'Q[^.!?]*:[^.!?]*[.!?]'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    for match in matches:
                        if technology.lower() in match.lower() and len(match) > 30:
                            clean_q = match.strip()
                            if clean_q not in questions:
                                questions.append(clean_q)
                
            except Exception as e:
                print(f"Ошибка поиска для {technology}: {e}")
        
        return list(set(questions))[:15]  
    
    def generate_answer(self, question: str) -> str:
        """Генерирует ответ через Groq API"""
        if not self.config.GROQ_API_KEY:
            return "Ответ недоступен. Настройте GROQ_API_KEY."
        
        prompt = f"""
        Ты опытный разработчик-интервьюер.
        Дай краткий и четкий ответ на вопрос для собеседования.
        
        Вопрос: {question}
        
        Ответ должен быть:
        - Лаконичным (3-5 предложений)
        - Конкретным и информативным
        - С примерами, если уместно
        - На русском языке
        
        Ответ:
        """
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 300
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                return f"Ошибка API: {response.status_code}"
                
        except Exception as e:
            return f"Ошибка генерации: {str(e)}"
    
    def create_embedding(self, text: str) -> List[float]:
        """Создает эмбеддинг для текста"""
        import numpy as np
        
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        vector = []
        for i in range(0, len(hash_bytes), 4):
            if len(vector) >= self.config.VECTOR_SIZE:
                break
            chunk = hash_bytes[i:i+4]
            val = int.from_bytes(chunk, 'big') / 2**32
            vector.append(val)
        
        while len(vector) < self.config.VECTOR_SIZE:
            vector.append(0.0)
        
        return vector[:self.config.VECTOR_SIZE]
    
    def save_to_qdrant(self, question: str, answer: str, technology: str):
        """Сохраняет вопрос в Qdrant"""
        if not self.config.QDRANT_URL or not self.config.QDRANT_API_KEY:
            print("Qdrant не настроен. Пропускаем сохранение.")
            return
        
        embedding = self.create_embedding(f"{question} {technology}")
        
        q_id = hashlib.md5(f"{question}{technology}".encode()).hexdigest()
        
        payload = {
            "points": [{
                "id": q_id,
                "vector": embedding,
                "payload": {
                    "question": question,
                    "answer": answer,
                    "technology": technology,
                    "created_at": datetime.now().isoformat(),
                    "source": "auto_collected"
                }
            }]
        }
        
        try:
            search_url = f"{self.config.QDRANT_URL}/collections/{self.config.COLLECTION_NAME}/points/{q_id}"
            response = requests.get(
                search_url,
                headers={"api-key": self.config.QDRANT_API_KEY}
            )
            
            if response.status_code == 200:
                print(f"✓ Вопрос уже существует: {question[:50]}...")
                return False
            
            url = f"{self.config.QDRANT_URL}/collections/{self.config.COLLECTION_NAME}/points"
            response = requests.put(
                url,
                headers={
                    "api-key": self.config.QDRANT_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ Сохранено: {question[:50]}...")
                return True
            else:
                print(f"✗ Ошибка Qdrant: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Ошибка сохранения: {e}")
            return False
    
    def collect_for_tech(self, technology: str) -> Dict:
        """Собирает вопросы для одной технологии"""
        print(f"\n🔍 Сбор вопросов для: {technology}")
        
        questions = self.search_questions(technology)
        print(f"   Найдено вопросов: {len(questions)}")
        
        results = {"added": 0, "total": len(questions)}
        
        for i, question in enumerate(questions, 1):
            print(f"   [{i}/{len(questions)}] Обработка...")
            
            answer = self.generate_answer(question)
            
            if self.save_to_qdrant(question, answer, technology):
                results["added"] += 1
            
            import time
            time.sleep(2)
        
        return results
    
    def run(self):
        """Запускает полный сбор"""
        print("🚀 Запуск сбора вопросов для собеседований")
        print("=" * 50)
        
        total_results = {}
        
        for tech in self.config.TECHNOLOGIES:
            try:
                results = self.collect_for_tech(tech)
                total_results[tech] = results
                
                import time
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Ошибка для {tech}: {e}")
                total_results[tech] = {"error": str(e)}
        
        self.save_report(total_results)
        
        print("\n" + "=" * 50)
        print("📊 ИТОГИ СБОРА:")
        for tech, res in total_results.items():
            if "added" in res:
                print(f"  {tech}: {res['added']}/{res['total']} вопросов")

        self.generate_github_summary(total_results)
        
        return total_results
    
    def generate_github_summary(self, results: Dict):
        """Генерирует summary для GitHub Actions"""
        summary = ["## 📊 Результаты сбора", ""]
        
        for tech, res in results.items():
            if "added" in res:
                summary.append(f"### {tech}")
                summary.append(f"- Найдено: {res['total']}")
                summary.append(f"- Добавлено: {res['added']}")
                summary.append("")
        
        with open("github_summary.md", "w", encoding="utf-8") as f:
            f.write("\n".join(summary))
        
        print("📋 Summary сохранен в github_summary.md")

    def save_report(self, results: Dict):
        """Сохраняет отчет в читаемом формате"""
        report = []
        report.append("# 📚 Отчет о сборе вопросов для собеседований")
        report.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        for tech, res in results.items():
            report.append(f"## {tech}")
            
            if "error" in res:
                report.append(f"❌ Ошибка: {res['error']}")
            else:
                report.append(f"- Найдено вопросов: {res['total']}")
                report.append(f"- Добавлено в базу: {res['added']}")
                report.append(f"- Пропущено (дубликаты): {res['total'] - res['added']}")
            
            report.append("")
        
        with open("collection_report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        
        print("📄 Отчет сохранен в collection_report.md")
        
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    collector = SimpleInterviewCollector()
    collector.run()
