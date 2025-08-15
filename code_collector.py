#!/usr/bin/env python3
"""
Скрипт для сбора всех .py файлов в один текстовый файл.
"""

import os
from pathlib import Path

def collect_python_files(output_file: str = "collected_code.txt", root_dir: str = ".") -> None:
    """
    Собирает все .py файлы из текущей директории и поддиректорий в один текстовый файл.
    
    Args:
        output_file: Имя выходного файла
        root_dir: Корневая директория для поиска
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Рекурсивный поиск всех .py файлов
        for py_file in Path(root_dir).rglob("*.py"):
            # Пропускаем файлы, начинающиеся с точки и файлы в __pycache__
            if py_file.name.startswith('.'):
                continue
            
            if '__pycache__' in str(py_file):
                continue
                
            # Исключаем каталог venv
            if 'venv' in str(py_file):
                continue
                
            # Исключаем сам скрипт сборщика
            if py_file.name == "code_collector.py":
                continue
                
            try:
                # Записываем полный путь к файлу
                outfile.write(f"{py_file.absolute()}\n")
                
                # Записываем содержимое файла
                with open(py_file, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                
                # Записываем разделитель и пустую строку
                outfile.write("\n" + "="*80 + "\n\n")
                
            except Exception as e:
                print(f"Ошибка при чтении файла {py_file}: {e}")

if __name__ == "__main__":
    collect_python_files()
    print("Сбор файлов завершен. Результат записан в collected_code.txt")