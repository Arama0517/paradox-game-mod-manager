import logging

from rich.logging import RichHandler

logging.root.addHandler(RichHandler(markup=True, rich_tracebacks=True))

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
# logger.addHandler(RichHandler(markup=True))


__all__ = ['logger']
