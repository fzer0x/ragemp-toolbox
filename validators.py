import os

REQUIRED_FILES = [
    "common.rpf",
    "update.rpf",
]

def validate_redux_folder(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    files = os.listdir(path)
    for req in REQUIRED_FILES:
        if req not in files:
            return False
    return True