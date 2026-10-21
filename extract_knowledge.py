import os
import json
import fitz  # PyMuPDF
import docx2txt


def extract_all_insights(folder_dir: str, output_file: str):
    """Извлекает текст из PDF и Word, ища ключевые слова по визуалу."""
    consolidated_data = []

    visual_keywords = [
        "стиль",
        "промпт",
        "prompt",
        "иллюстрация",
        "цвет",
        "композиция",
        "ошибка",
        "критерий",
        "обложка",
        "стикер",
        "персонаж",
        "фон",
        "разрешение",
    ]

    for filename in os.listdir(folder_dir):
        filepath = os.path.join(folder_dir, filename)
        file_insights = {"file": filename, "visual_guidelines": [], "key_prompts": []}

        # --- Обработка PDF ---
        if filename.lower().endswith(".pdf"):
            try:
                doc = fitz.open(filepath)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text("text")
                    for line in text.split("\n"):
                        line_clean = line.strip()
                        if (
                            any(kw in line_clean.lower() for kw in visual_keywords)
                            and len(line_clean) > 15
                        ):
                            file_insights["visual_guidelines"].append(
                                f"Стр. {page_num+1}: {line_clean}"
                            )
                doc.close()
            except Exception as e:
                file_insights["visual_guidelines"].append(f"Ошибка чтения PDF: {e}")

        # --- Обработка Word ---
        elif filename.lower().endswith((".docx", ".doc")):
            try:
                text = docx2txt.process(filepath)
                for line in text.split("\n"):
                    line_clean = line.strip()
                    if (
                        any(kw in line_clean.lower() for kw in visual_keywords)
                        and len(line_clean) > 15
                    ):
                        file_insights["visual_guidelines"].append(f"Word: {line_clean}")
            except Exception as e:
                file_insights["visual_guidelines"].append(f"Ошибка чтения Word: {e}")

        # Сохраняем только те файлы, где мы что-то нашли
        if file_insights["visual_guidelines"]:
            consolidated_data.append(file_insights)

    # Создаем папку output, если её нет
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(consolidated_data, f, ensure_ascii=False, indent=2)

    print(
        f"✅ Извлечение завершено. Найдено совпадений в {len(consolidated_data)} файлах."
    )
    print(f"📁 Результат сохранен в: {output_file}")


if __name__ == "__main__":
    # Пути относительно корня проекта
    RAW_DATA_DIR = "./raw_data"
    OUTPUT_FILE = "./output/course_visual_guidelines.json"

    print("🚀 Запуск оркестратора извлечения знаний...")
    extract_all_insights(RAW_DATA_DIR, OUTPUT_FILE)
