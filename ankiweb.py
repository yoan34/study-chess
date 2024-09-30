import requests
import json
import os
import math
import chess
import urllib.request
import base64

basicModel = 'Basic'
reversedModel = 'Basic (and reversed card)'

url = 'http://127.0.0.1:8765'
headers = {'Content-Type': 'application/json'}


def create_deck(deck_name):
    result = invoke('createDeck', deck=deck_name)
    print(f"Deck '{deck_name}' créé avec succès. ID: {result}")
    
    
def create_anki_board_card():
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
                openings_names[name]["moves"].append({opening: sorted(values["moves"], key=lambda x: x['white'] * x['averageRating']*(1 + 0.05 * math.log(x['freq'] + 1)), reverse=True)[:2]})

                
    openings_names = dict(sorted(openings_names.items(), key=lambda item: item[1]["count"]))

    result = []
    for key, values in openings_names.items():
        count = values["count"]
        for move in values["moves"]:
            the_move, top_move = next(iter(move.items()))
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
                    "last_play": the_move.split(',')[-1],
                })
                    
    result = sorted(result, key=lambda x: x['play'])
    return result


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        print("duplicate")
    return response['result']

# Fonction pour convertir une image locale en base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


boards = create_anki_board_card()
for board in boards:
    print(board['play'])
    total_moves = len(board['play'].split(','))
    turn_player = 'white' if total_moves % 2 == 0 else 'black'
    try:
        img = encode_image(f"static/board_img/{board['play']}.png")
    except Exception as e:
        print("image not found")
        continue
    create_deck(f"echecs::{turn_player}::{board['name']}::move_{board['total_move']}")
    top_play1 = f"1) freq={board['top_move'][0]['freq']}% {board['top_move'][0]['uci']} W={board['top_move'][0]['white']}% ({board['top_move'][0]['total_games']})"
    if len(board['top_move']) > 1:
        top_play2 = f"2) freq={board['top_move'][1]['freq']}% {board['top_move'][1]['uci']} W={board['top_move'][1]['white']}% ({board['top_move'][1]['total_games']})"
    else:
        top_play2 = "no play 2"
    
    note = {
        "deckName": f"echecs::{turn_player}::{board['name']}::move_{board['total_move']}",  # Nom du deck où tu veux ajouter la carte
        "modelName": "Basic",   # Modèle de la carte

        "fields": {
            "Front": f"last play:{board['last_play']}\n ({board['total_move']})", 
            "Back": f"{top_play1}\n{top_play2}"
        },
        "tags": ["example", "image"],
        "picture": [
            {
                "data": img,
                "filename": f"{board['play']}.png",
                "fields": ["Front"]
            }
        ]
    }
    result= invoke('addNote', note=note)
    print(f"Résultat : {result}")


    

