#!/usr/bin/env python3
"""
Classic Nokia 1100 Snake Game
A faithful recreation of the iconic mobile game
"""

import pygame
import sys
import random
import time
from enum import Enum
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 20  # Size of each grid cell
GRID_WIDTH = 20  # 20 cells wide
GRID_HEIGHT = 20  # 20 cells tall
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE + 60  # Extra space for UI
FPS = 10

# Colors (Modified: dark background, red snake)
BACKGROUND = (20, 20, 40)  # Dark blue-grey
SNAKE_COLOR = (255, 0, 0)  # Bright red
FOOD_COLOR = (255, 255, 255)  # White
BORDER_COLOR = (100, 100, 150)  # Light grey-blue
TEXT_COLOR = (200, 200, 255)  # Light blue
DEATH_COLOR = (255, 0, 0)  # Red

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SNAKE - Nokia 1100")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Menu and game state
        self.menu_active = True
        self.selected_level = 1

        # UI buttons (filled in init)
        self.menu_buttons = {}

        # Apple / orange mechanics (initialize before spawn_food is used)
        self.apples_eaten_since_orange = 0
        self.orange_active = False
        self.orange_pos = None
        self.orange_spawn_time = 0.0
        self.orange_duration = 5.0  # seconds until orange value decays to minimum

        self.reset_game()
        self.difficulty = 1
        self.game_over_message = None
        self.game_paused = False
    
    def reset_game(self):
        # Initialize snake in the middle of the screen
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.game_over_message = None
    
    def spawn_food(self) -> Tuple[int, int]:
        """Spawn food at a random location not occupied by snake"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake and (not self.orange_active or (x, y) != self.orange_pos):
                return (x, y)

    def spawn_orange(self) -> Tuple[int, int]:
        """Spawn orange at a random location not occupied by snake or food"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake and (x, y) != self.food:
                return (x, y)
    
    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            # Menu handling with mouse and keys
            if self.menu_active:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # Play button
                    if self.menu_buttons.get('play') and self.menu_buttons['play'].collidepoint(mx, my):
                        self.menu_active = False
                        self.reset_game()
                    # Quit
                    if self.menu_buttons.get('quit') and self.menu_buttons['quit'].collidepoint(mx, my):
                        return False
                    # Level buttons
                    for key in ('lvl1', 'lvl2', 'lvl3'):
                        if self.menu_buttons.get(key) and self.menu_buttons[key].collidepoint(mx, my):
                            self.selected_level = int(key[-1])
                            self.difficulty = self.selected_level
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.menu_active = False
                        self.reset_game()
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.selected_level = int(pygame.key.name(event.key))
                        self.difficulty = self.selected_level
                continue

            if event.type == pygame.KEYDOWN:
                # Direction controls
                if event.key in (pygame.K_UP, pygame.K_w):
                    if self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                
                # Game controls
                elif event.key == pygame.K_SPACE:
                    self.game_paused = not self.game_paused
                elif event.key == pygame.K_r:
                    self.reset_game()
                    self.game_paused = False
                elif event.key == pygame.K_1:
                    self.difficulty = 1
                    self.reset_game()
                    self.game_paused = False
                elif event.key == pygame.K_2:
                    self.difficulty = 2
                    self.reset_game()
                    self.game_paused = False
                elif event.key == pygame.K_3:
                    self.difficulty = 3
                    self.reset_game()
                    self.game_paused = False
        
        return True
    
    def update(self):
        if self.game_over or self.game_paused:
            return
        
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over = True
            self.game_over_message = "WALL COLLISION"
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            self.game_over_message = "SELF COLLISION"
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food:
            self.score += 10 * self.difficulty
            self.food = self.spawn_food()
            # Track apples eaten; spawn orange after 5 apples
            self.apples_eaten_since_orange += 1
            if self.apples_eaten_since_orange >= 5 and not self.orange_active:
                self.orange_pos = self.spawn_orange()
                self.orange_active = True
                self.orange_spawn_time = time.time()
                self.apples_eaten_since_orange = 0
        else:
            # Remove tail if no food eaten
            self.snake.pop()

        # Check orange collision
        if self.orange_active and new_head == self.orange_pos:
            # Compute orange score based on time since spawn (decays linearly from 50 to 5)
            elapsed = time.time() - self.orange_spawn_time
            frac = min(max(elapsed / self.orange_duration, 0.0), 1.0)
            orange_score = max(5, int(50 - frac * 45))
            self.score += orange_score
            # Give a small length bonus
            for _ in range(2):
                self.snake.append(self.snake[-1])
            self.orange_active = False
            self.orange_pos = None
            self.orange_spawn_time = 0.0
    
    def draw(self):
        self.screen.fill(BACKGROUND)
        # If menu active, draw menu and return
        if self.menu_active:
            self.draw_menu()
            pygame.display.flip()
            return
        
        # Draw border
        pygame.draw.rect(self.screen, BORDER_COLOR, 
                        (0, 0, SCREEN_WIDTH, GRID_HEIGHT * GRID_SIZE), 2)
        
        # Draw food
        # Draw apple as circle
        ax = self.food[0] * GRID_SIZE + GRID_SIZE // 2
        ay = self.food[1] * GRID_SIZE + GRID_SIZE // 2
        pygame.draw.circle(self.screen, FOOD_COLOR, (ax, ay), GRID_SIZE // 2 - 4)

        # Draw orange if active (bigger circle)
        if self.orange_active and self.orange_pos:
            ox = self.orange_pos[0] * GRID_SIZE + GRID_SIZE // 2
            oy = self.orange_pos[1] * GRID_SIZE + GRID_SIZE // 2
            pygame.draw.circle(self.screen, (255, 140, 0), (ox, oy), GRID_SIZE // 2)
            pygame.draw.circle(self.screen, (200, 100, 0), (ox, oy), GRID_SIZE // 2, 2)
        
        # Draw snake as rounded body (circles + midpoint circles to hide grid)
        for i, (x, y) in enumerate(self.snake):
            cx = x * GRID_SIZE + GRID_SIZE // 2
            cy = y * GRID_SIZE + GRID_SIZE // 2
            # Head color slightly different
            color = (255, 100, 100) if i == 0 else SNAKE_COLOR
            # Draw circle for segment
            pygame.draw.circle(self.screen, color, (cx, cy), GRID_SIZE // 2 - 1)

            # Draw midpoint circle between this and next segment to fully cover grid lines
            if i + 1 < len(self.snake):
                nx, ny = self.snake[i + 1]
                ncx = nx * GRID_SIZE + GRID_SIZE // 2
                ncy = ny * GRID_SIZE + GRID_SIZE // 2
                midx = (cx + ncx) // 2
                midy = (cy + ncy) // 2
                pygame.draw.circle(self.screen, color, (midx, midy), GRID_SIZE // 2 - 1)

            # Draw eyes on head
            if i == 0:
                eye_color = (0, 0, 0)
                ex_offset = GRID_SIZE // 4
                ey_offset = GRID_SIZE // 6
                if self.direction == Direction.RIGHT:
                    pygame.draw.circle(self.screen, eye_color, (cx + ex_offset, cy - ey_offset), 2)
                    pygame.draw.circle(self.screen, eye_color, (cx + ex_offset, cy + ey_offset), 2)
                elif self.direction == Direction.LEFT:
                    pygame.draw.circle(self.screen, eye_color, (cx - ex_offset, cy - ey_offset), 2)
                    pygame.draw.circle(self.screen, eye_color, (cx - ex_offset, cy + ey_offset), 2)
                elif self.direction == Direction.UP:
                    pygame.draw.circle(self.screen, eye_color, (cx - ey_offset, cy - ex_offset), 2)
                    pygame.draw.circle(self.screen, eye_color, (cx + ey_offset, cy - ex_offset), 2)
                elif self.direction == Direction.DOWN:
                    pygame.draw.circle(self.screen, eye_color, (cx - ey_offset, cy + ex_offset), 2)
                    pygame.draw.circle(self.screen, eye_color, (cx + ey_offset, cy + ex_offset), 2)
        
        # Draw UI background
        pygame.draw.rect(self.screen, (30, 30, 50), 
                        (0, GRID_HEIGHT * GRID_SIZE, SCREEN_WIDTH, 60))
        
        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, GRID_HEIGHT * GRID_SIZE + 5))
        
        # Draw difficulty
        diff_text = self.font.render(f"LEVEL: {self.difficulty}", True, TEXT_COLOR)
        self.screen.blit(diff_text, (SCREEN_WIDTH - 150, GRID_HEIGHT * GRID_SIZE + 5))
        
        # Draw snake length
        length_text = self.font.render(f"LENGTH: {len(self.snake)}", True, TEXT_COLOR)
        self.screen.blit(length_text, (10, GRID_HEIGHT * GRID_SIZE + 30))
        
        # Draw pause status
        if self.game_paused:
            pause_text = self.large_font.render("PAUSED", True, TEXT_COLOR)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, BACKGROUND, pause_rect.inflate(20, 20))
            self.screen.blit(pause_text, pause_rect)
        
        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = self.large_font.render("GAME OVER", True, DEATH_COLOR)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(game_over_text, game_over_rect)
            
            # Reason
            reason_text = self.font.render(self.game_over_message, True, TEXT_COLOR)
            reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(reason_text, reason_rect)
            
            # Final score
            final_score_text = self.font.render(f"FINAL SCORE: {self.score}", True, TEXT_COLOR)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(final_score_text, final_score_rect)
            
            # Instructions
            restart_text = self.font.render("PRESS R TO RESTART", True, TEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
            self.screen.blit(restart_text, restart_rect)
        
        # Draw instructions on bottom right
        inst_text = self.font.render("SPACE: Pause | R: Restart | 1-3: Level", True, TEXT_COLOR)
        self.screen.blit(inst_text, (SCREEN_WIDTH - 280, GRID_HEIGHT * GRID_SIZE + 30))
        
        pygame.display.flip()

    def draw_menu(self):
        # Background for menu (slightly different shade)
        self.screen.fill((30, 30, 60))

        # Title
        title = self.large_font.render("SNAKE", True, (180, 255, 180))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Subtitle / instructions
        subtitle = self.font.render("Classic Nokia-style snake – select options below", True, TEXT_COLOR)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle, sub_rect)

        # Buttons
        btn_w, btn_h = 220, 48
        cx = SCREEN_WIDTH // 2
        start_y = 180

        play_rect = pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h)
        lvl1_rect = pygame.Rect(cx - btn_w // 2, start_y + 70, 70, 40)
        lvl2_rect = pygame.Rect(cx - 35, start_y + 70, 70, 40)
        lvl3_rect = pygame.Rect(cx + btn_w // 2 - 70, start_y + 70, 70, 40)
        quit_rect = pygame.Rect(cx - btn_w // 2, start_y + 140, btn_w, btn_h)

        # Store for input handling
        self.menu_buttons['play'] = play_rect
        self.menu_buttons['lvl1'] = lvl1_rect
        self.menu_buttons['lvl2'] = lvl2_rect
        self.menu_buttons['lvl3'] = lvl3_rect
        self.menu_buttons['quit'] = quit_rect

        # Draw main Play button
        pygame.draw.rect(self.screen, BORDER_COLOR, play_rect)
        play_text = self.font.render("PLAY", True, TEXT_COLOR)
        play_text_rect = play_text.get_rect(center=play_rect.center)
        self.screen.blit(play_text, play_text_rect)

        # Draw level buttons, highlight selected
        for idx, r in enumerate((lvl1_rect, lvl2_rect, lvl3_rect), start=1):
            fill = (30, 90, 30) if self.selected_level == idx else (0, 76, 0)
            pygame.draw.rect(self.screen, fill, r)
            pygame.draw.rect(self.screen, BORDER_COLOR, r, 2)
            t = self.font.render(str(idx), True, TEXT_COLOR)
            tr = t.get_rect(center=r.center)
            self.screen.blit(t, tr)

        # Draw Quit button
        pygame.draw.rect(self.screen, BORDER_COLOR, quit_rect)
        quit_text = self.font.render("QUIT", True, TEXT_COLOR)
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        self.screen.blit(quit_text, quit_text_rect)

        # Hint
        hint = self.font.render("Press ENTER to start | 1-3 to choose level", True, TEXT_COLOR)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(hint, hint_rect)
    
    def run(self):
        running = True
        
        # Speed adjustments based on difficulty
        fps_map = {1: 8, 2: 10, 3: 13}
        
        while running:
            running = self.handle_input()
            # If menu active, run at a steady menu FPS for smooth UI
            if self.menu_active:
                self.clock.tick(30)
            else:
                # Adjust FPS based on difficulty
                self.clock.tick(fps_map[self.difficulty])
            
            if running:
                self.update()
                self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
