import time
from os.path import getmtime
from filelock import FileLock


class UpdateID:
    def __init__(self) -> None:

        with FileLock("update_id.lock", timeout=10):
            try:
                with open("update_id", "r") as f:
                    pass
                t = time.time() - getmtime("update_id")
                if (t > 60*60*24*7):
                    raise FileNotFoundError
            except FileNotFoundError:
                with open("update_id", "w") as f:
                    f.write("-1")

    def compare(self, b) -> bool:
        with FileLock("update_id.lock", timeout=10):
            with open("update_id", "r+t") as f:
                last_update_id = int(f.read())
                if b <= last_update_id:
                    return False
                else:
                    f.seek(0)
                    f.write(f"{b}")
                    f.truncate()
                    return True
