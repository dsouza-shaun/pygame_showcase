import pygame
import sys
import config
from game import Game
from ui import Button

def main():
    # Initialize Pygame here
    pygame.init()

    # Initialize screen locally
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Tower Defense")

    game = Game()
    clock = pygame.time.Clock()
    running = True

    # Menu Buttons
    menu_btns = [
        Button(config.WIDTH // 2 - 100, config.HEIGHT // 2, 200, 50, "", lambda: game.set_state(config.PLAYING)),
        Button(config.WIDTH // 2 - 100, config.HEIGHT // 2 + 70, 200, 50, "", game.load_from_file, color=config.BLUE)
    ]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if game.state == config.MENU:
                        for btn in menu_btns:
                            if btn.rect.collidepoint(event.pos):
                                btn.callback()
                    elif game.state in [config.PLAYING, config.GAME_OVER, config.VICTORY]:
                        if game.state in [config.GAME_OVER, config.VICTORY]:
                            game.reset()
                        else:
                            game.handle_click(event.pos, event.button)

                elif event.button == 3: # Right click
                    if game.state == config.PLAYING:
                        game.handle_click(event.pos, event.button)

            if event.type == pygame.KEYDOWN:
                if game.state == config.PLAYING:
                    if event.key == pygame.K_1: game.select_tower_type('basic')
                    elif event.key == pygame.K_2: game.select_tower_type('sniper')
                    elif event.key == pygame.K_3: game.select_tower_type('splash')
                    elif event.key == pygame.K_4: game.select_tower_type('slow')
                    elif event.key == pygame.K_5: game.select_tower_type('rapid')
                    elif event.key == pygame.K_ESCAPE:
                        game.selected_tower = None
                    elif event.key == pygame.K_SPACE:
                        game.start_wave()
                    elif event.key == pygame.K_s:
                        game.save_game_state()

        game.update()

        # Pass the local 'screen' variable to the draw method
        game.draw(screen)

        # Draw menu buttons manually if in menu
        if game.state == config.MENU:
            for btn in menu_btns:
                btn.draw(screen)
            start_text = game.font.render("START GAME", True, config.WHITE)
            load_text = game.font.render("LOAD GAME", True, config.WHITE)
            screen.blit(start_text, (menu_btns[0].rect.centerx - start_text.get_width()//2, menu_btns[0].rect.centery - start_text.get_height()//2))
            screen.blit(load_text, (menu_btns[1].rect.centerx - load_text.get_width()//2, menu_btns[1].rect.centery - load_text.get_height()//2))

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()