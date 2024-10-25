def ssl():
    import warnings

    import urllib3
    from requests.sessions import Session

    from src.settings import settings

    origin = Session.__init__

    def patched(self):
        origin(self)
        self.verify = settings.get('ssl') or True

    warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

    Session.__init__ = patched


def init():
    from loguru import logger
    from rich.logging import RichHandler

    # 设置 logger
    logger.remove()
    logger.add(RichHandler())

    # 适配用反代加速Steam的工具
    ssl()


init()
