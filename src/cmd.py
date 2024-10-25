import subprocess


def clear():
    subprocess.check_call(['cmd.exe', '/c', 'cls'])


__all__ = ['clear']
