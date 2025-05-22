import pygame
import tkinter as tk
from tkinter import messagebox
import sys
import random
import numpy as np

# --- Constants ---
WIDTH, HEIGHT = 600, 400
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10
WHITE = (240, 240, 240)
BLACK = (15, 15, 15)
RED = (255, 32, 32)
FPS = 60
PADDLE_SPEED = 6
BALL_SPEED = 6

# --- Sound (simple Atari-style beep using numpy) ---
def play_beep():
    freq = 440  # Hz
    duration = 60  # milliseconds
    sample_rate = 44100
    t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), False)
    wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))  # Square wave for Atari effect
    wave = (wave * 32767).astype(np.int16)
    sound = pygame.mixer.Sound(wave)
    sound.play()

# --- Pong Game Class ---
class PongGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pong - Cat-san Edition!')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Consolas', 36, bold=True)
        self.reset()
        self.running = True
        self.winner = None

    def reset(self):
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_dx = BALL_SPEED * random.choice((1, -1))
        self.ball_dy = BALL_SPEED * random.choice((1, -1))
        self.paddle_left_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle_right_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.score_left = 0
        self.score_right = 0
        self.winner = None
        self.running = True

    def draw(self):
        self.screen.fill(BLACK)
        # Draw paddles
        pygame.draw.rect(self.screen, WHITE, (10, self.paddle_left_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (WIDTH-20, self.paddle_right_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        # Draw ball
        pygame.draw.rect(self.screen, RED, (self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE))
        # Draw center line
        for i in range(10, HEIGHT, 30):
            pygame.draw.rect(self.screen, WHITE, (WIDTH//2-2, i, 4, 18))
        # Draw scores
        text_l = self.font.render(str(self.score_left), True, WHITE)
        text_r = self.font.render(str(self.score_right), True, WHITE)
        self.screen.blit(text_l, (WIDTH//4, 15))
        self.screen.blit(text_r, (3*WIDTH//4, 15))

    def update(self, mouse_y):
        # --- Player Paddle: Mouse Y ---
        self.paddle_right_y = max(0, min(HEIGHT-PADDLE_HEIGHT, mouse_y - PADDLE_HEIGHT//2))

        # --- AI Paddle: Track Ball ---
        if self.ball_y + BALL_SIZE//2 > self.paddle_left_y + PADDLE_HEIGHT//2:
            self.paddle_left_y += PADDLE_SPEED
        elif self.ball_y + BALL_SIZE//2 < self.paddle_left_y + PADDLE_HEIGHT//2:
            self.paddle_left_y -= PADDLE_SPEED
        self.paddle_left_y = max(0, min(HEIGHT-PADDLE_HEIGHT, self.paddle_left_y))

        # --- Ball Move ---
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # --- Ball Collisions ---
        # Top/bottom
        if self.ball_y <= 0 or self.ball_y >= HEIGHT-BALL_SIZE:
            self.ball_dy *= -1
            play_beep()
        # Paddle Right
        if (self.ball_x + BALL_SIZE >= WIDTH-20 and
            self.paddle_right_y < self.ball_y + BALL_SIZE and
            self.paddle_right_y + PADDLE_HEIGHT > self.ball_y):
            self.ball_dx *= -1
            play_beep()
        # Paddle Left
        if (self.ball_x <= 10 + PADDLE_WIDTH and
            self.paddle_left_y < self.ball_y + BALL_SIZE and
            self.paddle_left_y + PADDLE_HEIGHT > self.ball_y):
            self.ball_dx *= -1
            play_beep()

        # --- Scoring ---
        if self.ball_x < 0:
            self.score_right += 1
            play_beep()
            self.ball_x, self.ball_y = WIDTH//2, HEIGHT//2
            self.ball_dx = BALL_SPEED * random.choice((1, -1))
            self.ball_dy = BALL_SPEED * random.choice((1, -1))
        if self.ball_x > WIDTH:
            self.score_left += 1
            play_beep()
            self.ball_x, self.ball_y = WIDTH//2, HEIGHT//2
            self.ball_dx = BALL_SPEED * random.choice((1, -1))
            self.ball_dy = BALL_SPEED * random.choice((1, -1))

        # --- Game Over ---
        if self.score_left >= 5:
            self.running = False
            self.winner = 'AI Cat'
        if self.score_right >= 5:
            self.running = False
            self.winner = 'You'

    def run(self):
        root = tk.Tk()
        root.withdraw() # Hide main window
        while True:
            while self.running:
                mouse_y = pygame.mouse.get_pos()[1]
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        root.destroy()
                        sys.exit()
                self.update(mouse_y)
                self.draw()
                pygame.display.flip()
                self.clock.tick(FPS)
            # --- Game Over Dialog (tkinter) ---
            msg = f"Game Over! Winner: {self.winner}\nPlay again? (y/n)"
            ans = messagebox.askquestion("Game Over", msg)
            if ans == 'yes':
                self.reset()
            else:
                pygame.quit()
                root.destroy()
                sys.exit()

if __name__ == '__main__':
    PongGame().run()
