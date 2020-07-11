import numpy

class GameState:
    def __init__(self):
        self.board = numpy.array([["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                                  ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                                  ["--", "--", "--", "--", "--", "--", "--", "--"],
                                  ["--", "--", "--", "--", "--", "--", "--", "--"],
                                  ["--", "--", "--", "--", "--", "--", "--", "--"],
                                  ["--", "--", "--", "--", "--", "--", "--", "--"],
                                  ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                                  ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]])
        self.move_dict = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                          "B": self.getBishopMoves,"Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.kingPos = {"w": (7, 4), "b": (0, 4)}
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassant = ()
        self.currentCastlingRights = castlingRights(True, True, True, True)
        self.castleRightsLog = [castlingRights(self.currentCastlingRights.wks,
                                               self.currentCastlingRights.bks,
                                               self.currentCastlingRights.wqs,
                                               self.currentCastlingRights.bqs)]


    def makeMove(self, move):
        self.board[move.startRow, move.startCol] = "--"
        self.board[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        if move.pieceMoved[1] == "K":
            self.kingPos[move.pieceMoved[0]] = (move.endRow, move.endCol)
        if move.pawnPromote:
            promotePiece = input("Q, R, N, B: ")
            self.board[move.endRow, move.endCol] = move.pieceMoved[0] + promotePiece

        if move.isEnpassant:
            self.board[move.startRow, move.endCol] = "--"
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassant = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassant = ()
        
        if move.isCastle:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow, move.endCol-1] = self.board[move.endRow, move.endCol+1]
                self.board[move.endRow, move.endCol+1] = "--"
            else:
                self.board[move.endRow, move.endCol+1] = self.board[move.endRow, move.endCol-2]
                self.board[move.endRow, move.endCol-2] = "--"
        self.updateCastleRights(move)
        self.castleRightsLog.append(castlingRights(self.currentCastlingRights.wks,
                                                   self.currentCastlingRights.bks,
                                                   self.currentCastlingRights.wqs,
                                                   self.currentCastlingRights.bqs))
        
        self.whiteToMove = not self.whiteToMove
        print(self.board)

    
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow, move.startCol] = move.pieceMoved
            self.board[move.endRow, move.endCol] = move.pieceCaptured
            if move.pieceMoved[1] == "K":
                self.kingPos[move.pieceMoved[0]] = (move.startRow, move.startCol)
            self.whiteToMove = not self.whiteToMove

            if move.isEnpassant:
                self.board[move.endRow, move.endCol] = "--"
                self.board[move.startRow, move.endCol] = move.pieceCaptured
                self.enpassant = (move.endRow, move.endCol)
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassant = ()

            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRights = castlingRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            if move.isCastle:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow, move.endCol+1] = self.board[move.endRow, move.endCol-1]
                    self.board[move.endRow, move.endCol-1] = "--"
                else:
                    self.board[move.endRow, move.endCol-2] = self.board[move.endRow, move.endCol+1]
                    self.board[movve.endRow, move.endCol+1] = "--"
            print(self.board)
    

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False


    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checksAndPins()
        if self.whiteToMove:
            kingRow, kingCol = self.kingPos["w"][0], self.kingPos["w"][1]
        else:
            kingRow, kingCol = self.kingPos["b"][0], self.kingPos["b"][1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow, checkCol]
                validSq = []
                if pieceChecking[1] == "N":
                    validSq = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i)
                        validSq.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSq:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getPossibleMoves()
        if len(moves) == 0:
            inCheck, pin, checks = self.checksAndPins()
            if inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        if self.whiteToMove:
            self.getCastleMoves(self.kingPos["w"][0], self.kingPos["w"][1], moves, "w")
        else:
            self.getCastleMoves(self.kingPos["b"][0], self.kingPos["w"][1], moves, "b")
        return moves

    
    def checksAndPins(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            ecolor, allycolor = "b", "w"
            startRow = self.kingPos["w"][0]
            startCol = self.kingPos["w"][1]
        else:
            ecolor, allycolor = "w", "b"
            startRow = self.kingPos["b"][0]
            startCol = self.kingPos["b"][1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    endpiece = self.board[endRow, endCol]
                    if endpiece[0] == allycolor and endpiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endpiece[0] == ecolor:
                        ptype = endpiece[1]
                        if (0 <= j <= 3 and ptype == "R") or \
                            (4 <= j <= 7 and ptype == "B") or \
                                (i == 1 and ptype == "P" and ((ecolor == "w" and 6 <= j <= 7) or (ecolor == "b" and 4 <= j <= 5))) or \
                                    (ptype == "Q") or (i ==1 and ptype == "K"):
                                    if possiblePin == ():
                                        inCheck = True
                                        checks.append((endRow, endCol, d[0], d[1]))
                                        break
                                    else:
                                        pins.append(possiblePin)
                                        break
                        else:
                            break
                else:
                    break
        directions = ((-2, 1), (-2, -1), (-1, -2), (1, -2), (2, 1), (2, -1), (1, 2), (-1, 2))
        for d in directions:
            endRow = startRow + d[0]
            endCol = startCol + d[1]
        if (0 <= endRow < 8) and (0 <= endCol < 8):
            endpiece = self.board[endRow, endCol]
            if endpiece[0] == ecolor and endpiece[1] == "N":
                inCheck = True
                checks.append((endRow, endCol, d[0], d[1]))
        return inCheck, pins, checks

            

    def getPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                color = self.board[r, c][0]
                if (color == "w" and self.whiteToMove) or (color == "b" and not self.whiteToMove):
                    piece = self.board[r, c][1]
                    self.move_dict[piece](r, c, moves)
        return moves
    

    def getPawnMoves(self, r, c, moves):
        piecePin = False
        pinDir = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePin = True
                pinDir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            ecolor = "b"
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            ecolor = "w"
        pawnPromote = False


        if self.board[r+moveAmount, c] == "--":
            if not piecePin or pinDir == (moveAmount, 0):
                if r+moveAmount == backRow:
                    pawnPromote = True
                moves.append(Move((r, c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromote))
                if r == startRow and self.board[r+2*moveAmount, c] == "--":
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))
        pawnPromote = False
        if c-1 >= 0 and r+moveAmount >= 0:
            if not piecePin or pinDir == (moveAmount, -1):
                if self.board[r+moveAmount, c-1][0] == ecolor:
                    if r+moveAmount == backRow:
                        pawnPromote = True
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board, pawnPromotion=pawnPromote))
                elif (r+moveAmount, c-1) == self.enpassant:
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board, isEnpassant=True))
        pawnPromote = False
        if c+1 < len(self.board) and r+moveAmount >= 0:
            if not piecePin or pinDir == (moveAmount, 1):
                if self.board[r+moveAmount, c+1][0] == ecolor: 
                    if r+moveAmount == backRow:
                        pawnPromote = True
                    moves.append(Move((r, c), (r+moveAmount, c+1), self.board, pawnPromotion=pawnPromote))
                elif (r+moveAmount, c+1) == self.enpassant:
                    moves.append(Move((r, c), (r+moveAmount, c+1), self.board, isEnpassant=True))
            

    def getRookMoves(self, r, c, moves):
        piecePin = False
        pinDir = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePin = True
                pinDir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(pins[i])
                break
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        ecolor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePin or pinDir == d or pinDir == (-d[0], -d[1]):
                        endpiece = self.board[endRow, endCol]
                        if endpiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endpiece[0] == ecolor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
            

    def getKnightMoves(self, r, c, moves):
        piecePin = False
        pinDir = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePin = True
                self.pins.remove(self.pins[i])
                break

        directions = ((-2, 1), (-2, -1), (-1, -2), (1, -2), (2, 1), (2, -1), (1, 2), (-1, 2))
        allycolor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                if not piecePin:
                    endpiece = self.board[endRow, endCol]
                    if not endpiece[0] == allycolor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    def getBishopMoves(self, r, c, moves):
        piecePin = False
        pinDir = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePin = True
                pinDir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(pins[i])
                break
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        ecolor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePin or pinDir == d or pinDir == (-d[0], -d[1]):
                        endpiece = self.board[endRow, endCol]
                        if endpiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endpiece[0] == ecolor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
    

    def getQueenMoves(self, r, c, moves):
        piecePin = False
        pinDir = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePin = True
                pinDir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        ecolor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePin or pinDir == d or pinDir == (-d[0], -d[1]):
                        endpiece = self.board[endRow, endCol]
                        if endpiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endpiece[0] == ecolor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break


    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allycolor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                endpiece = self.board[endRow, endCol]
                if not endpiece[0] == allycolor:
                    self.kingPos[allycolor] = (endRow, endCol)
                    inCheck, pin, checks = self.checksAndPins()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    self.kingPos[allycolor] = (r, c)
    

    def sqUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False


    def getCastleMoves(self, r, c, moves, allycolor):
        if self.sqUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastles(r, c, moves, allycolor)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastles(r, c, moves, allycolor)


    def getKingSideCastles(self, r, c, moves, allycolor):
        if self.board[r, c+1] == "--" and self.board[r, c+2] == "--":
            if (not self.sqUnderAttack(r, c+1)) and (not self.sqUnderAttack(r, c+2)):
                moves.append(Move((r, c), (r, c+2), self.board, isCastle=True))


    def getQueenSideCastles(self, r, c, moves, allycolor):
        if self.board[r, c-1] == "--" and self.board[r, c-2] == "--" and self.board[r, c-3] == "--":
            if (not self.sqUnderAttack(r, c-1)) and (not self.sqUnderAttack(r, c+2)):
                moves.append(Move((r, c), (r, c-2), self.board, isCastle=True))


class castlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    colsToFiles = {v:k for k,v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isEnpassant=False, pawnPromotion=False, isCastle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]
        self.pawnPromote = pawnPromotion
        self.isEnpassant = isEnpassant
        if self.isEnpassant:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        self.isCastle = isCastle
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    

    def getChessNotations(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    

