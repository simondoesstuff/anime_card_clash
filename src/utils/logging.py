from datetime import datetime
from rich import print


def tprint(*args, **kwargs):
    time_str = datetime.now().strftime("%T")
    print(f"[bold white][{time_str}][/bold white]", *args, **kwargs)