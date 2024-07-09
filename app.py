import pygame
import random
import json
import math
from random_word import RandomWords

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("DynoType")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
WIDTH = 1280
HEIGHT = 720

# Load images
player_images_orig = [
    pygame.image.load('assets/images/dinoCharactersVersion1.1/gifs/DinoSprites_doux.gif'),
    pygame.image.load('assets/images/dinoCharactersVersion1.1/gifs/DinoSprites_mort.gif'),
    pygame.image.load('assets/images/dinoCharactersVersion1.1/gifs/DinoSprites_tard.gif'),
    pygame.image.load('assets/images/dinoCharactersVersion1.1/gifs/DinoSprites_vita.gif')
]

level_images_orig = [
    pygame.image.load('assets/images/Levels/1.png'),
    pygame.image.load('assets/images/Levels/2.png'),
    pygame.image.load('assets/images/Levels/3.png'),
    pygame.image.load('assets/images/Levels/4.png')
]

button_image_idle = pygame.image.load('assets/images/Prinbles_Buttons_Cartoon-II (v 1.0) (9_11_2023)/png/Buttons/Rect-Text-Blue/Play-Idle.png')
button_image_clicked = pygame.image.load('assets/images/Prinbles_Buttons_Cartoon-II (v 1.0) (9_11_2023)/png/Buttons/Rect-Text-Blue/Play-Click.png')
asteroid_image = pygame.image.load('assets/images/—Pngtree—meteorite space fire_13340354.png')
volume_mute_image_idle = pygame.image.load('assets/images/Prinbles_Buttons_Cartoon-II (v 1.0) (9_11_2023)/png/Buttons/Square-Icon-Blue/Sound-None-Idle.png')
volume_up_image_idle = pygame.image.load('assets/images/Prinbles_Buttons_Cartoon-II (v 1.0) (9_11_2023)/png/Buttons/Square-Icon-Blue/Sound-Three-Idle.png')
volume_down_image_idle = pygame.image.load('assets/images/Prinbles_Buttons_Cartoon-II (v 1.0) (9_11_2023)/png/Buttons/Square-Icon-Blue/Sound-Two-Idle.png')

# Initialize the random word generator
with open('words.json', 'r') as f:
    data = json.load(f)
    level_1 = data['levels']['1']['words']
    level_2 = data['levels']['2']['words']
    level_3 = data['levels']['3']['words']

level_4 = RandomWords()

class Player:
    def __init__(self, image, scale=4):
        self.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT / 1.26))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Asteroid:
    def __init__(self, words):
        self.image = pygame.transform.scale(asteroid_image, (100, 100))
        self.word = random.choice(words)
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -50))
        self.speed = 2

    def move_towards(self, target_x, target_y):
        # Calculate direction vector (dx, dy)
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery

        # Calculate the distance to the target
        distance = math.hypot(dx, dy)

        if distance != 0:
            # Normalize direction vector
            dx /= distance
            dy /= distance

            # Move asteroid towards the target
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        word_text = font.render(self.word, True, pygame.Color("white"))
        surface.blit(word_text, (self.rect.x, self.rect.y - 30))

class TextBox:
    def __init__(self):
        self.rect = pygame.Rect(275, HEIGHT - 75, 400, 40)
        self.text = ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color("white"), self.rect, 2)
        text_surface = font.render(self.text, True, pygame.Color("white"))
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 5))

class Score:
    def __init__(self):
        self.rect = pygame.Rect(25, HEIGHT - 75, 200, 40)
        self.score = 0

    def increment(self):
        self.score += 1

    def decrement(self):
        if self.score > 0:
            self.score -= 1

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color("white"), self.rect, 2)
        text_surface = font.render(f"Score: {self.score}", True, pygame.Color("white"))
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 5))

class Volume:
    def __init__(self, mute_image, volume_up_image, volume_down_image, pos=(10, 10), spacing=80):
        self.images = {
            'mute': mute_image,
            'down': volume_down_image,
            'up': volume_up_image
        }
        self.positions = {
            'mute': pos,
            'down': (pos[0] + spacing, pos[1]),
            'up': (pos[0] + 2 * spacing, pos[1]),
        }
        self.rects = {
            'mute': self.images['mute'].get_rect(topleft=self.positions['mute']),
            'down': self.images['down'].get_rect(topleft=self.positions['down']),
            'up': self.images['up'].get_rect(topleft=self.positions['up']),
        }
        
    def draw(self, surface):
        for key in self.images:
            surface.blit(self.images[key], self.positions[key])
        
class Game:
    def __init__(self):
        self.state = "home"
        self.player = None
        self.asteroids = []
        self.textbox = TextBox()
        self.score = Score()
        self.start_time = None
        self.selected_character = 0
        self.button_clicked = False
        self.button_rect = button_image_idle.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        self.volume_control = Volume(volume_mute_image_idle, volume_up_image_idle, volume_down_image_idle)
        self.character_images = [pygame.transform.scale(img, (img.get_width() * 4, img.get_height() * 4)) for img in player_images_orig]
        self.character_rects = [
            self.character_images[0].get_rect(center=(WIDTH / 2 - 200, HEIGHT / 1.45)),
            self.character_images[1].get_rect(center=(WIDTH / 2 - 75, HEIGHT / 1.45)),
            self.character_images[2].get_rect(center=(WIDTH / 2 + 75, HEIGHT / 1.45)),
            self.character_images[3].get_rect(center=(WIDTH / 2 + 200, HEIGHT / 1.45))
        ]
        scale_factor = 0.2
        self.level_images = [pygame.transform.scale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))) for img in level_images_orig]
        self.level_rects = [
            self.level_images[0].get_rect(center=(WIDTH / 2 - 200, HEIGHT / 2)),
            self.level_images[1].get_rect(center=(WIDTH / 2 - 65, HEIGHT / 2)),
            self.level_images[2].get_rect(center=(WIDTH / 2 + 65, HEIGHT / 2)),
            self.level_images[3].get_rect(center=(WIDTH / 2 + 200, HEIGHT / 2))
        ]
        self.background_image = pygame.image.load('assets/images/Free Pixel Art Forest/Preview/Background.png').convert()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
        self.homescreen_image = pygame.image.load('assets/images/PNG/game_background_3/game_background_3.1.png').convert()
        self.homescreen_image = pygame.transform.scale(self.homescreen_image, (WIDTH, HEIGHT))
        self.character_select_image = pygame.image.load('assets/images/PNG/game_background_4/game_background_4.png').convert()
        self.character_select_image = pygame.transform.scale(self.character_select_image, (WIDTH, HEIGHT))

        self.home_title_font = pygame.font.Font('assets/fonts/Silver.ttf', 72)
        self.home_title_text = self.home_title_font.render('DinoType', True, pygame.Color("white"))
        self.home_title_rect = self.home_title_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))

        self.character_title_font = pygame.font.Font('assets/fonts/Silver.ttf', 72)
        self.character_title_text = self.character_title_font.render("Choose your Dino!", True, pygame.Color("white"))
        self.character_title_rect = self.character_title_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 200))

        self.difficulty_title_font = pygame.font.Font('assets/fonts/Silver.ttf', 72)
        self.difficulty_title_text = self.difficulty_title_font.render("Choose your difficulty!", True, pygame.Color("White"))
        self.difficulty_title_rect = self.difficulty_title_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 200))

        # Music flags
        self.home_music_playing = False
        self.game_music_playing = False

        # Sound effects
        self.start_click = pygame.mixer.Sound('assets/sound/UI Soundpack/MP3/Retro8.mp3')
        self.character_click = pygame.mixer.Sound('assets/sound/UI Soundpack/MP3/Retro8.mp3')
        self.difficulty_click = pygame.mixer.Sound('assets/sound/UI Soundpack/MP3/Retro10.mp3')

    def play_home_music(self):
        pygame.mixer.music.load('assets/music/2016_ Clement Panchout_ Life is full of Joy.wav')
        pygame.mixer.music.play(-1)
        self.home_music_playing = True
        self.game_music_playing = False

    def play_game_music(self):
        pygame.mixer.music.load('assets/music/2014 07_ Clement Panchout_ Partycles OST_ Cheerful Title Screen.wav')
        pygame.mixer.music.play(-1)
        self.home_music_playing = False
        self.game_music_playing = True

    def draw_timer(self, surface):
        if self.state == "game" and self.start_time is not None:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.start_time) // 1000
            timer_text = font.render(f"Timer: {elapsed_time} seconds", True, pygame.Color("black"))
            surface.blit(timer_text, (1050, 10))

    def home_screen(self):
        screen.blit(self.homescreen_image, (0, 0))
        screen.blit(self.home_title_text, self.home_title_rect)
        if self.button_clicked:
            screen.blit(button_image_clicked, self.button_rect)
        else:
            screen.blit(button_image_idle, self.button_rect)
        if not self.home_music_playing:
            self.play_home_music()
        self.volume_control.draw(screen)

    def character_select(self):
        screen.blit(self.character_select_image, (0, 0))
        screen.blit(self.character_title_text, self.character_title_rect)
        for img, rect in zip(self.character_images, self.character_rects):
            screen.blit(img, rect)
        self.volume_control.draw(screen)

    def difficulty_select(self):
        screen.fill("black")
        screen.blit(self.difficulty_title_text, self.difficulty_title_rect)
        for img, rect in zip(self.level_images, self.level_rects):
            screen.blit(img, rect)
            self.volume_control.draw(screen)
    
    def game_screen(self):
        screen.blit(self.background_image, (0, -60))
        pygame.draw.rect(screen, (32, 42, 68), [0, HEIGHT - 100, WIDTH, 100])
        pygame.draw.rect(screen, 'white', [0, 0, WIDTH, HEIGHT], 5)
        pygame.draw.line(screen, 'white', [250, HEIGHT - 100], (250, HEIGHT), 2)
        pygame.draw.line(screen, 'white', [700, HEIGHT - 100], (700, HEIGHT), 2)
        pygame.draw.line(screen, 'white', [0, HEIGHT - 100], (WIDTH, HEIGHT - 100), 2)
        self.player.draw(screen)
        self.draw_timer(screen)
        for asteroid in self.asteroids:
            asteroid.draw(screen)
        self.textbox.draw(screen)
        self.score.draw(screen)
        self.volume_control.draw(screen)
        if not self.game_music_playing:
            self.play_game_music()

    def handle_home_click(self, mouse_pos):
        if self.button_rect.collidepoint(mouse_pos):
            self.button_clicked = True
            self.start_click.play()

    def handle_mouse_up(self, mouse_pos):
        if self.button_clicked and self.button_rect.collidepoint(mouse_pos):
            self.state = "character_selection"
        self.button_clicked = False

    def handle_character_click(self, mouse_pos):
        for i, rect in enumerate(self.character_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_character = i
                self.player = Player(player_images_orig[self.selected_character])
                self.character_click.play()
                self.state = "difficulty_selection"

    def handle_difficulty_click(self, mouse_pos):
        for i, rect in enumerate(self.level_rects):
            if rect.collidepoint(mouse_pos):
                self.start_time = pygame.time.get_ticks()

                if (i == 0):
                    self.level_words = level_1
                if (i == 1):
                    self.level_words = level_2
                if (i == 2):
                    self.level_words = level_3
                if (i == 3):
                    self.level_words = [level_4.get_random_word() for _ in range(50)]
                self.difficulty_click.play()
                self.state = "game"

    def generate_asteroid(self):
        self.asteroids.append(Asteroid(self.level_words))

    def move_asteroids(self):
        for asteroid in self.asteroids:
            asteroid.move_towards(self.player.rect.centerx, self.player.rect.centery)

    def remove_offscreen_asteroids(self):
        self.asteroids = [asteroid for asteroid in self.asteroids if asteroid.rect.y < HEIGHT]

    def handle_typing(self, input_text):
        for asteroid in self.asteroids:
            if asteroid.word == input_text:
                self.asteroids.remove(asteroid)
                self.score.increment()
                return True
        self.score.decrement()
        return False

    def run(self):
        generate_asteroid_event = pygame.USEREVENT + 1
        pygame.time.set_timer(generate_asteroid_event, 1000)  # Generate a new asteroid every 2 seconds
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "home":
                        self.handle_home_click(event.pos)
                    elif self.state == "character_selection":
                        self.handle_character_click(event.pos)
                    elif self.state == "difficulty_selection":
                        self.handle_difficulty_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event.pos)
                elif event.type == generate_asteroid_event and self.state == "game":
                    self.generate_asteroid()
                elif event.type == pygame.KEYDOWN and self.state == "game":
                    typed_text = self.textbox.handle_event(event)
                    if typed_text is not None:
                        self.handle_typing(typed_text)
                        self.textbox.text = ""

            if self.state == "home":
                self.home_screen()
            elif self.state == "character_selection":
                self.character_select()
            elif self.state == "difficulty_selection":
                self.difficulty_select()
            elif self.state == "game":
                self.move_asteroids()
                self.remove_offscreen_asteroids()
                self.game_screen()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
