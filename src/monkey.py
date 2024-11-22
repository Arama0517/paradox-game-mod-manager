from urllib3.exceptions import InsecureRequestWarning


def patch_requests():
    from warnings import filterwarnings

    from requests.sessions import Session

    from src.settings import settings

    origin = Session.__init__

    def patched(self):
        origin(self)
        self.verify = settings.get('ssl') or True

    filterwarnings('ignore', category=InsecureRequestWarning)

    Session.__init__ = patched


def patch_asyncio():
    from asyncio import set_event_loop_policy

    from asyncio_gevent import EventLoopPolicy

    set_event_loop_policy(EventLoopPolicy())


def patch_all():
    patch_asyncio()
    patch_requests()
