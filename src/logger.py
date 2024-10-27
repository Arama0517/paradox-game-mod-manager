import logging

from rich.logging import RichHandler

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
logger.addHandler(RichHandler())

__all__ = ['logger']
