# game/logging_config.py
"""Настройка логирования."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

def setup_logging(config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Настройка логирования.
    
    Args:
        config: Параметры логирования
        
    Returns:
        Корневой логгер
    """
    # Параметры по умолчанию
    if config is None:
        config = {}
        
    level = config.get('level', logging.INFO)
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
        
    log_dir = Path(config.get('log_directory', 'logs'))
    log_file = config.get('log_file', 'game.log')
    file_max_bytes = config.get('file_max_bytes', 10485760)
    backup_count = config.get('backup_count', 5)
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Создаем директорию для логов
    log_dir.mkdir(exist_ok=True)
    full_log_path = log_dir / log_file
    
    # Настройка форматтеров
    formatter = logging.Formatter(log_format)
    
    # Настройка хендлеров
    handlers: List[logging.Handler] = []  # Явная типизация
    
    # Файловый хендлер с ротацией
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(full_log_path),
        maxBytes=file_max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)
    
    # Консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    
    for handler in handlers:
        root_logger.addHandler(handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено. Уровень: {logging.getLevelName(level)}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для модуля.
    
    Args:
        name: Имя модуля
        
    Returns:
        Логгер
    """
    return logging.getLogger(name)

def shutdown_logging() -> None:
    """Завершить логирование."""
    logging.shutdown()