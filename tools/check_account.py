import sys

from steam.webauth import WebAuth

import src

__all__ = ['src']


def main():
    user_name, password = sys.argv[1:3]
    webauth = WebAuth()
    webauth.login(user_name, password)
    print(webauth.refresh_token, type(webauth.refresh_token))


if __name__ == '__main__':
    main()
