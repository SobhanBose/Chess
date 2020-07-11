import os
import pygame

import ChessEngine

pygame.init()

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
FPS = 15
PIECES = {}

def loadPieces():
    files = [f for f in os.listdir("images/") if os.path.isfile(os.path.join("images/", f))]
    for f in files:
        PIECES[f[:-4]] = pygame.transform.scale(pygame.image.load(f"images/{f}"), (SQ_SIZE,SQ_SIZE))


def drawBoard(screen):
    global colors
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            pygame.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r, c]
            if piece != "--":
                screen.blit(PIECES[piece], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSq(screen, gs, validMoves, sqSelected):
    s = pygame.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(70)
    s.fill(pygame.Color("red"))
    if gs.sqUnderAttack(gs.kingPos["w"][0], gs.kingPos["w"][1]):
        screen.blit(s, (gs.kingPos["w"][1]*SQ_SIZE, gs.kingPos["w"][0]*SQ_SIZE))
    if gs.sqUnderAttack(gs.kingPos["b"][0], gs.kingPos["b"][1]):
        screen.blit(s, (gs.kingPos["b"][1]*SQ_SIZE, gs.kingPos["b"][0]*SQ_SIZE))

    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r, c][0] == ("w" if gs.whiteToMove else "b"):
            s.fill(pygame.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(pygame.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if move.isEnpassant:
                        s.fill(pygame.Color("green"))
                        screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))
                        s.fill(pygame.Color("yellow"))
                        continue
                    if gs.board[move.endRow, move.endCol][0] == ("b" if gs.whiteToMove else "w"):
                        s.fill(pygame.Color("green"))
                        screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))
                        s.fill(pygame.Color("yellow"))
                        continue
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSq(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def animate(screen, board, move, clock):
    global colors
    dr = move.endRow - move.startRow
    dc = move.endCol - move.startCol
    fpsq = 10
    fcount = (abs(dr) + abs(dc)) * fpsq
    for frame in range(fcount+1):
        r, c = (move.startRow + dr*frame/fcount, move.startCol + dc*frame/fcount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol)%2]
        endSq = pygame.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, endSq)
        if move.pieceCaptured != "--":
            if move.isEnpassant:
                endSq = pygame.Rect(move.endCol*SQ_SIZE, move.startRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
                screen.blit(PIECES[move.pieceCaptured], endSq)
            else:
                screen.blit(PIECES[move.pieceCaptured], endSq)
        screen.blit(PIECES[move.pieceMoved], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(100)


def drawEndScreen(screen, text):
    font = pygame.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, pygame.Color("grey"))
    textLoc = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH//2 - textObject.get_width()//2, HEIGHT//2 - textObject.get_height()//2)
    screen.blit(textObject, textLoc)
    textObject = font.render(text, 0, pygame.Color("black"))
    screen.blit(textObject, textLoc.move(2, 2))
    font = pygame.font.SysFont("Helvetica", 20, True, False)
    textObject = font.render("Press R to restart game!!!", 0, pygame.Color("red"))
    textLoc = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH//2 - textObject.get_width()//2, HEIGHT//2 - textObject.get_height()//2)
    screen.blit(textObject, textLoc.move(0, 35))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadPieces()
    sqSelected = ()
    mouseClick = []
    running = True
    CheckMate = False
    StaleMate = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not CheckMate and not StaleMate:
                    location = pygame.mouse.get_pos()
                    c = location[0]//SQ_SIZE
                    r = location[1]//SQ_SIZE
                    if sqSelected == (r, c):
                        sqSelected = ()
                        mouseClick = []
                    elif gs.board[r, c] != "--" or len(mouseClick) != 0:
                        sqSelected = (r, c)
                        print(sqSelected)
                        mouseClick.append(sqSelected)
                    if len(mouseClick) == 2:
                        move = ChessEngine.Move(mouseClick[0], mouseClick[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                            sqSelected = ()
                            mouseClick = []
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undoMove()
                    moveMade = False
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    mouseClick = []
                if event.key == pygame.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    CheckMate = False
                    StaleMate = False
        
        if moveMade:
            animate(screen, gs.board, gs.moveLog[-1], clock)
            validMoves = gs.getValidMoves()
            moveMade = False
        
        drawGameState(screen, gs, validMoves, sqSelected)

        if len(validMoves) == 0:
                if gs.checkmate:
                    CheckMate = True
                    if gs.whiteToMove:
                        drawEndScreen(screen, "BLACK WINS BY CHECKMATE!!!")
                    if not gs.whiteToMove:
                        drawEndScreen(screen, "WHITE MOVES BY STALEMATE!!!")
                elif gs.stalemate:
                    StaleMate = True
                    drawEndScreen(screen, "STALEMATE!!!")
                    
        clock.tick(FPS)
        pygame.display.flip()

#Driver
if __name__ == '__main__':
    main()
