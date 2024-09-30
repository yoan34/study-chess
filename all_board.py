import math
import pprint
import chess
import os
import random
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from tools import (
    choice_a_play,
    check_a_play,
    get_openings,
    get_json_from_file,
    create_json_file,
    add_play_in_json_file,
    increment_play_in_json_file,
    create_next_play_in_json_file,
    get_correct_opening_name
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


# Montre les fichiers statiques (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Utilise Jinja2 pour les templates HTML
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    print('heheh')
    return templates.TemplateResponse("all_openings.html", {"request": request})


@app.get("/boards_for_white", response_class=JSONResponse)
async def play_move(request: Request):
    files = os.listdir("data/0,1400")
    openings_names = {}
    for file in files:
        with open(f"data/0,1400/{file}", "r") as f:
            openings = json.load(f)
        
        for opening, values in openings.items():
            if "name" in values:
                if values['name'] is not None and values['name'] != "None":
                    name = values['name']['name']
                else:
                    name = ""
                if name not in openings_names:
                    openings_names[name] = {"count": 0, "moves": []}

                openings_names[name]["count"] += 1
                openings_names[name]["moves"].append({opening: sorted(values["moves"], key=lambda x: x['white'] * x['averageRating']*(1 + 0.05 * math.log(x['freq'] + 1)), reverse=True)[:2]})

                
    openings_names = dict(sorted(openings_names.items(), key=lambda item: item[1]["count"]))

    result = []
    for key, values in openings_names.items():
        count = values["count"]
        for move in values["moves"]:
            the_move, top_move = next(iter(move.items()))
            if not the_move.startswith('e2e4'):
                print(f"{the_move=} not start by e2e4")
                continue
            boards_img = os.listdir('static/board_img')
            boards_name_img = [board_img.split('.')[0] for board_img in boards_img]
            if the_move in boards_name_img:
                print(f"image already exist for this move {the_move}")
                continue

            if len(the_move.split(',')) > 20:
                continue
            board = chess.Board()
            if len(the_move.split(',')) % 2 == 0:
                for move_uci in the_move.split(','):
                    board.push_uci(move_uci)
                    
                fen=board.fen()
                result.append({
                    "name": key,
                    "play": the_move,
                    "fen": fen,
                    "top_move": top_move,
                    "total_move": len(the_move.split(',')),
                    "last_play": the_move.split(',')[-1]
                })
                    
    result = sorted(result, key=lambda x: x['play'])

    return result

@app.get("/boards_for_black", response_class=JSONResponse)
async def play_move(request: Request):
    files = os.listdir("data/0,1400")
    openings_names = {}
    print("in black")
    for file in files:
        with open(f"data/0,1400/{file}", "r") as f:
            openings = json.load(f)
        
        for opening, values in openings.items():
            print(f"black: {opening}")
            if "name" in values:
                if values['name'] is not None and values['name'] != "None":
                    name = values['name']['name']
                else:
                    name = ""
                if name not in openings_names:
                    openings_names[name] = {"count": 0, "moves": []}

                openings_names[name]["count"] += 1
                openings_names[name]["moves"].append({opening: sorted(values["moves"], key=lambda x: x['black'] * x['averageRating']*(1 + 0.05 * math.log(x['freq'] + 1)), reverse=True)[:2]})

                
    openings_names = dict(sorted(openings_names.items(), key=lambda item: item[1]["count"]))

    result = []
    for key, values in openings_names.items():
        count = values["count"]
        for move in values["moves"]:
            the_move, top_move = next(iter(move.items()))
            if not the_move:
                continue
            boards_img = os.listdir('static/board_img')
            boards_name_img = [board_img.split('.')[0] for board_img in boards_img]
            if the_move in boards_name_img:
                print(f"image already exist for this move {the_move}")
                continue

            if len(the_move.split(',')) > 20:
                continue
            board = chess.Board()
            if len(the_move.split(',')) % 2 == 1:
                
                for move_uci in the_move.split(','):
                    if move_uci:
                        board.push_uci(move_uci)
                    
                fen=board.fen()
                result.append({
                    "name": key,
                    "play": the_move,
                    "fen": fen,
                    "top_move": top_move,
                    "total_move": len(the_move.split(',')),
                    "last_play": the_move.split(',')[-1]
                })
                    
    result = sorted(result, key=lambda x: x['play'])

    return result


@app.get("/white_openings", response_class=JSONResponse)
async def play_move(request: Request):
    files = os.listdir("data/0,1400")
    openings_names = {}
    OPENINGS_NAMES = {}
    for file in files:
        with open(f"data/0,1400/{file}", "r") as f:
            openings = json.load(f)
        
        for opening, values in openings.items():
            if "name" in values:
                if values['name'] is not None and values['name'] != "None":
                    name = values['name']['name']
                    if name not in OPENINGS_NAMES:
                        OPENINGS_NAMES[name] = []
                    OPENINGS_NAMES[name].append(opening)
    
    pprint.pprint(OPENINGS_NAMES)
    
    for opening_name, plays in OPENINGS_NAMES.items():
        min_length = min(len(s) for s in plays)
        OPENINGS_NAMES[opening_name] = [s for s in plays if len(s) == min_length][0]
        print(f"LEN: {len(OPENINGS_NAMES[opening_name])}")
        if len(OPENINGS_NAMES[opening_name]) > 1:
            print(opening_name, OPENINGS_NAMES[opening_name])
    
    
    result = []
    
    for name, move in OPENINGS_NAMES.items():
        board = chess.Board()
        for move_uci in move.split(','):
            if move_uci:
                board.push_uci(move_uci)
                    
                fen=board.fen()
        result.append([move, name, fen])
    pprint.pprint(result)
    result = sorted(result, key=lambda x: (len(x[0].split(',')), x[1]))
    print("after")
    pprint.pprint(result)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
