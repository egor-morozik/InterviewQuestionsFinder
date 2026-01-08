#!/usr/bin/env python3
"""
Создает красивый отчет для GitHub Actions
"""

import json
from datetime import datetime
import sys

def generate_summary():
    """Генерирует summary для GitHub Actions"""
    
    try:
        with open("results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("❌ Файл results.json не найден")
        return
    
    summary_lines = []
    
    # Заголовок
    summary_lines.append("# 🚀 Результаты автоматического сбора")
    summary_lines.append("")
    summary_lines.append(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    summary_lines.append("")
    
    # Таблица результатов
    summary_lines.append("## 📊 Статистика по технологиям")
    summary_lines.append("")
    summary_lines.append("| Технология | Найдено | Добавлено |")
    summary_lines.append("|------------|---------|-----------|")
    
    total_found = 0
    total_added = 0
    
    for tech, stats in results.items():
        if isinstance(stats, dict) and "total" in stats:
            found = stats.get("total", 0)
            added = stats.get("added", 0)
            summary_lines.append(f"| {tech} | {found} | {added} |")
            total_found += found
            total_added += added
    
    summary_lines.append("")
    summary_lines.append(f"**Итого:** Найдено {total_found}, добавлено {total_added} вопросов")
    summary_lines.append("")
    summary_lines.append("📄 [Полный отчет](artifact/collection-report/collection_report.md)")
    
    # Выводим в stdout для GitHub Actions
    print("\n".join(summary_lines))
    
    # Также сохраняем в файл
    with open("github_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

if __name__ == "__main__":
    generate_summary()