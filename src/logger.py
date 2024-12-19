import logging

from rich.logging import RichHandler

logging.root.addHandler(RichHandler(markup=True, rich_tracebacks=True))

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)


__all__ = ['logger']
