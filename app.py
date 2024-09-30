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
    get_correct_opening_name,
    get_top_2_move
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
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/play", response_class=JSONResponse)
async def play_move(request: Request):
    data = await request.json()
    play, rating = data.get("play"), data.get("rating")
    print(f"play_move - {play=}, {rating=}")
    moves_played = play.split(',')
    
    if len(moves_played) == 1 and not moves_played[0]:
        moves_played = []
        
    filename = Path(f"data/{rating}/{len(moves_played)}_moves.json")

    if not filename.exists():
        create_json_file(filename)

    openings = get_json_from_file(filename)
    
    if play not in openings:
        print(f"play_move - MOVE {play} NOT EXIST: CALL API")
        opening = get_openings(play=play, rating=rating)
        add_play_in_json_file(filename, opening, play)
        openings = {play: opening}
    else:
        print(f"play_move - MOVE {play} EXIST!!!")
        
        
    next_play = choice_a_play(openings=openings, play=play)
    opening_name_play = f"{play},{next_play['uci'].replace('-', '')}" if play else f"{next_play['uci'].replace('-', '')}"
    opening_name = get_correct_opening_name(opening_name_play, rating, len(moves_played)+1)
    print(f"waiiiiiiiiiiiit {next_play}")
    if "name" in next_play["name"]:
        opening_name = next_play["name"]["name"] if opening_name is None else opening_name
    print(f"OPENING_NAME AFTER COMPUTER PLAY: {opening_name}")
    if "error" in next_play:
        return {"error": "no more line"}
    create_next_play_in_json_file(play, rating, next_play)
    
    top_next_play = f"{play},{next_play['uci'].replace('-', '')}"
    if top_next_play.startswith(','):
        top_next_play = top_next_play[1:]
    print(f"{top_next_play=}")
    top_openings = get_openings(play=top_next_play, rating=rating)
    get_top_2_play = get_top_2_move(top_openings["moves"], play=top_next_play)
    return {"next_play": next_play, "moves": openings[play]["moves"], "opening_name": opening_name, "top_play": get_top_2_play}


@app.post("/check_move", response_class=JSONResponse)
async def check_move(request: Request):
    
    data = await request.json()
    play, rating = data.get("play"), data.get("rating")
    print(f"check_move - {play=}, {rating=}")
    
    moves_played = play.split(',')[:-1] # on veut pas le dernier move 
        
    filename = Path(f"data/{rating}/{len(moves_played)}_moves.json")
    
    print(f"here: {play=}")
    openings = get_json_from_file(filename)
    
        
    previous_move = "" if len(play) == 4 else play[:-5]
    opening = {"name": openings[previous_move]["name"]}
    index, next_move = check_a_play(openings[previous_move]["moves"], play)
    opening["moves"] = next_move
    opening["play"] = index
    
    # Il faut faire la partie ou le NOUVEAU coup n'existe pas et/ou l'ajouté/l'incrémenter
    filename = Path(f"data/{rating}/{len(moves_played)+1}_moves.json")

    if not filename.exists():
        create_json_file(filename)

    openings = get_json_from_file(filename)
    
    if play not in openings:
        print(f"check_move - MOVE {play} NOT EXIST: CALL API")
        new_opening = get_openings(play=play, rating=rating)
        if "error" in new_opening:
            return {"error": "incorrect_move"}
        add_play_in_json_file(filename, new_opening, play, is_count=True)
    else:
        print(f"check_move - MOVE {play} EXIST!!!")
        increment_play_in_json_file(filename, play)
        
    return opening



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
