# game/mixins/__init__.py
"""Централизованные миксины для всего проекта."""

from .logging_mixin import LoggingMixin
from .ui_mixin import HeaderMixin, FooterMixin, StandardLayoutMixin, LayoutProtocol

__all__ = [
    'LoggingMixin',
    'HeaderMixin', 
    'FooterMixin', 
    'StandardLayoutMixin',
    'LayoutProtocol'
]