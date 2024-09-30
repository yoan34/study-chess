async function fetchNextMove(play) {
    try {
        const category = getSelectedCategory();
        const response = await fetch(`http://127.0.0.1:8000/play`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ play, rating: category })
        });
        const data = await response.json();
        console.log("fetchNextMove",data);
        const top_play1 = document.getElementById("top-play1")
        const top_play2 = document.getElementById("top-play2")
        top_play1.textContent = `freq${data.top_play[0].freq}% - (${data.top_play[0].uci}) W=${data.top_play[0].white}% B=${data.top_play[0].black}% ${data.top_play[0].total_games}`
        top_play2.textContent = `freq${data.top_play[1].freq}% - (${data.top_play[1].uci}) W=${data.top_play[1].white}% B=${data.top_play[1].black}% ${data.top_play[1].total_games}`

        if (data.error) {
            let elem = document.getElementById("message").textContent = "Pas assez de moves dans l'API";
            return "error"
        }
        
        if (data.next_play.name !== null) {
            document.getElementById("opening_name").textContent = data.opening_name
        }
        

        if (MOVES.length >= 4) {
            MOVES += ","+data.next_play.uci.replace("-", "")
        } else {
            MOVES += data.next_play.uci.replace("-", "")
        }
        // Appliquer le mouvement sur le plateau
        createComputerLineMove(data.next_play, data.moves)
        computerMove(data.next_play.uci);
        
    } catch (error) {
        console.error('Erreur lors de la récupération des données:', error);
    }
}
async function fetchCorrectMove(play) {
    try {
        const category = getSelectedCategory();
        const response = await fetch(`http://127.0.0.1:8000/check_move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ play, rating: category })
        });
        const data = await response.json();
        console.log("fetchCorrectMove", data);
        console.log(data.play)
        if (data.error) {
            let elem = document.getElementById("message").textContent = "Erreur: Incorrect Move!";

            board.position(previousPosition);
            return "error";
        }
        if (data.name !== null) {
            document.getElementById("opening_name").textContent = data.name.name
        }
        
        if (data.play === -1 || data.play > getSelectedTopPlay()) {
            const modalLine = document.getElementById("modal-line");
            const classMap = [
                "sub_blue",   // i = 0
                "sub_green",  // i = 1
                "sub_green",  // i = 2
                "sub_yellow", // i = 3
                "sub_yellow", // i = 4
                "sub_yellow", // i = 5
                "sub_orange", // i = 6
                "sub_orange", // i = 7
                "sub_orange", // i = 8
                "sub_red",    // i = 9
                "sub_red",    // i = 10
                "sub_red"     // i = 11
            ];
            for (let i = 0; i < data.moves.length; i++) {
                const subElement = document.createElement("div");
                const textBold = data.play-1 === i ? "sub_text_bold": "sub_text_normal";
                subElement.classList.add(textBold, classMap[i], "sub-info");
                
                const moveElem = document.createElement("div");
                moveElem.classList.add("sub-info-text");
                moveElem.textContent = `${i+1}) ${data.moves[i].uci}`
                const moveFreq = document.createElement("div");
                moveFreq.classList.add("sub-info-freq");
                moveFreq.textContent = `frequence=${data.moves[i].freq}%`
                const moveWhite = document.createElement("div");
                moveWhite.classList.add("sub-info-text");
                moveWhite.textContent = `W=${data.moves[i].white}%`;
                const moveDraw = document.createElement("div");
                moveDraw.classList.add("sub-info-text");
                moveDraw.textContent = `D=${data.moves[i].draws}%`;
                const moveBlack = document.createElement("div");
                moveBlack.classList.add("sub-info-text");
                moveBlack.textContent = `B=${data.moves[i].black}%`;
                const moveRating = document.createElement("div");
                moveRating.classList.add("sub-info-avg-elo");
                moveRating.textContent = `${data.moves[i].averageRating} avg elo `;
                const moveGame = document.createElement("div");
                moveGame.classList.add("sub-info-count-game");
                moveGame.textContent = `${data.moves[i].total_games} games`;
                subElement.appendChild(moveElem);
                subElement.appendChild(moveFreq);
                subElement.appendChild(moveWhite);
                subElement.appendChild(moveDraw);
                subElement.appendChild(moveBlack);
                subElement.appendChild(moveRating);
                subElement.appendChild(moveGame);

                modalLine.appendChild(subElement);
            }
            showModal()
            
            return "error"
        } else {
            //get the move
            console.log("before createplauerlinemove: ", data.play, data.play-1)
            let player_move = data.moves[data.play-1]

            
            createPlayerLineMove(player_move, data.moves, data.play-1)
            playerMove(player_move.uci);
        }
        
        
    } catch (error) {
        console.error('Erreur lors de la récupération des données:', error);
    }
}