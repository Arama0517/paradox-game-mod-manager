def patch_requests(settings: dict):
    import warnings

    import urllib3
    from requests.sessions import Session

    origin = Session.__init__

    def patched(self):
        origin(self)
        self.verify = settings.get('ssl') or True

    warnings.filterwarnings(
        'ignore', category=urllib3.exceptions.InsecureRequestWarning
    )

    Session.__init__ = patched


def init():
    from src.path import initialize_data_dir
    from src.settings import settings

    patch_requests(settings)
    initialize_data_dir(settings)


init()
