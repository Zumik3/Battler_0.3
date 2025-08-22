# game/mixins/logging_mixin.py
"""Миксин для добавления логирования в классы."""

import logging
from typing import Any, Optional

class LoggingMixin:
    """Добавляет логирование в класс."""
    
    _logger: Optional[logging.Logger] = None
    
    @property
    def logger(self) -> logging.Logger:
        """Получить логгер для текущего класса."""
        if self._logger is None:
            try:
                logger_name = f"{type(self).__module__}.{type(self).__name__}"
                self._logger = logging.getLogger(logger_name)
            except Exception:
                self._logger = logging.getLogger("fallback")
        return self._logger
    
    def log_debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Записать DEBUG сообщение."""
        try:
            self.logger.debug(message, *args, **kwargs)
        except Exception:
            pass
    
    def log_info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Записать INFO сообщение."""
        try:
            self.logger.info(message, *args, **kwargs)
        except Exception:
            pass
    
    def log_warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Записать WARNING сообщение."""
        try:
            self.logger.warning(message, *args, **kwargs)
        except Exception:
            pass
    
    def log_error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Записать ERROR сообщение."""
        try:
            self.logger.error(message, *args, **kwargs)
        except Exception:
            pass
    
    def log_critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Записать CRITICAL сообщение."""
        try:
            self.logger.critical(message, *args, **kwargs)
        except Exception:
            pass