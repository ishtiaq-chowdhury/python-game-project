import pygame
from sys import exit
from random import randint, choice

# Sprites
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_index = 0
        player_walk_1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
        player_walk_2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_jump = pygame.image.load("graphics/player/player_jump.png").convert_alpha()
        self.jump_sound = pygame.mixer.Sound("audio/jump.mp3")
        self.jump_sound.set_volume(0.05)
        self.gravity = 0
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80,300))

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom == 300:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom > 300:
            self.rect.bottom = 300

    def animate_player(self):
        if self.rect.bottom == 300:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]
        else:
            self.image = self.player_jump

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animate_player()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, species):
        super().__init__()
        if species == "Fly":
            fly_flight_1 = pygame.image.load("graphics/fly/fly1.png").convert_alpha()
            fly_flight_2 = pygame.image.load("graphics/fly/fly2.png").convert_alpha()
            self.frames = [fly_flight_1, fly_flight_2]
            y_pos = 210
        elif species == "Snail":
            snail_glide_1 = pygame.image.load("graphics/snail/snail1.png").convert_alpha()
            snail_glide_2 = pygame.image.load("graphics/snail/snail2.png").convert_alpha()
            self.frames = [snail_glide_1, snail_glide_2]
            y_pos = 300
        else: y_pos = -1
        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(1200,1400),y_pos))

    def animate_obstacle(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        if self.rect.x < -100:
            self.kill()

    def update(self):
        self.animate_obstacle()
        self.destroy()
        self.rect.x -= score // 5 + 6

# Functions
def display_score():
    current_time = (pygame.time.get_ticks() - start_time) // 1000
    score_surf = pixel_font.render(f'Score: {current_time}', False, "black")
    score_rect = score_surf.get_rect(center=(400,50))
    screen.blit(score_surf,score_rect)
    return current_time

def sprite_collisions():
    if pygame.sprite.spritecollide(player_group.sprite,obstacle_group,False):
        background_music.stop()
        player_group.sprite.jump_sound.stop()
        return True
    else: return False

# Setup
pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption("Pixel Runner")
pygame.display.set_icon(pygame.image.load("graphics/Player/player_stand.png"))

pixel_font = pygame.font.Font("font/pixeltype.ttf", 50)
pixel_font2 = pygame.font.Font("font/pixeltype.ttf", 35)
clock = pygame.time.Clock()
start_time = 0
game_active = False
score = 0
highscore = 0

# Groups
player_group = pygame.sprite.GroupSingle()
player_group.add(Player())

obstacle_group = pygame.sprite.Group()

# Obstacle Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,2000)

# Music
background_music = pygame.mixer.Sound("audio/music.wav")
background_music.set_volume(0.25)
background_music_playing = False

# Environment
sky_surf = pygame.image.load("graphics/environment/sky.png").convert_alpha()
ground_surf = pygame.image.load("graphics/environment/ground.png").convert_alpha()

# Start Screen
title_surf = pixel_font.render("Pixel Runner", False, "#6fc4a9")
message_surf = pixel_font.render("Click to Start / Space to Jump", False, "#6fc4a9")

icon_surf = pygame.image.load("graphics/player/player_stand.png").convert_alpha()
icon_surf = pygame.transform.scale2x(icon_surf)

while True:
    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(["Fly", "Snail", "Snail", "Snail"])))
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_active = True
                player_group.sprite.rect.bottom = 300
                player_group.sprite.gravity = 0
                obstacle_group.empty()
                start_time = pygame.time.get_ticks()
                background_music_playing = False

    # Game Loop
    if game_active:
        # Music
        if score == 2 and not background_music_playing:
            background_music_playing = True
            background_music.play(loops=-1)

        # Environment
        screen.blit(sky_surf, (0, 0))
        screen.blit(ground_surf, (0, 300))

        # Score
        score = display_score()

        # Player
        player_group.draw(screen)
        player_group.update()

        # Obstacles
        obstacle_group.draw(screen)
        obstacle_group.update()

        # Collisions
        game_active = not sprite_collisions()
    else:
        # Start Screen
        screen.fill("#6084a4")
        if score == 0:
            title_rect = title_surf.get_rect(center=(400, 80))
            message_rect = message_surf.get_rect(center=(400, 320))
            icon_rect = icon_surf.get_rect(center=(400, 195))
        else:
            title_rect = title_surf.get_rect(center=(400, 70))
            message_rect = message_surf.get_rect(center=(400, 310))
            icon_rect = icon_surf.get_rect(center=(400, 185))

            if score > highscore: highscore = score
            scores_surf = pixel_font2.render(f"Current Score: {score}     Highscore: {highscore}", False, "black")
            scores_rect = scores_surf.get_rect(center=(400, 340))
            screen.blit(scores_surf, scores_rect)

        screen.blit(title_surf, title_rect)
        screen.blit(message_surf, message_rect)
        screen.blit(icon_surf,icon_rect)

    # End Tick
    pygame.display.update()
    clock.tick(60)