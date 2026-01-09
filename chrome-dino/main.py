import pygame
import os
import random

pygame.init()

# ------------------ CONSTANTS ------------------
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Run")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (83, 83, 83)

# ------------------ LOAD ASSETS ------------------
RUNNING = [
    pygame.image.load(os.path.join("assets/dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("assets/dino", "DinoRun2.png"))
]
JUMPING = pygame.image.load(os.path.join("assets/dino", "DinoJump.png"))
DUCKING = [
    pygame.image.load(os.path.join("assets/dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("assets/dino", "DinoDuck2.png"))
]

SMALL_CACTUS = [
    pygame.image.load(os.path.join("assets/cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("assets/cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("assets/cactus", "SmallCactus3.png"))
]

LARGE_CACTUS = [
    pygame.image.load(os.path.join("assets/cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("assets/cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("assets/cactus", "LargeCactus3.png"))
]

BIRD = [
    pygame.image.load(os.path.join("assets/bird", "Bird1.png")),
    pygame.image.load(os.path.join("assets/bird", "Bird2.png"))
]

CLOUD = pygame.image.load(os.path.join("assets/other", "Cloud.png"))
BG = pygame.image.load(os.path.join("assets/other", "Track.png"))

FONT_SMALL = pygame.font.Font("freesansbold.ttf", 20)
FONT_BIG = pygame.font.Font("freesansbold.ttf", 40)

# ------------------ CLASSES ------------------
class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.duck_img = DUCKING

        self.dino_run = True
        self.dino_jump = False
        self.dino_duck = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL

        self.image = self.run_img[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.rect.inflate_ip(-20, -20)

    def update(self, userInput):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.dino_duck:
            self.duck()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_jump = True
            self.dino_run = False
            self.dino_duck = False
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
        elif not self.dino_jump:
            self.dino_run = True
            self.dino_duck = False

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.rect.inflate_ip(-20, -20)
        self.step_index += 1

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS_DUCK
        self.rect.inflate_ip(-20, -10)
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        self.rect.y -= self.jump_vel * 3
        self.jump_vel -= 0.8

        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self):
        SCREEN.blit(self.image, self.rect)
        # pygame.draw.rect(SCREEN, (255, 0, 0), self.rect, 2)  # debug


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1200)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2000, 3000)
            self.y = random.randint(50, 100)

    def draw(self):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, y_pos):
        self.image = image
        self.type = random.randint(0, len(image) - 1)
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = y_pos
        self.rect.inflate_ip(-10, -10)

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.remove(self)

    def draw(self):
        SCREEN.blit(self.image[self.type], self.rect)
        # pygame.draw.rect(SCREEN, (0, 0, 255), self.rect, 2)


class Bird(Obstacle):
    def __init__(self):
        super().__init__(BIRD, 250)
        self.index = 0

    def draw(self):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


# ------------------ GAME FUNCTIONS ------------------
def score():
    global points, game_speed

    points += 1
    if points % 100 == 0:
        game_speed += 1

    # Format score like 000089
    score_text = f"{points:06d}"

    text = FONT_SMALL.render(score_text, True, GREY)
    SCREEN.blit(text, (SCREEN_WIDTH - 120, 40))

def background():
    global x_pos_bg
    image_width = BG.get_width()
    SCREEN.blit(BG, (x_pos_bg, 380))
    SCREEN.blit(BG, (image_width + x_pos_bg, 380))
    if x_pos_bg <= -image_width:
        x_pos_bg = 0
    x_pos_bg -= game_speed


def main():
    global game_speed, x_pos_bg, points, obstacles
    clock = pygame.time.Clock()

    player = Dinosaur()
    cloud = Cloud()

    game_speed = 20
    x_pos_bg = 0
    points = 0
    obstacles = []

    run = True
    while run:
        SCREEN.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        userInput = pygame.key.get_pressed()

        player.update(userInput)
        player.draw()

        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0:
                obstacles.append(Obstacle(SMALL_CACTUS, 325))
            elif choice == 1:
                obstacles.append(Obstacle(LARGE_CACTUS, 300))
            else:
                obstacles.append(Bird())

        for obstacle in obstacles:
            obstacle.update()
            obstacle.draw()
            if player.rect.colliderect(obstacle.rect):
                pygame.time.delay(1000)
                menu(points)

        background()
        cloud.update()
        cloud.draw()
        score()

        clock.tick(30)
        pygame.display.update()


def menu(last_score):
    while True:
        SCREEN.fill(WHITE)

        title = FONT_BIG.render("DINO RUN", True, BLACK)
        msg = FONT_SMALL.render("Press ANY KEY to Start", True, BLACK)

        SCREEN.blit(title, (SCREEN_WIDTH // 2 - 100, 200))
        SCREEN.blit(msg, (SCREEN_WIDTH // 2 - 120, 260))

        if last_score > 0:
            score_text = FONT_SMALL.render(f"Last Score: {last_score}", True, BLACK)
            SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - 70, 300))

        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                main()


# ------------------ START ------------------
menu(0)
