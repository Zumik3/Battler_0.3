#!/usr/bin/env python3
"""
Скрипт для сбора всех Python файлов, JSON файлов и Markdown файлов (кроме README.md) 
в один текстовый файл с разделителями.
"""

import os
import pathlib
from typing import List, Tuple


def should_skip_directory(dir_path: pathlib.Path) -> bool:
    """
    Проверяет, нужно ли пропустить директорию.
    
    Args:
        dir_path: Путь к директории
        
    Returns:
        bool: True если директорию нужно пропустить, False если нет
    """
    # Пропускаем директории, начинающиеся с точки
    for part in dir_path.parts:
        if part.startswith('.'):
            return True
    return False


def collect_files() -> List[Tuple[str, str]]:
    """
    Собирает все Python файлы, JSON файлы и Markdown файлы (кроме README.md) 
    из указанных директорий, исключая директории, начинающиеся с точки.
    Также включает PROJECT_TODO.md из корня, если он существует.
    
    Returns:
        List[Tuple[str, str]]: Список кортежей (путь_к_файлу, содержимое_файла)
    """
    files_content = []
    
    # Добавляем PROJECT_TODO.md из корня, если он существует
    project_todo = pathlib.Path('PROJECT_TODO.md')
    if project_todo.is_file():
        try:
            with open(project_todo, 'r', encoding='utf-8') as f:
                content = f.read()
            files_content.append((str(project_todo), content))
            print(f"Добавлен файл: {project_todo}")
        except Exception as e:
            print(f"Ошибка при чтении файла {project_todo}: {e}")
    else:
        print("Файл PROJECT_TODO.md не найден в корне проекта")
    
    # Определяем директории и файлы для сбора
    targets = [
        'game',
        'tests', 
        'main.py',
        'guide'  # Добавлена новая папка
    ]
    
    # Расширения файлов, которые нужно собирать
    allowed_extensions = {'.py', '.json', '.md'}
    
    for target in targets:
        target_path = pathlib.Path(target)
        
        if should_skip_directory(target_path):
            print(f"Пропущена директория: {target_path} (начинается с точки)")
            continue
            
        if target_path.is_file() and target_path.suffix.lower() in allowed_extensions:
            # Проверяем, не является ли это README.md
            if target_path.name.lower() == 'readme.md':
                print(f"Пропущен файл: {target_path} (README.md игнорируется)")
                continue
                
            # Отдельный файл
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                files_content.append((str(target_path), content))
                print(f"Добавлен файл: {target_path}")
            except Exception as e:
                print(f"Ошибка при чтении файла {target_path}: {e}")
                
        elif target_path.is_dir():
            # Директория - рекурсивно собираем все разрешенные файлы
            for file_path in target_path.rglob('*'):
                # Проверяем, не находится ли файл в директории, начинающейся с точки
                if should_skip_directory(file_path.parent):
                    continue
                    
                if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                    # Проверяем, не является ли это README.md
                    if file_path.name.lower() == 'readme.md':
                        print(f"Пропущен файл: {file_path} (README.md игнорируется)")
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        files_content.append((str(file_path), content))
                        print(f"Добавлен файл: {file_path}")
                    except Exception as e:
                        print(f"Ошибка при чтении файла {file_path}: {e}")
        else:
            print(f"Цель не найдена или не является файлом/директорией: {target}")
    
    return files_content


def write_combined_file(files_content: List[Tuple[str, str]], output_file: str = 'combined_source.txt') -> None:
    """
    Записывает все файлы в один текстовый файл с разделителями.
    
    Args:
        files_content: Список кортежей (путь_к_файлу, содержимое_файла)
        output_file: Имя выходного файла
    """
    separator = "=" * 80
    
    # Записываем содержимое
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Сборник исходных кодов и конфигурационных файлов\n")
        f.write(f"Дата создания: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{separator}\n\n")
        
        for file_path, content in files_content:
            f.write(f"{separator}\n")
            f.write(f"Файл: {file_path}\n")
            f.write(f"{separator}\n\n")
            f.write(content)
            f.write(f"\n\n")
    
    print(f"Все файлы успешно объединены в {output_file}")


def main() -> None:
    """Основная функция скрипта."""
    output_file = 'combined_source.txt'
    
    # Очищаем результирующий файл при каждом запуске
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            pass  # Создаем пустой файл или очищаем существующий
        print(f"Файл {output_file} очищен")
    except Exception as e:
        print(f"Ошибка при очистке файла {output_file}: {e}")
    
    print("Сбор всех файлов...")
    
    # Собираем файлы
    files_content = collect_files()
    
    if not files_content:
        print("Не найдено файлов для сбора.")
        return
    
    print(f"\nНайдено файлов: {len(files_content)}")
    
    # Записываем в объединенный файл
    write_combined_file(files_content, output_file)
    
    print("Готово!")


if __name__ == '__main__':
    main()