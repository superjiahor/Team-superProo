import pygame
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
FPS = 60
PLAYER_VEL = 5
LASER_VEL = 10
ENEMY_VEL = 3
ENEMY_GEN_DELAY = 2000
BG_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Master")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

font = pygame.font.Font(None, 36)

# Load assets
background_image = pygame.image.load('background.png')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

player_image = pygame.image.load('player.png')
player_image = pygame.transform.scale(player_image, (50, 50))

enemy_image = pygame.image.load('enemy.png')
enemy_image = pygame.transform.scale(enemy_image, (50, 50))

player_laser_image = pygame.image.load('player_laser.png')
player_laser_image = pygame.transform.scale(player_laser_image, (30, 10))

enemy_laser_image = pygame.image.load('enemy_laser.png')
enemy_laser_image = pygame.transform.scale(enemy_laser_image, (30, 10))

# Soundtrack
pygame.mixer.music.load('soundtrack.mp3')  # Load the soundtrack
pygame.mixer.music.play(-1)  # Loop the soundtrack indefinitely

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(player_image, (70, 70))
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 200
        self.shoot_delay = 250  # milliseconds
        self.last_shoot_time = pygame.time.get_ticks()

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw_health(self, surface):
        health_text = font.render(f'Health: {self.health}', True, WHITE)
        surface.blit(health_text, (10, 10))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_VEL
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_VEL

        # Continuous shooting
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and (current_time - self.last_shoot_time) >= self.shoot_delay:
            self.shoot()
            self.last_shoot_time = current_time

    def shoot(self):
        laser = Laser(self.rect.right, self.rect.centery, LASER_VEL, GREEN, player_laser_image)
        all_sprites.add(laser)
        player_lasers.add(laser)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(enemy_image, (65, 65))
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 10
        self.attack_timer = 0

    def update(self):
        self.rect.x -= ENEMY_VEL
        if self.rect.right < 0:
            self.kill()
        self.attack_timer += 1
        if self.attack_timer > 100:
            self.attack()
            self.attack_timer = 0
        if random.randint(1, 100) == 1:
            self.shoot()

    def shoot(self):
        laser = Laser(self.rect.left, self.rect.centery, -LASER_VEL, RED, enemy_laser_image)
        all_sprites.add(laser)
        enemy_lasers.add(laser)

    def attack(self):
        if self.rect.x > 0 and player.health > 0:
            player.take_damage(5)

# Laser class
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

# Spawn enemy function
def spawn_enemy():
    x = WIDTH
    y = random.randint(50, HEIGHT - 50)
    enemy = Enemy(x, y)
    all_sprites.add(enemy)
    enemies.add(enemy)

# Draw cover screen
def draw_cover():
    screen.fill(BLACK)
    cover_text = font.render("Welcome to Infinite Enemy Waves", True, WHITE)
    start_text = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(cover_text, (screen.get_width() // 2 - cover_text.get_width() // 2, screen.get_height() // 2 - cover_text.get_height()))
    screen.blit(start_text, (screen.get_width() // 2 - start_text.get_width() // 2, screen.get_height() // 2 + cover_text.get_height() // 2))
    pygame.display.flip()

# Game loop
def game_loop():
    global player
    global all_sprites, player_lasers, enemy_lasers, enemies

    all_sprites = pygame.sprite.Group()
    player_lasers = pygame.sprite.Group()
    enemy_lasers = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    player = Player(50, HEIGHT // 2)
    all_sprites.add(player)

    score = 0
    spawn_timer = 0
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and player.health <= 0:
                game_loop()  # Restart the game on click after game over

        spawn_timer += 1
        if spawn_timer > 100:
            spawn_enemy()
            spawn_timer = 0

        all_sprites.update()

        if pygame.sprite.spritecollide(player, enemy_lasers, True):
            player.take_damage(10)

        for enemy in enemies:
            if pygame.sprite.spritecollide(enemy, player_lasers, True):
                enemy.health -= 10
                if enemy.health <= 0:
                    enemy.kill()
                    score += 10

        screen.fill(BG_COLOR)
        screen.blit(background_image, (0, 0))

        all_sprites.draw(screen)
        player.draw_health(screen)

        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 50))

        if player.health <= 0:
            game_over_text = font.render("Game Over - Click to Restart", True, WHITE)
            screen.blit(game_over_text, (screen.get_width() // 2 - 150, screen.get_height() // 2))
            pygame.display.flip()

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

# Game cover screen
cover_mode = True
while cover_mode:
    draw_cover()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cover_mode = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            cover_mode = False
            game_loop()

pygame.quit()
