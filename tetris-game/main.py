import pygame
import sys
import config
import classes

# Main game loop
def game_loop():

    block_size = 20
    board_col_num = 10
    board_row_num = 20
    board_line_width = 10
    block_line_width = 1
    score_board_width = block_size * (board_col_num//2)
    board_pos_x = config.DISPLAY_WIDTH*0.3
    board_pos_y = config.DISPLAY_HEIGHT*0.15

    main_board = classes.MainBoard(block_size,board_pos_x,board_pos_y,board_col_num,board_row_num,board_line_width,block_line_width,score_board_width)

    x_change = 0

    game_exit = False

    clock = pygame.time.Clock()

    while not game_exit: #Stay in this loop unless the game is quit

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #Looks for quitting event in every iteration (Meaning closing the game window)
                game_exit = True

            if event.type == pygame.KEYDOWN: #Keyboard keys press events
                if event.key == pygame.K_LEFT:
                    x_change += -1
                if event.key == pygame.K_RIGHT:
                    x_change += 1
                if event.key == pygame.K_DOWN:
                    config.key.down.status = 'pressed'
                if event.key == pygame.K_UP:
                    if config.key.rotate.status == 'idle':
                        config.key.rotate.trig = True
                        config.key.rotate.status = 'pressed'
                if event.key == pygame.K_z:
                    if config.key.cRotate.status == 'idle':
                        config.key.cRotate.trig = True
                        config.key.cRotate.status = 'pressed'
                if event.key == pygame.K_p:
                    if config.key.pause.status == 'idle':
                        config.key.pause.trig = True
                        config.key.pause.status = 'pressed'
                if event.key == pygame.K_r:
                    if config.key.restart.status == 'idle':
                        config.key.restart.trig = True
                        config.key.restart.status = 'pressed'
                if event.key == pygame.K_RETURN:
                    config.key.enter.status = 'pressed'

            if event.type == pygame.KEYUP: #Keyboard keys release events
                if event.key == pygame.K_LEFT:
                    x_change += 1
                if event.key == pygame.K_RIGHT:
                    x_change += -1
                if event.key == pygame.K_DOWN:
                    config.key.down.status = 'released'
                if event.key == pygame.K_UP:
                    config.key.rotate.status = 'idle'
                if event.key == pygame.K_z:
                    config.key.cRotate.status = 'idle'
                if event.key == pygame.K_p:
                    config.key.pause.status = 'idle'
                if event.key == pygame.K_r:
                    config.key.restart.status = 'idle'
                if event.key == pygame.K_RETURN:
                    config.key.enter.status = 'idle'

            if x_change > 0:
                config.key.xNav.status = 'right'
            elif x_change < 0:
                config.key.xNav.status = 'left'
            else:
                config.key.xNav.status = 'idle'

        config.gameDisplay.fill(config.BLACK) #Whole screen is painted black in every iteration before any other drawings occur

        main_board.game_action() #Apply all the game actions here
        main_board.draw() #Draw the new board after game the new game actions
        config.gameClock.update() #Increment the frame tick

        pygame.display.update() #Pygame display update
        clock.tick(60) #Pygame clock tick function(60 fps)

# Main program
if __name__ == "__main__":
    config.key = classes.GameKeyInput()
    config.gameClock = classes.GameClock()
    game_loop()
    pygame.quit()
    sys.exit()