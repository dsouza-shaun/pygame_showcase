import pygame
import math
import random
import config

#Class for the game input keys and their status
class GameKeyInput:

    def __init__(self):
        self.xNav = self.KeyName('idle',False) # 'left' 'right'
        self.down = self.KeyName('idle',False) # 'pressed' 'released'
        self.rotate = self.KeyName('idle',False) # 'pressed' //KEY UP
        self.cRotate = self.KeyName('idle',False) # 'pressed' //KEY Z
        self.enter = self.KeyName('idle',False) # 'pressed' //KEY Enter
        self.pause = self.KeyName('idle',False) # 'pressed' //KEY P
        self.restart = self.KeyName('idle',False) # 'pressed' //KEY R

    class KeyName:

        def __init__(self, init_status, init_trig):
            self.status = init_status
            self.trig = init_trig


#Class for the game's timing events
class GameClock:

    def __init__(self):
        self.frameTick = 0 #The main clock tick of the game, increments at each frame (1/60 secs, 60 fps)
        self.pausedMoment = 0
        self.move = self.TimingType(config.MOVE_PERIOD_INIT) #Drop and move(right and left) timing object
        self.fall = self.TimingType(config.levelSpeeds[config.STARTING_LEVEL]) #Free fall timing object
        self.clearAniStart = 0

    class TimingType:

        def __init__(self, frame_period):
            self.preFrame = 0
            self.framePeriod = frame_period

        def check(self, frame_tick):
            if frame_tick - self.preFrame > self.framePeriod - 1:
                self.preFrame = frame_tick
                return True
            return False

    def pause(self):
        self.pausedMoment = self.frameTick

    def unpause(self):
        self.frameTick = self.pausedMoment

    def restart(self):
        self.frameTick = 0
        self.pausedMoment = 0
        self.move = self.TimingType(config.MOVE_PERIOD_INIT)
        self.fall = self.TimingType(config.levelSpeeds[config.STARTING_LEVEL])
        self.clearAniStart = 0

    def update(self):
        self.frameTick = self.frameTick + 1


# Class for all the game mechanics, visuals and events
class MainBoard:

    def __init__(self, block_size, x_pos, y_pos, col_num, row_num, board_line_width, block_line_width, score_board_width):

        #Size and position initiations
        self.blockSize = block_size
        self.xPos = x_pos
        self.yPos = y_pos
        self.colNum = col_num
        self.rowNum = row_num
        self.boardLineWidth = board_line_width
        self.blockLineWidth = block_line_width
        self.scoreBoardWidth = score_board_width

        #Matrix that contains all the existing blocks in the game board, except the moving piece
        self.blockMat = [['empty'] * col_num for i in range(row_num)]

        self.piece = MovingPiece(col_num, row_num, 'uncreated')

        self.lineClearStatus = 'idle' # 'clearRunning' 'clearFin'
        self.clearedLines = [-1,-1,-1,-1]

        self.gameStatus = 'firstStart' # 'running' 'gameOver'
        self.gamePause = False
        self.nextPieces = ['I','I']

        self.score = 0
        self.level = config.STARTING_LEVEL
        self.lines = 0

    def restart(self):
        self.blockMat = [['empty'] * self.colNum for i in range(self.rowNum)]

        self.piece = MovingPiece(self.colNum,self.rowNum,'uncreated')

        self.lineClearStatus = 'idle'
        self.clearedLines = [-1,-1,-1,-1]
        config.gameClock.fall.preFrame = config.gameClock.frameTick
        self.generate_next_two_pieces()
        self.gameStatus = 'running'
        self.gamePause = False

        self.score = 0
        self.level = config.STARTING_LEVEL
        self.lines = 0

        config.gameClock.restart()

    def erase_block(self, x_ref, y_ref, row, col):
        pygame.draw.rect(config.gameDisplay, config.BLACK, [x_ref + (col * self.blockSize), y_ref + (row * self.blockSize), self.blockSize, self.blockSize], 0)

    def draw_block(self, x_ref, y_ref, row, col, color):
        pygame.draw.rect(config.gameDisplay, config.BLACK, [x_ref + (col * self.blockSize), y_ref + (row * self.blockSize), self.blockSize, self.blockLineWidth], 0)
        pygame.draw.rect(config.gameDisplay, config.BLACK, [x_ref + (col * self.blockSize) + self.blockSize - self.blockLineWidth, y_ref + (row * self.blockSize), self.blockLineWidth, self.blockSize], 0)
        pygame.draw.rect(config.gameDisplay, config.BLACK, [x_ref + (col * self.blockSize), y_ref + (row * self.blockSize), self.blockLineWidth, self.blockSize], 0)
        pygame.draw.rect(config.gameDisplay, config.BLACK, [x_ref + (col * self.blockSize), y_ref + (row * self.blockSize) + self.blockSize - self.blockLineWidth, self.blockSize, self.blockLineWidth], 0)

        pygame.draw.rect(config.gameDisplay, color, [x_ref + (col * self.blockSize) + self.blockLineWidth, y_ref + (row * self.blockSize) + self.blockLineWidth, self.blockSize - (2 * self.blockLineWidth), self.blockSize - (2 * self.blockLineWidth)], 0)

    def draw_gameboard_border(self):
        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,(self.blockSize*self.colNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth),self.boardLineWidth],0)
        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.boardLineWidth,(self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)],0)
        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.boardLineWidth,(self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)],0)
        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth,self.yPos+(self.blockSize*self.rowNum)+self.blockLineWidth,(self.blockSize*self.colNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth),self.boardLineWidth],0)

    def draw_gameboard_content(self):

        if self.gameStatus == 'firstStart':

            title_text = config.fontTitle.render('TETRIS', False, config.WHITE)
            config.gameDisplay.blit(title_text,(self.xPos+1.55*self.blockSize,self.yPos+8*self.blockSize))

            version_text = config.fontVersion.render('v 1.0', False, config.WHITE)
            config.gameDisplay.blit(version_text,(self.xPos+7.2*self.blockSize,self.yPos+11.5*self.blockSize))

        else:

            for row in range(0,self.rowNum):
                for col in range(0,self.colNum):
                    if self.blockMat[row][col] == 'empty':
                        self.erase_block(self.xPos, self.yPos, row, col)
                    else:
                        self.draw_block(self.xPos, self.yPos, row, col, config.blockColors[self.blockMat[row][col]])

            if self.piece.status == 'moving':
                for i in range(0,4):
                    self.draw_block(self.xPos, self.yPos, self.piece.blocks[i].currentPos.row, self.piece.blocks[i].currentPos.col, config.blockColors[self.piece.type])

            if self.gamePause:
                pygame.draw.rect(config.gameDisplay, config.DARK_GRAY, [self.xPos+1*self.blockSize,self.yPos+8*self.blockSize,8*self.blockSize,4*self.blockSize],0)
                pause_text = config.fontPAUSE.render('PAUSE', False, config.BLACK)
                config.gameDisplay.blit(pause_text,(self.xPos+1.65*self.blockSize,self.yPos+8*self.blockSize))

            if self.gameStatus == 'gameOver':
                pygame.draw.rect(config.gameDisplay, config.LIGHT_GRAY, [self.xPos+1*self.blockSize,self.yPos+8*self.blockSize,8*self.blockSize,8*self.blockSize],0)
                game_over_text0 = config.fontGAMEOVER.render('GAME', False, config.BLACK)
                config.gameDisplay.blit(game_over_text0,(self.xPos+2.2*self.blockSize,self.yPos+8*self.blockSize))
                game_over_text1 = config.fontGAMEOVER.render('OVER', False, config.BLACK)
                config.gameDisplay.blit(game_over_text1,(self.xPos+2.35*self.blockSize,self.yPos+12*self.blockSize))


    def draw_scoreboard_border(self):
        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.scoreBoardWidth+self.boardLineWidth,self.boardLineWidth],0)
        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.boardLineWidth+self.blockLineWidth+self.scoreBoardWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.boardLineWidth,(self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)],0)
        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth,self.yPos+(self.blockSize*self.rowNum)+self.blockLineWidth,self.scoreBoardWidth+self.boardLineWidth,self.boardLineWidth],0)

    def draw_scoreboard_content(self):

        x_pos_ref = self.xPos+(self.blockSize*self.colNum)+self.boardLineWidth+self.blockLineWidth
        y_pos_ref = self.yPos
        y_last_block = self.yPos+(self.blockSize*self.rowNum)

        if self.gameStatus == 'running':
            next_piece_text = config.fontSB.render('next:', False, config.TEXT_COLOR)
            config.gameDisplay.blit(next_piece_text,(x_pos_ref+self.blockSize,self.yPos))

            blocks = [[0,0],[0,0],[0,0],[0,0]]
            origin = [0,0]
            for i in range(0,4):
                blocks[i][config.ROW] = origin[config.ROW] + config.pieceDefs[self.nextPieces[1]][i][config.ROW]
                blocks[i][config.COL] = origin[config.COL] + config.pieceDefs[self.nextPieces[1]][i][config.COL]

                if self.nextPieces[1] == 'O':
                    self.draw_block(x_pos_ref + 0.5 * self.blockSize, y_pos_ref + 2.25 * self.blockSize, blocks[i][config.ROW], blocks[i][config.COL], config.blockColors[self.nextPieces[1]])
                elif self.nextPieces[1] == 'I':
                    self.draw_block(x_pos_ref + 0.5 * self.blockSize, y_pos_ref + 1.65 * self.blockSize, blocks[i][config.ROW], blocks[i][config.COL], config.blockColors[self.nextPieces[1]])
                else:
                    self.draw_block(x_pos_ref + 1 * self.blockSize, y_pos_ref + 2.25 * self.blockSize, blocks[i][config.ROW], blocks[i][config.COL], config.blockColors[self.nextPieces[1]])

            if not self.gamePause:
                pause_text = config.fontSmall.render('P -> pause', False, config.WHITE)
                config.gameDisplay.blit(pause_text,(x_pos_ref+1*self.blockSize,y_last_block-15*self.blockSize))
            else:
                unpause_text = config.fontSmall.render('P -> unpause', False, self.white_sine_animation())
                config.gameDisplay.blit(unpause_text,(x_pos_ref+1*self.blockSize,y_last_block-15*self.blockSize))

            restart_text = config.fontSmall.render('R -> restart', False, config.WHITE)
            config.gameDisplay.blit(restart_text,(x_pos_ref+1*self.blockSize,y_last_block-14*self.blockSize))

        else:

            y_block_ref = 0.3
            text0 = config.fontSB.render('press', False, self.white_sine_animation())
            config.gameDisplay.blit(text0,(x_pos_ref+self.blockSize,self.yPos+y_block_ref*self.blockSize))
            text1 = config.fontSB.render('enter', False, self.white_sine_animation())
            config.gameDisplay.blit(text1,(x_pos_ref+self.blockSize,self.yPos+(y_block_ref+1.5)*self.blockSize))
            text2 = config.fontSB.render('to', False, self.white_sine_animation())
            config.gameDisplay.blit(text2,(x_pos_ref+self.blockSize,self.yPos+(y_block_ref+3)*self.blockSize))
            if self.gameStatus == 'firstStart':
                text3 = config.fontSB.render('start', False, self.white_sine_animation())
                config.gameDisplay.blit(text3,(x_pos_ref+self.blockSize,self.yPos+(y_block_ref+4.5)*self.blockSize))
            else:
                text3 = config.fontSB.render('restart', False, self.white_sine_animation())
                config.gameDisplay.blit(text3,(x_pos_ref+self.blockSize,self.yPos+(y_block_ref+4.5)*self.blockSize))

        pygame.draw.rect(config.gameDisplay, config.BORDER_COLOR, [x_pos_ref,y_last_block-12.5*self.blockSize,self.scoreBoardWidth,self.boardLineWidth],0)

        score_text = config.fontSB.render('score:', False, config.TEXT_COLOR)
        config.gameDisplay.blit(score_text,(x_pos_ref+self.blockSize,y_last_block-12*self.blockSize))
        score_num_text = config.fontSB.render(str(self.score), False, config.NUM_COLOR)
        config.gameDisplay.blit(score_num_text,(x_pos_ref+self.blockSize,y_last_block-10*self.blockSize))

        level_text = config.fontSB.render('level:', False, config.TEXT_COLOR)
        config.gameDisplay.blit(level_text,(x_pos_ref+self.blockSize,y_last_block-8*self.blockSize))
        level_num_text = config.fontSB.render(str(self.level), False, config.NUM_COLOR)
        config.gameDisplay.blit(level_num_text,(x_pos_ref+self.blockSize,y_last_block-6*self.blockSize))

        lines_text = config.fontSB.render('lines:', False, config.TEXT_COLOR)
        config.gameDisplay.blit(lines_text,(x_pos_ref+self.blockSize,y_last_block-4*self.blockSize))
        lines_num_text = config.fontSB.render(str(self.lines), False, config.NUM_COLOR)
        config.gameDisplay.blit(lines_num_text,(x_pos_ref+self.blockSize,y_last_block-2*self.blockSize))

    # All the screen drawings occurs in this function, called at each game loop iteration
    def draw(self):

        self.draw_gameboard_border()
        self.draw_scoreboard_border()

        self.draw_gameboard_content()
        self.draw_scoreboard_content()

    @staticmethod
    def white_sine_animation():

        sine = math.floor(255 * math.fabs(math.sin(2*math.pi*(config.gameClock.frameTick/(config.SINE_ANI_PERIOD*2)))))
        sine_effect = [sine,sine,sine]
        return sine_effect

    def line_clear_animation(self):

        clear_ani_stage = math.floor((config.gameClock.frameTick - config.gameClock.clearAniStart)/config.CLEAR_ANI_PERIOD)
        half_col = math.floor(self.colNum/2)
        if clear_ani_stage < half_col:
            for i in range(0,4):
                if self.clearedLines[i] >= 0:
                    self.blockMat[self.clearedLines[i]][half_col + clear_ani_stage] = 'empty'
                    self.blockMat[self.clearedLines[i]][(half_col-1)-clear_ani_stage] = 'empty'
        else:
            self.lineClearStatus = 'cleared'

    def drop_free_blocks(self): #Drops down the floating blocks after line clears occur

        for cLIndex in range(0,4):
            if self.clearedLines[cLIndex] >= 0:
                for rowIndex in range(self.clearedLines[cLIndex],0,-1):
                    for colIndex in range(0,self.colNum):
                        self.blockMat[rowIndex+cLIndex][colIndex] = self.blockMat[rowIndex+cLIndex-1][colIndex]

                for colIndex in range(0,self.colNum):
                    self.blockMat[0][colIndex] = 'empty'

    def get_complete_lines(self): #Returns index list(length of 4) of cleared lines(-1 if not assigned as cleared line)

        cleared_lines = [-1,-1,-1,-1]
        c_l_index = -1
        row_index = self.rowNum - 1

        while row_index >= 0:
            for colIndex in range(0,self.colNum):
                if self.blockMat[row_index][colIndex] == 'empty':
                    row_index = row_index - 1
                    break
                if colIndex == self.colNum - 1:
                    c_l_index = c_l_index + 1
                    cleared_lines[c_l_index] = row_index
                    row_index = row_index - 1

        if c_l_index >= 0:
            config.gameClock.clearAniStart = config.gameClock.frameTick
            self.lineClearStatus = 'clearRunning'
        else:
            self.prepare_next_spawn()

        return cleared_lines

    def prepare_next_spawn(self):
        self.generate_next_piece()
        self.lineClearStatus = 'idle'
        self.piece.status = 'uncreated'

    def generate_next_two_pieces(self):
        self.nextPieces[0] = config.pieceNames[random.randint(0,6)]
        self.nextPieces[1] = config.pieceNames[random.randint(0,6)]
        self.piece.type = self.nextPieces[0]

    def generate_next_piece(self):
        self.nextPieces[0] = self.nextPieces[1]
        self.nextPieces[1] = config.pieceNames[random.randint(0,6)]
        self.piece.type = self.nextPieces[0]

    def check_and_apply_game_over(self):
        if self.piece.gameOverCondition:
            self.gameStatus = 'gameOver'
            for i in range(0,4):
                if self.piece.blocks[i].currentPos.row >= 0 and self.piece.blocks[i].currentPos.col >= 0:
                    self.blockMat[self.piece.blocks[i].currentPos.row][self.piece.blocks[i].currentPos.col] = self.piece.type

    def update_scores(self):

        cleared_lines_num = 0
        for i in range(0,4):
            if self.clearedLines[i] > -1:
                cleared_lines_num = cleared_lines_num + 1

        self.score = self.score + (self.level+1)*config.baseLinePoints[cleared_lines_num] + self.piece.dropScore
        if self.score > 999999:
            self.score = 999999
        self.lines = self.lines + cleared_lines_num
        self.level = config.STARTING_LEVEL + math.floor(self.lines/10)
        if self.level > 99:
            self.level = 99

    def update_speed(self):

        if self.level < 29:
            config.gameClock.fall.framePeriod = config.levelSpeeds[self.level]
        else:
            config.gameClock.fall.framePeriod = 1

        if config.gameClock.fall.framePeriod < 4:
            config.gameClock.fall.framePeriod = config.gameClock.move.framePeriod

    # All the game events and mechanics are placed in this function, called at each game loop iteration
    def game_action(self):

        if self.gameStatus == 'firstStart':
            if config.key.enter.status == 'pressed':
                self.restart()

        elif self.gameStatus == 'running':

            if config.key.restart.trig:
                self.restart()
                config.key.restart.trig = False

            if not self.gamePause:

                self.piece.move(self.blockMat)
                self.check_and_apply_game_over()

                if config.key.pause.trig:
                    config.gameClock.pause()
                    self.gamePause = True
                    config.key.pause.trig = False

                if self.gameStatus != 'gameOver':
                    if self.piece.status == 'moving':
                        if config.key.rotate.trig:
                            self.piece.rotate('CW')
                            config.key.rotate.trig = False

                        if config.key.cRotate.trig:
                            self.piece.rotate('cCW')
                            config.key.cRotate.trig = False

                    elif self.piece.status == 'collided':
                        if self.lineClearStatus == 'idle':
                            for i in range(0,4):
                                self.blockMat[self.piece.blocks[i].currentPos.row][self.piece.blocks[i].currentPos.col] = self.piece.type
                            self.clearedLines = self.get_complete_lines()
                            self.update_scores()
                            self.update_speed()
                        elif self.lineClearStatus == 'clearRunning':
                            self.line_clear_animation()
                        else: # 'clearFin'
                            self.drop_free_blocks()
                            self.prepare_next_spawn()

            else: # self.gamePause = True
                if config.key.pause.trig:
                    config.gameClock.unpause()
                    self.gamePause = False
                    config.key.pause.trig = False

        else: # 'gameOver'
            if config.key.enter.status == 'pressed':
                self.restart()

# Class for all the definitions of current moving piece
class MovingPiece:

    def __init__(self, col_num, row_num, status):

        self.colNum = col_num
        self.rowNum = row_num

        self.blockMat = [['empty'] * col_num for i in range(row_num)]

        self.blocks = []
        for i in range(0,4):
            self.blocks.append(MovingBlock())

        self.currentDef = [[0] * 2 for i in range(4)]
        self.status = status # 'uncreated' 'moving' 'collided'
        self.type = 'I' # 'O', 'T', 'S', 'Z', 'J', 'L'

        self.gameOverCondition = False

        self.dropScore = 0
        self.lastMoveType = 'noMove'

    def apply_next_move(self):
        for i in range(0,4):
            self.blocks[i].currentPos.col = self.blocks[i].nextPos.col
            self.blocks[i].currentPos.row = self.blocks[i].nextPos.row

    def apply_fast_move(self):

        if config.gameClock.move.check(config.gameClock.frameTick):
            if self.lastMoveType == 'downRight' or self.lastMoveType == 'downLeft' or self.lastMoveType == 'down':
                self.dropScore = self.dropScore + 1
            self.apply_next_move()

    def slow_move_action(self):

        if config.gameClock.fall.check(config.gameClock.frameTick):
            if self.mov_collision_check('down'):
                self.create_next_move('noMove')
                self.status = 'collided'
            else:
                self.create_next_move('down')
                self.apply_next_move()

    def create_next_move(self, move_type):

        self.lastMoveType = move_type

        for i in range(0,4):
            self.blocks[i].nextPos.row = self.blocks[i].currentPos.row + config.directions[move_type][config.ROW]
            self.blocks[i].nextPos.col = self.blocks[i].currentPos.col + config.directions[move_type][config.COL]

    def mov_collision_check_block(self, dir_type, block_index):
        if dir_type == 'down':
            if (self.blocks[block_index].currentPos.row + 1 > self.rowNum - 1) or self.blockMat[self.blocks[block_index].currentPos.row + config.directions[dir_type][config.ROW]][self.blocks[block_index].currentPos.col + config.directions[dir_type][config.COL]] != 'empty':
                return True
        else:
            if ( ((config.directions[dir_type][config.COL]) * (self.blocks[block_index].currentPos.col + config.directions[dir_type][config.COL])) > (((self.colNum - 1) + (config.directions[dir_type][config.COL]) * (self.colNum - 1)) / 2) or
                    self.blockMat[self.blocks[block_index].currentPos.row + config.directions[dir_type][config.ROW]][self.blocks[block_index].currentPos.col + config.directions[dir_type][config.COL]] != 'empty'):
                return True
        return False

    def mov_collision_check(self, dir_type): #Collision check for next move
        for i in range(0,4):
            if self.mov_collision_check_block(dir_type, i):
                return True
        return False

    def rot_collision_check_block(self, block_coor):
        if block_coor[config.ROW]>self.rowNum-1 or block_coor[config.ROW]<0 or block_coor[config.COL]>self.colNum-1 or block_coor[config.COL]<0 or self.blockMat[block_coor[config.ROW]][block_coor[config.COL]] != 'empty':
            return True
        return False

    def rot_collision_check(self, block_coor_list): #Collision check for rotation
        for i in range(0,4):
            if self.rot_collision_check_block(block_coor_list[i]):
                return True
        return False

    def spawn_collision_check(self, origin): #Collision check for spawn

        for i in range(0,4):
            spawn_row = origin[config.ROW] + config.pieceDefs[self.type][i][config.ROW]
            spawn_col = origin[config.COL] + config.pieceDefs[self.type][i][config.COL]
            if spawn_row >= 0 and spawn_col >= 0:
                if self.blockMat[spawn_row][spawn_col] != 'empty':
                    return True
        return False

    def find_origin(self):

        origin = [0,0]
        origin[config.ROW] = self.blocks[0].currentPos.row - self.currentDef[0][config.ROW]
        origin[config.COL] = self.blocks[0].currentPos.col - self.currentDef[0][config.COL]
        return origin

    def rotate(self,rotationType):

        if self.type != 'O':
            temp_blocks = [[0] * 2 for i in range(4)]
            origin = self.find_origin()

            if self.type == 'I':
                piece_mat_size = 4
            else:
                piece_mat_size = 3

            for i in range(0,4):
                if rotationType == 'CW':
                    temp_blocks[i][config.ROW] = origin[config.ROW] + self.currentDef[i][config.COL]
                    temp_blocks[i][config.COL] = origin[config.COL] + (piece_mat_size - 1) - self.currentDef[i][config.ROW]
                else:
                    temp_blocks[i][config.COL] = origin[config.COL] + self.currentDef[i][config.ROW]
                    temp_blocks[i][config.ROW] = origin[config.ROW] + (piece_mat_size - 1) - self.currentDef[i][config.COL]

            if not self.rot_collision_check(temp_blocks):
                for i in range(0,4):
                    self.blocks[i].currentPos.row = temp_blocks[i][config.ROW]
                    self.blocks[i].currentPos.col = temp_blocks[i][config.COL]
                    self.currentDef[i][config.ROW] = self.blocks[i].currentPos.row - origin[config.ROW]
                    self.currentDef[i][config.COL] = self.blocks[i].currentPos.col - origin[config.COL]

    def spawn(self):

        self.dropScore = 0

        origin = [0,3]

        for i in range(0,4):
            self.currentDef[i] = list(config.pieceDefs[self.type][i])

        spawn_try = 0
        while spawn_try < 2:
            if not self.spawn_collision_check(origin):
                break
            else:
                spawn_try = spawn_try + 1
                origin[config.ROW] = origin[config.ROW] - 1
                self.gameOverCondition = True
                self.status = 'collided'

        for i in range(0,4):
            spawn_row = origin[config.ROW] + config.pieceDefs[self.type][i][config.ROW]
            spawn_col = origin[config.COL] + config.pieceDefs[self.type][i][config.COL]
            self.blocks[i].currentPos.row = spawn_row
            self.blocks[i].currentPos.col = spawn_col

    def move(self, last_block_mat):

        if self.status == 'uncreated':
            self.status = 'moving'
            self.blockMat = last_block_mat
            self.spawn()

        elif self.status == 'moving':

            if config.key.down.status == 'pressed':
                if config.key.xNav.status == 'right':
                    if self.mov_collision_check('down'):
                        self.create_next_move('noMove')
                        self.status = 'collided'
                    elif self.mov_collision_check('downRight'):
                        self.create_next_move('down')
                    else:
                        self.create_next_move('downRight')

                elif config.key.xNav.status == 'left':
                    if self.mov_collision_check('down'):
                        self.create_next_move('noMove')
                        self.status = 'collided'
                    elif self.mov_collision_check('downLeft'):
                        self.create_next_move('down')
                    else:
                        self.create_next_move('downLeft')

                else: # 'idle'
                    if self.mov_collision_check('down'):
                        self.create_next_move('noMove')
                        self.status = 'collided'
                    else:
                        self.create_next_move('down')

                self.apply_fast_move()

            elif config.key.down.status == 'idle':
                if config.key.xNav.status == 'right':
                    if self.mov_collision_check('right'):
                        self.create_next_move('noMove')
                    else:
                        self.create_next_move('right')
                elif config.key.xNav.status == 'left':
                    if self.mov_collision_check('left'):
                        self.create_next_move('noMove')
                    else:
                        self.create_next_move('left')
                else:
                    self.create_next_move('noMove')

                self.apply_fast_move()

                self.slow_move_action()

            else: # 'released'
                config.key.down.status = 'idle'


# Class for the blocks of the moving piece. Each piece is made of 4 blocks in Tetris game
class MovingBlock:

    def __init__(self):

        self.currentPos = self.CurrentPosClass(0,0)
        self.nextPos = self.NextPosClass(0,0)

    class CurrentPosClass:

        def __init__(self,row,col):
            self.row = row
            self.col = col

    class NextPosClass:

        def __init__(self,row,col):
            self.row = row
            self.col = col