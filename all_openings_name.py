import os
import chess
import json
from collections import defaultdict


files = os.listdir("data/0,1400")
openings_names = {}
for file in files:
    with open(f"data/0,1400/{file}", "r") as f:
        openings = json.load(f)
    
    for opening, values in openings.items():
        if opening == "King's Gambit Declined: Petrov's Defense":
            print(f"{opening=} play={values}")
        if "name" in values:
            if values['name'] is not None and values['name'] != "None":
                name = values['name']['name']
            else:
                name = ""
            #print(f"{opening}  count={values['count']}  name={name}")
            if name not in openings_names:
                openings_names[name] = {"count": 0, "moves": []}

            openings_names[name]["count"] += 1
            openings_names[name]["moves"].append(opening)
            
print(list(openings_names.items()))
openings_names = dict(sorted(openings_names.items(), key=lambda item: item[1]["count"]))

for key, values in openings_names.items():
    moves = sorted(values["moves"])
    count = values["count"]
    if "King's Gambit"in key:
        for move in moves:
            board = chess.Board()
            for move_uci in move.split(','):
                board.push_uci(move_uci)
            fen=board.fen()
            print(f"{key:<50} {move:<80} {fen=}")
        print()
    
print(len(openings))


    
    
