import json
from os import path
boards_dir=path.join(path.dirname(__file__),"Boards")
def query(boardname) -> bool:
    board_file=path.join(boards_dir,boardname+".json")
    if not path.exists(board_file):
        return False
    with open(board_file) as f:
        try:
            data=json.load(f)
        except json.JSONDecodeError:
            return False
        return valid_data(data)

def valid_data(data) -> bool:
    if "numteams" not in data:
        return False
    if "dim" not in data:
        return False
    if "turnorder" not in data:
        return False
    if "boarddata" not in data:
        return False
    return True

def getBoard(boardname) -> dict:
    if not query(boardname):
        raise FileNotFoundError
    board_file=path.join(boards_dir,boardname+".json")
    with open(board_file) as f:
        return json.load(f)
        