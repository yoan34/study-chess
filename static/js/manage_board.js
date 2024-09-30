const playerMove = (move) => {
    console.log("player Mouvement reçu :", move);
    const moveCleaned = move.replace("-", "");
    let currentPosition = board.position();

    let sourceSquare = moveCleaned.slice(0, 2);
    let targetSquare = moveCleaned.slice(2, 4);

    let piece = currentPosition[targetSquare];

    if (piece === 'wK' || piece === 'bK') {  // Si la pièce est un roi (wK = roi blanc, bK = roi noir)
        const isKingSideCastle = (sourceSquare === 'e1' && targetSquare === 'h1') || (sourceSquare === 'e8' && targetSquare === 'h8');
        const isQueenSideCastle = (sourceSquare === 'e1' && targetSquare === 'a1') || (sourceSquare === 'e8' && targetSquare === 'a8');

        if (isKingSideCastle) {
            console.log("Petit roque détecté");
            if (sourceSquare === "e8") {
                board.move(`${targetSquare}-g8`);
                updateBoardPosition({f8: 'bR'})
            }
            if (sourceSquare === "e1") {
                board.move(`${targetSquare}-g1`);
                updateBoardPosition({f1: 'wR'})
            }
            
        } else if (isQueenSideCastle) {
            console.log("Grand roque détecté");
            if (sourceSquare === "e8") {
                board.move(`${targetSquare}-c8`);
                updateBoardPosition({d8: 'bR'})
            }
            if (sourceSquare === "e1") {
                board.move(`${targetSquare}-c1`);
                updateBoardPosition({d1: 'wR'})
            }
        } else {
            console.log("move roi standard")
            board.move(move);
        }
    } else {
        console.log("here")
        board.move(move);
    }
}

const computerMove = (move) => {
    console.log(" computer Mouvement reçu:", move);
    const moveCleaned = move.replace("-", "");
    let currentPosition = board.position();

    let sourceSquare = moveCleaned.slice(0, 2);
    let targetSquare = moveCleaned.slice(2, 4);

    console.log("position plateau", currentPosition)
    let piece = currentPosition[sourceSquare];

    console.log("Case source:", sourceSquare);
    console.log("Pièce sur la case target:", piece);

    if (piece === 'wK' || piece === 'bK') {  // Si la pièce est un roi (wK = roi blanc, bK = roi noir)
        const isKingSideCastle = (sourceSquare === 'e1' && targetSquare === 'g1') || (sourceSquare === 'e1' && targetSquare === 'h1') || (sourceSquare === 'e8' && targetSquare === 'g8') || (sourceSquare === 'e8' && targetSquare === 'h8');
        const isQueenSideCastle = (sourceSquare === 'e1' && targetSquare === 'c1') || (sourceSquare === 'e1' && targetSquare === 'a1') || (sourceSquare === 'e8' && targetSquare === 'c8') || (sourceSquare === 'e8' && targetSquare === 'a8');

        if (isKingSideCastle) {
            console.log("Petit roque détecté");
            if (piece === 'wK') {
                board.move('e1-g1', 'h1-f1');
            }
            if (piece === 'bK') {
                board.move('e8-g8', 'h8-f8')
            }
        
        } else if (isQueenSideCastle) {
            // Grand roque: Roi se déplace de e1 à c1 (blanc) ou e8 à c8 (noir)
            console.log("Grand roque détecté");
            if (piece === 'wK') {
               board.move('e1-c1','a1-d1'); 
            }
            if (piece === 'bK') {
                board.move('e8-c8', 'a8-d8')
            }
            
        } else {
            console.log("move roi standard")
            board.move(move);
        }
    } else {
        console.log("here")
        board.move(move);
    }
}

const updateBoardPosition = (newPosition) => {
    let currentPosition = board.position();
    const updatedPosition = { ...currentPosition, ...newPosition };
    board.position(updatedPosition);
};

const startGame = async (colorChoice) => {
    console.log("Color chosen:", colorChoice);
    document.getElementById('board').style.display = 'block';
    document.getElementById("opening_name").style.display = "block";
    document.getElementById('form_start_game').style.display = 'none';
    document.getElementById('menu_btn').style.display = 'inline';
    document.getElementById('restart_btn').style.display = 'inline';
    board = Chessboard('board', {
        draggable: true,
        position: 'start',
        orientation: colorChoice,
        onDrop: onDrop,
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
    });
    if (colorChoice === "black") {
        console.log("FIRST MOVE COMPUTER WHITE")
        await fetchNextMove("")
    }
}

async function onDrop(source, target) {
    previousPosition = board.position();
    if (MOVES.length === 0) {
        MOVES = source + target
    } else {
        MOVES += "," + source + target
    }
    
    console.log("MOVES: ", MOVES)

    const result = await fetchCorrectMove(MOVES)
    if (result !== "error") {
        
        fetchNextMove(MOVES)
    } else {
        MOVES = MOVES.slice(0, -5)
    }
}