import json  
import math

def stats():
    with open('quotes.json', 'r') as f:
        data = json.load(f)
        totalQuotes = len(data["quotes"])
        leaderBoard = {};
        
        for quote in data["quotes"]:
            if quote["auteur"].find("&") != -1:
                auteurs = quote["auteur"].split(" & ");
                for a in auteurs:
                    if not a.lower() in leaderBoard:
                        leaderBoard[a.lower()] = 1;
                    else:
                        leaderBoard[a.lower()] += 1;
                continue;
            if quote["auteur"].find(" en ") != -1:
                auteurs = quote["auteur"].split(" en ");
                for a in auteurs:
                    if not a.lower() in leaderBoard:
                        leaderBoard[a.lower()] = 1;
                    else:
                        leaderBoard[a.lower()] += 1;
                continue;
            if not quote["auteur"].lower() in leaderBoard:
                leaderBoard[quote["auteur"].lower()] = 1;
            else:
                leaderBoard[quote["auteur"].lower()]+= 1;
         
        leaderBoard = dict(sorted(leaderBoard.items(),key=lambda x:x[1],reverse=True))
        totalAuthors = len(leaderBoard);
        colWidth = max(math.log(totalQuotes, 10), len("totalAuthors"));
        cols = 2;
        rows = 2;
        board1 = makeBoard(colWidth, cols, rows);
        board1 = setValueInBoard(board1, "totalQuotes", 0, 0, cols, colWidth);
        board1 = setValueInBoard(board1, f"{totalQuotes}", 1, 0, cols, colWidth);
        board1 = setValueInBoard(board1, "totalAuthors", 0, 1, cols, colWidth);
        board1 = setValueInBoard(board1, f"{totalAuthors}", 1, 1, cols, colWidth);
        print(board1);
        
        colWidth = 10;
        cols = 3;
        rows = 1+len(leaderBoard);
        board2 = makeBoard(colWidth, cols, rows);
        board2 = setValueInBoard(board2, "place", 0, 0, cols, colWidth);
        board2 = setValueInBoard(board2, "auteur", 1, 0, cols, colWidth);
        board2 = setValueInBoard(board2, "quotes", 2, 0, cols, colWidth);
        i = 1;
        for auteur in leaderBoard:
            board2 = setValueInBoard(board2, f"{i}", 0, i, cols, colWidth);
            board2 = setValueInBoard(board2, auteur, 1, i, cols, colWidth);
            board2 = setValueInBoard(board2, f"{leaderBoard[auteur]}", 2, i, cols, colWidth);
            i+=1;
            if (i > 15):
                break;
        print(board2);
    pass
    
def setValueInBoard(board, value, x, y, cols, colWidth):
    label = chr((x)+(y*cols)+ord('{'))
    for i in range(len(value), colWidth):
        value+=" ";
    board = board.replace(label, value);
    return board;
  
def makeBoard(colWidth, cols, rows):
    board = "```\n┌";
    for j in range(cols):
        for i in range(colWidth):
            board += "─";
        if not j == cols-1:
            board += "┬";
    board+= "┐\n";
    for i in range(rows):
        for j in range(cols):
            board += f"│{chr((j)+(i*cols)+ord('{'))}";
        board += "│\n";
        
        if not i == rows-1:           
            board += "├";
            for k in range(cols):
                for l in range(colWidth):
                    board += "─";
                if not k == cols-1:
                    board += "┼";
            board+= "┤\n";
        
    board+= "└";
    for j in range(cols):
        for i in range(colWidth):
            board += "─";
        if not j == cols-1:
            board += "┴";
    board+= "┘\n```";
    return board;
    
#board = makeBoard(5, 5, 3);
#print(board);

stats();