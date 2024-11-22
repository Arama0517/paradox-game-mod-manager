from src.pages.install import get_item_children
from src.steam_clients import client

# Kaiserreich简体中文版
Kaiserreich_CN_item_id = 2946487287


def test_get_item_children():
    client.anonymous_login()
    result = get_item_children(Kaiserreich_CN_item_id)
    print(result)
