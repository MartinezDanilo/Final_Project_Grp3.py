import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 1
BULLET_SPEED = 7
ENEMY_BULLET_SPEED = 5
BOSS_SPEED = 3  # Speed of the boss
BOSS_SHOOT_INTERVAL = 4000  # Time in milliseconds between boss shots
BOSS_HEALTH = 100  # Boss health

# Image Sizes
PLAYER_SIZE = (64, 64)  # Size for the player image
ENEMY_SIZE = (50, 50)    # Size for the enemy image
BOSS_SIZE = (100, 100)   # Size for the boss enemy

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aircraft Fighter")

# Load images
player_image = pygame.image.load("tank.png")  # Ensure this image exists
player_image = pygame.transform.scale(player_image, PLAYER_SIZE)
player_rect = player_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

# Load background image
background_image = pygame.image.load("BG.jpg")  # Ensure this image exists
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and resize enemy images
enemy_images = [
    pygame.transform.scale(pygame.image.load("helicopter.png"), ENEMY_SIZE),
    pygame.transform.scale(pygame.image.load("transport.png"), ENEMY_SIZE),
    pygame.transform.scale(pygame.image.load("aircraft2.png"), ENEMY_SIZE),
    pygame.transform.scale(pygame.image.load("aircraft3.png"), ENEMY_SIZE)
]

# Load and resize boss image
boss_image = pygame.transform.scale(pygame.image.load("boss.png"), BOSS_SIZE)  # Ensure this image exists

# Load sound effects
pygame.mixer.music.load("background_music.mp3")  # Background music
pygame.mixer.music.set_volume(0.5)  # Set volume for music
player_bullet_sound = pygame.mixer.Sound("PlayerBullet.mp3")
enemy_bullet_sound = pygame.mixer.Sound("enemy_bullet.mp3")
enemy_die_sound = pygame.mixer.Sound("EnemyDie.mp3")
game_over_sound = pygame.mixer.Sound("GameOver.mp3")

# Bullet class
class Bullet:
    def __init__(self, x, y, speed=BULLET_SPEED):
        self.rect = pygame.Rect(x, y, 5, 10)
        self.speed = speed

    def move(self):
        self.rect.y -= self.speed

# Enemy class
class Enemy:
    def __init__(self):
        self.image = random.choice(enemy_images)  # Randomly choose an enemy image
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH - ENEMY_SIZE[0]), 0))
        self.bullets = []
        self.has_shot = False  # Flag to check if the enemy has shot

    def move(self):
        self.rect.y += ENEMY_SPEED

    def shoot(self):
        if not self.has_shot:
            bullet_x = self.rect.centerx - 2.5
            bullet_y = self.rect.bottom
            self.bullets.append(Bullet(bullet_x, bullet_y, ENEMY_BULLET_SPEED))
            enemy_bullet_sound.play()  # Play enemy bullet sound
            self.has_shot = True  # Set flag to indicate the enemy has shot

# Boss class
class Boss:
    def __init__(self):
        self.image = boss_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.health = BOSS_HEALTH  # Boss starts with 100 health
        self.bullets = []
        self.last_shot_time = pygame.time.get_ticks()  # Track time of the last shot
        self.direction = random.choice([-1, 1])  # Random initial direction

    def move(self):
        # Random movement and target tracking
        if random.random() < 0.02:  # Random chance to change direction
            self.direction *= -1  # Reverse direction

        # Update position with directional movement
        self.rect.x += self.direction * BOSS_SPEED

        # Keep the boss within the screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1  # Reverse direction
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.direction = -1  # Reverse direction

    def shoot(self):
        bullet_x = self.rect.centerx - 2.5
        bullet_y = self.rect.bottom
        self.bullets.append(Bullet(bullet_x, bullet_y, ENEMY_BULLET_SPEED))
        enemy_bullet_sound.play()  # Play enemy bullet sound

# Main game loop
def main():
    clock = pygame.time.Clock()
    bullets = []
    enemies = []
    boss = None
    score = 0
    level = 1  # Start at level 1
    lives = 3  # Player's lives
    global ENEMY_SPEED  # Make ENEMY_SPEED global to modify it

    pygame.mixer.music.play(-1)  # Play background music in a loop

    bullet_fired = False  # Flag to track if a bullet has been fired

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
            player_rect.x += PLAYER_SPEED
        
        # Fire a bullet when the up arrow is pressed
        if keys[pygame.K_UP] and not bullet_fired:
            bullets.append(Bullet(player_rect.centerx - 2.5, player_rect.top))
            player_bullet_sound.play()  # Play player bullet sound
            bullet_fired = True  # Set the flag to indicate a bullet has been fired
        elif not keys[pygame.K_UP]:
            bullet_fired = False  # Reset the flag if the key is not pressed

        # Move bullets
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        # Spawn enemies
        if not boss and random.randint(1, 50) == 1:
            enemies.append(Enemy())

        # Move enemies and their bullets
        for enemy in enemies[:]:
            enemy.move()
            if enemy.rect.top > SCREEN_HEIGHT:
                enemies.remove(enemy)

            # Shoot bullet when enemy arrives on screen
            if enemy.rect.top >= 50:  # Adjust this value if needed:
                enemy.shoot()

            # Move enemy bullets
            for bullet in enemy.bullets[:]:
                bullet.rect.y += ENEMY_BULLET_SPEED  # Move bullets downward
                if bullet.rect.top > SCREEN_HEIGHT:
                    enemy.bullets.remove(bullet)

                # Check for bullet collisions with player
                if bullet.rect.colliderect(player_rect):
                    enemy.bullets.remove(bullet)
                    lives -= 1  # Reduce lives when hit
                    if lives <= 0:
                        running = False  # End game if no lives left
                    break

            # Check for bullet collisions with enemies
            for bullet in bullets[:]:
                if bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemy_die_sound.play()  # Play enemy die sound
                    score += 1  # Increment score when enemy is hit
                    enemies.remove(enemy)  # Remove enemy only after score increment
                    break  # Exit the bullet loop since the enemy is already removed

        # Check for level up
        if score > 0 and score % 50 == 0:  # Every 50 points
            level += 1  # Increment level
            ENEMY_SPEED *= 1.5  # Increase speed by half
            score += 1  # Avoid re-triggering the level up on the same score

            # Spawn boss enemy
            boss = Boss()

        # Move and shoot the boss
        if boss:
            boss.move()
            current_time = pygame.time.get_ticks()
            if current_time - boss.last_shot_time > BOSS_SHOOT_INTERVAL:  # Check if 4 seconds have passed
                boss.shoot()
                boss.last_shot_time = current_time  # Reset the last shot time

            # Move boss bullets
            for bullet in boss.bullets[:]:
                bullet.rect.y += ENEMY_BULLET_SPEED  # Move bullets downward
                if bullet.rect.top > SCREEN_HEIGHT:
                    boss.bullets.remove(bullet)
                # Check for bullet collisions with the player
                if bullet.rect.colliderect(player_rect):
                    boss.bullets.remove(bullet)
                    lives -= 1  # Reduce lives when hit
                    if lives <= 0:
                        running = False  # End game if no lives left
                    break

            # Check for bullet collisions with the boss
            for bullet in bullets[:]:
                if bullet.rect.colliderect(boss.rect):
                    bullets.remove(bullet)
                    score += 10  # Increment score for hitting boss
                    enemy_die_sound.play()  # Play enemy die sound for boss hit
                    boss.health -= 1  # Decrement boss health for each bullet hit
                    if boss.health <= 0:
                        boss = None  # Remove the boss when defeated
                        level += 1  # Increment level after defeating the boss
                    break  # Exit the bullet loop since the boss is already hit

        # Check for win condition
        if level > 3:  # Win condition: Reach level 3
            running = False  # End the game

        # Draw the background
        screen.blit(background_image, (0, 0))

        # Draw the player
        screen.blit(player_image, player_rect)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, RED, bullet.rect)

        # Draw enemies and their bullets
        for enemy in enemies:
            screen.blit(enemy.image, enemy.rect)
            for bullet in enemy.bullets:
                pygame.draw.rect(screen, RED, bullet.rect)

        # Draw boss if exists
        if boss:
            screen.blit(boss.image, boss.rect)
            for bullet in boss.bullets:
                pygame.draw.rect(screen, RED, bullet.rect)

            # Draw boss health bar at the top of the screen
            health_bar_width = 200  # Width of the health bar
            health_bar_height = 20  # Height of the health bar
            health_percentage = boss.health / BOSS_HEALTH
            # Draw background of health bar
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - health_bar_width // 2, 10, health_bar_width, health_bar_height))
            # Draw current health of boss
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH // 2 - health_bar_width // 2, 10, health_bar_width * health_percentage, health_bar_height))

        # Display score, lives, and level with correct colors
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, RED)
        lives_text = font.render(f'Lives: {lives}', True, GREEN)
        level_text = font.render(f'Level: {level}', True, BLUE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(level_text, (10, 70))

        pygame.display.flip()
        clock.tick(60)

    # Play game over sound and show game over message
    game_over_sound.play()
    font_game_over = pygame.font.Font(None, 74)
    game_over_text = font_game_over.render('Game Over', True, (255, 0, 0))
    play_again_text = font_game_over.render('Press R to Play Again', True, (0, 0, 0))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 40))
    screen.blit(play_again_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 10))
    pygame.display.flip()

    # Wait for player input to restart or quit
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_input = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press R to restart
                    main()
                    waiting_for_input = False

    pygame.quit()

if __name__ == "__main__":
    main()
