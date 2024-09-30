import random
import math
import json
import requests
from pathlib import Path
from time import sleep


def create_next_play_in_json_file(play: str, rating: str, next_play: dict):
    if not play:
        play = next_play['uci'].replace("-", "")
    else:
        play = f"{play},{next_play['uci'].replace('-', '')}"
    moves_played = play.split(',')
    if len(moves_played) == 1 and not moves_played[0]:
        moves_played = []
        
    filename = Path(f"data/{rating}/{len(moves_played)}_moves.json")
    if not filename.exists():
        create_json_file(filename)

    openings = get_json_from_file(filename)
    if play not in openings:
        print(f"create_next_play_in_json_file - MOVE {play} NOT EXIST: CALL API")
        opening = get_openings(play=play, rating=rating)
        add_play_in_json_file(filename, opening, play)
    else:
        print(f"create_next_play_in_json_file - MOVE {play} EXIST!!!")

def increment_play_in_json_file(filename: Path, play: str):
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            openings = json.load(f)
        except Exception as e:
            print(f"Error in 'add_play_in_json_file': {e}")
    openings[play]["count"] += 1

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(openings, f, ensure_ascii=False, indent=4)

def add_play_in_json_file(filename: Path, openings: dict, play: str, is_count: bool = False):
    print(f"ADDING PLAY: {play}")
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error in 'add_play_in_json_file': {e}")
    data[play] = openings
    if is_count:
        data[play]["count"] += 1

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_json_file(filename: Path):
    print(f"creating file: {filename.name}")
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.touch(exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

def get_json_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Le fichier {filename} n'existe pas.")
    except json.JSONDecodeError:
        print(f"Le fichier {filename} contient du JSON invalide.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier {filename}: {e}")

def choice_a_play(openings: dict, play: str):
    moves_data = openings[play].get("moves", [])
    moves = [move["uci"] for move in moves_data]
    weights = [move["freq"] for move in moves_data]
    if not moves or not weights:
        return {"error": "no more line"}

    selected_move = random.choices(moves, weights=weights, k=1)[0]
    selected_move_uci = random.choices(moves, weights=weights, k=1)[0]
    selected_move = next(move for move in moves_data if move["uci"] == selected_move_uci)
    move = f"{selected_move_uci[:2]}-{selected_move_uci[2:]}"
    selected_move["uci"] = move
    selected_move["name"] = openings[play]["name"]
    return selected_move


def get_top_2_move(moves: list, play: str):
    print(f"MOVES in 2 play:{moves}   play={play}")
    play=play.replace('-', ',')
    play = play.split(',')
    if len(play) % 2 == 1:
        player = "black"
    else:
        player = "white"
    play = play[-1]
    print(f"PLAY: {play} player:{player}")
    if player == 'white':
        sorted_moves = sorted(moves, key=lambda x: x['white'] * x['averageRating']*(1 + 0.05 * math.log(x['freq'] + 1)), reverse=True)
    elif player == 'black':
        sorted_moves = sorted(moves, key=lambda x: x['black'] * x['averageRating']*(1 + 0.05 * math.log(x['freq'] + 1)), reverse=True)
    for move in sorted_moves:
        uci = move['uci']
        move['uci'] = uci[:2] + "-" + uci[2:]
        
    print(f"top22222222222222 move:  {sorted_moves[0]['uci']} {sorted_moves[1]['uci']}")
    return sorted_moves[:2]
        
        
def check_a_play(moves: list, play: str):
    play = play.split(',')
    if len(play) % 2 == 0:
        player = "black"
    else:
        player = "white"
    play = play[-1]
    print(f"PLAY: {play} player:{player}")
    if player == 'white':
        sorted_moves = sorted(moves, key=lambda x: x['white'] * x['averageRating']*(1 + 0.05 * math.log(x['freq'] + 1)), reverse=True)
    elif player == 'black':
        sorted_moves = sorted(moves, key=lambda x: x['black'] * x['averageRating']*(1 + 0.05 * math.log(x['freq'] + 1)), reverse=True)
        
    play_index = next((index for index, move in enumerate(sorted_moves) if move['uci'] == play), None)
    if play_index is None:
        play_index = -1
    else:
        play_index += 1
    print(f"{play_index=}")
    print(sorted_moves)
    for move in sorted_moves:
        uci = move['uci']
        move['uci'] = uci[:2] + "-" + uci[2:]
    return play_index, sorted_moves

def extract_data(data):
    opening = {"moves": [], "count": 0}
    total_games = sum(sum([move["white"], move["black"], move["draws"]]) for move in data["moves"])

    opening["total_game_move"] = total_games
    opening["name"] = data.get("opening", None)

    for move in data["moves"]:
        total = move["black"] + move["white"] + move["draws"]
        winrate_white = move["white"] / total * 100
        winrate_black = move["black"] / total * 100
        draw_rate = move["draws"] / total * 100
        freq_move = total / total_games * 100
        line = {
            "total_games": total,
            "freq": round(freq_move, 2),
            "white": round(winrate_white, 2),
            "black": round(winrate_black, 2),
            "draws": round(draw_rate, 2),
            "uci": move["uci"],
            "averageRating": move["averageRating"]
        }
        opening["moves"].append(line)

    return opening

def get_openings(play: str, rating: str, move: int = 12, retries: int = 3):
    url = "https://explorer.lichess.ovh/lichess"
    params = {
        "play": play,
        "ratings": rating,
        "moves": move
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            status_code = response.status_code
            response.raise_for_status()  # Vérifie les erreurs HTTP
            return extract_data(response.json())
        
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: code={status_code} {http_err} - Attempt {attempt + 1} of {retries}")
            print(f"MOVE NOT CORRECT PROBABILITY")
            return {"error": "incorrect_move"}
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: code={status_code}{conn_err} - Attempt {attempt + 1} of {retries}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: code={status_code}{timeout_err} - Attempt {attempt + 1} of {retries}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error during GET openings: code={status_code}{req_err} - Attempt {attempt + 1} of {retries}")
        except ValueError as val_err:
            print(f"JSON decoding failed: code={status_code}{val_err} - Attempt {attempt + 1} of {retries}")

        if attempt < retries - 1:  # Attendre seulement si ce n'est pas le dernier essai
            print("Waiting 5s before retrying...")
            sleep(5)

    # Si toutes les tentatives échouent
    print(f"Failed to get data after {retries} attempts.")
    return None



def get_correct_opening_name(play: str, rating: str, moves_played: int):
    
    filename = Path(f"data/{rating}/{moves_played}_moves.json")
    print(f"{play=}   {moves_played=}  {filename=}")
    if not filename.exists():
        return
    openings = get_json_from_file(filename)
    if play not in openings:
        print(f"not play={play} in file....")
        return
    return openings[play]["name"]["name"]
    

if __name__ == "__main__":
    response = get_openings(play="e2e4,e7e5", rating="0,1400")    # 407.882.729
    print(response)
    top_2_move = get_top_2_move(response['moves'], "e2e4,e7e5")
    for move in top_2_move:
        print(move)
