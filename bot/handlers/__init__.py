from __future__ import annotations

from aiogram import Router

from .messages import router as messages_router
from .start import router as start_router


router = Router()
router.include_router(start_router)
router.include_router(messages_router)


__all__ = ['router']
