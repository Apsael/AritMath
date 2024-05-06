import os
import pygame
import random
from PIL import Image, ImageDraw, ImageFont #pip install Pillow

# Initialize Pygame
pygame.init()

# Set the dimensions of the game window
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AritMath")

# Get the script's directory
current_dir = os.path.dirname(__file__)

# Path to assets
assets_dir = os.path.join(current_dir, "Assets")

# Relative paths to resources
bg_images = [pygame.image.load(os.path.join(assets_dir, f"images/bg/bg_{random.randint(1, 5)}.png"))]
balloon_image = pygame.image.load(os.path.join(assets_dir, "images/balloon.png"))

# Load cursor assets
gun_sight_image_path = os.path.join(assets_dir, "images/gun_sight.png")
gun_sight_surface = pygame.image.load(gun_sight_image_path)
gun_sight_cursor = pygame.cursors.Cursor((0, 0), gun_sight_surface)
pygame.mouse.set_cursor(gun_sight_cursor)


# Load button images for level selection
lvl1_image = pygame.image.load(os.path.join(assets_dir, "images/lvl1.png"))
lvl2_image = pygame.image.load(os.path.join(assets_dir, "images/lvl2.png"))
lvl3_image = pygame.image.load(os.path.join(assets_dir, "images/lvl3.png"))
lvl4_image = pygame.image.load(os.path.join(assets_dir, "images/lvl4.png"))
lvl5_image = pygame.image.load(os.path.join(assets_dir, "images/lvl5.png"))

# Load other images
heart_image = pygame.image.load(os.path.join(assets_dir, "images/heart.png"))
credit_image = pygame.image.load(os.path.join(assets_dir, "images/credit.png"))
start_button = pygame.image.load(os.path.join(assets_dir, "images/start_button.png"))
start_button_pressed = pygame.image.load(os.path.join(assets_dir, "images/start_button_pressed.png"))
quit_button = pygame.image.load(os.path.join(assets_dir, "images/quit_button.png"))
quit_button_pressed = pygame.image.load(os.path.join(assets_dir, "images/quit_button_pressed.png"))
game_over = pygame.image.load(os.path.join(assets_dir, "images/game_over.png"))
continue_button = pygame.image.load(os.path.join(assets_dir, "images/continue_button.png"))

# Load sounds and background music
pygame.mixer.music.load(os.path.join(assets_dir, "music/background_music.mp3"))
balloon_sound = pygame.mixer.Sound(os.path.join(assets_dir, "sounds/balloon_sound.wav"))
pop_sound = pygame.mixer.Sound(os.path.join(assets_dir, "sounds/pop_sound.wav"))
correct_sound = pygame.mixer.Sound(os.path.join(assets_dir, "sounds/correct_sound.wav"))
incorrect_sound = pygame.mixer.Sound(os.path.join(assets_dir, "sounds/incorrect_sound.wav"))

# Global dictionary to store best scores for each level
best_scores = {
    "Level1": 0,
    "Level2": 0,
    "Level3": 0,
    "Level4": 0,
    "Level5": 0,
}

# Define scenes
class Scene:
    def handle_event(self, event):
        pass
    
    def update(self):
        pass
    
    def draw(self, screen):
        pass

# Main menu scene
class MainMenuScene(Scene):
    def __init__(self):
        super().__init__()
        self.start_button_rect = pygame.Rect(300, 250, 200, 100)  # Centered
        self.quit_button_rect = pygame.Rect(700, 10, 90, 50)  # Top right

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.start_button_rect.collidepoint(x, y):
                pygame.mixer.Sound.play(correct_sound)  # Play sound on click
                return LevelOptions()
            elif self.quit_button_rect.collidepoint(x, y):
                return None  # End game
        return self  # Stay in this scene

    def draw(self, screen):
        screen.blit(random.choice(bg_images), (0, 0))
        screen.blit(start_button, self.start_button_rect.topleft)
        screen.blit(quit_button, self.quit_button_rect.topleft)
        screen.blit(credit_image, (10, 10))

# Base scene with common functionality for all game levels
class BaseLevelScene(pygame.sprite.Sprite):
    def __init__(self, timer_duration, best_scores, level_name):
        super().__init__()
        self.timer_duration = timer_duration
        self.best_scores = best_scores
        self.level_name = level_name
        self.score = 0
        self.lives = 3
        self.generate_operation()

    def reset_timer(self):
        self.start_time = pygame.time.get_ticks()

    def update(self):
        # Calculate elapsed time
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= self.timer_duration:
            pygame.mixer.Sound.play(incorrect_sound)  # Play when timer expires
            self.lives -= 1
            if self.lives == 0:
                return GameOverScene(self.score)  # Game over if no lives left
            self.generate_operation()  # Generate new operation if timer expires

        # Update balloon positions
        for idx, rect in enumerate(self.balloon_positions):
            direction = self.balloon_directions[idx]
            rect.y += direction
            if rect.y <= 200 and direction == -1:  # Hit upper limit
                self.balloon_directions[idx] = 1  # Change direction to down
            elif rect.y >= 400 and direction == 1:  # Hit lower limit
                self.balloon_directions[idx] = -1  # Change direction to up
        
        return self  # Stay in this scene

    def draw(self, screen):
        screen.blit(random.choice(bg_images), (0, 0))
        font = pygame.font.Font(None, 50)
        operation_text = font.render(self.current_operation, True, (0, 0, 0))
        screen.blit(operation_text, (331, 150))  # Centered text
        
        # Draw balloons with answers
        for idx, rect in enumerate(self.balloon_positions):
            screen.blit(balloon_image, rect.topleft)
            answer_text = font.render(str(self.balloon_answers[idx]), True, (255, 255, 255))
            screen.blit(answer_text, (rect.centerx - 20, rect.centery - 30))
        
        # Draw score and best score
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        best_score_text = font.render(f"Best: {self.best_scores[self.level_name]}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(best_score_text, (200, 10))
        
        # Draw hearts (lives)
        heart_width = 40
        heart_positions = [(700 + heart_width * i, 10) for i in range(self.lives)]
        for pos in heart_positions:
            screen.blit(heart_image, pos)  # Draw hearts for lives
        
        # Draw timer
        elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining_time = max(0, self.timer_duration / 1000 - elapsed_seconds)
        timer_text = font.render(f"Time: {remaining_time:.1f}", True, (0, 0, 0))
        screen.blit(timer_text, (10, 60))  # Draw timer

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            for idx, rect in enumerate(self.balloon_positions):
                if rect.collidepoint(x, y):
                    if self.balloon_answers[idx] == self.correct_answer:
                        pygame.mixer.Sound.play(correct_sound)  # Play sound on correct answer
                        self.score += 1
                        if self.score > self.best_scores[self.level_name]:
                            self.best_scores[self.level_name] = self.score  # Update best score
                        self.generate_operation()  # Generate new operation
                    else:
                        pygame.mixer.Sound.play(incorrect_sound)  # Play sound on incorrect answer
                        self.lives -= 1
                        self.balloon_positions.pop(idx)  # Remove the wrong balloon
                        self.balloon_answers.pop(idx)
                    if self.lives == 0:
                        return GameOverScene(self.score)  # Game over if no lives left
        return self  # Stay in the scene

# Game over scene
class GameOverScene(Scene):
    def __init__(self, score):
        super().__init__()
        self.score = score
        self.continue_button_rect = pygame.Rect(300, 400, 200, 50)  # Centered
        self.quit_button_rect = pygame.Rect(550, 400, 200, 50)  # Next to it

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.continue_button_rect.collidepoint(x, y):
                return MainMenuScene()  # Return to main menu
            elif self.quit_button_rect.collidepoint(x, y):
                return None  # End game
        return self  # Stay in this scene

    def draw(self, screen):
        screen.blit(random.choice(bg_images), (0, 0))
        screen.blit(game_over, (300, 200))  # Centered game over image
        font = pygame.font.Font(None, 50)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (350, 100))  # Score displayed
        screen.blit(continue_button, self.continue_button_rect.topleft)
        screen.blit(quit_button, self.quit_button_rect.topleft)

# Scene for Level Selection (LevelOptions)
class LevelOptions(Scene):
    def __init__(self):
        super().__init__()
        self.button_rects = []
        self.button_images = [lvl1_image, lvl2_image, lvl3_image, lvl4_image, lvl5_image]
        
        # Position the buttons from left to right and centered vertically
        button_width = 120
        button_height = 80
        start_x = 69
        y = (HEIGHT - button_height) // 2  # Centered on Y-axis
        for img in self.button_images:
            self.button_rects.append(pygame.Rect(start_x, y, button_width, button_height))
            start_x += button_width + 20  # Spacing between buttons

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            for idx, rect in enumerate(self.button_rects):
                if rect.collidepoint(x, y):
                    # Go to the selected level
                    if idx == 0:
                        return Level1()
                    elif idx == 1:
                        return Level2()
                    elif idx == 2:
                        return Level3()
                    elif idx == 3:
                        return Level4()
                    elif idx == 4:
                        return Level5()
        return self  # Stay in this scene
    
    def draw(self, screen):
        screen.blit(random.choice(bg_images), (0, 0))
        for idx, img in enumerate(self.button_images):
            screen.blit(img, self.button_rects[idx].topleft)

# Individual Level Scenes
class Level1(BaseLevelScene):
    def __init__(self):
        super().__init__(5000, best_scores, "Level1")  # 5 seconds for addition
    
    def generate_operation(self):
        self.reset_timer()
        A = random.randint(1, 99)
        B = random.randint(1, 99)
        self.current_operation = f"{A} + {B} = ?"
        self.correct_answer = A + B
        self.generate_answers()

    def generate_answers(self):
        possible_answers = [self.correct_answer]
        while len(possible_answers) < 6:
            ans = random.randint(1, 198)
            if ans not in possible_answers:
                possible_answers.append(ans)
        random.shuffle(possible_answers)
        self.setup_balloons(possible_answers)

    def setup_balloons(self, possible_answers):
        self.balloon_positions = []
        self.balloon_answers = []
        self.balloon_directions = []
        start_x = 50
        y = 300
        for ans in possible_answers:
            rect = pygame.Rect(start_x, y, 80, 120)
            self.balloon_positions.append(rect)
            self.balloon_answers.append(ans)
            self.balloon_directions.append(1 if len(self.balloon_positions) % 2 == 0 else -1)
            start_x += 120  # Spacing between balloons        

class Level2(BaseLevelScene):
    def __init__(self):
        super().__init__(5000, best_scores, "Level2")  # 5 seconds for subtraction
    
    def generate_operation(self):
        self.reset_timer()  # Reset timer when generating new operations
        A = random.randint(10, 99)
        B = random.randint(1, A - 1)
        self.current_operation = f"{A} - {B} = ?"
        self.correct_answer = A - B
        self.generate_answers()
    
    def generate_answers(self):
        possible_answers = [self.correct_answer]
        while len(possible_answers) < 6:
            ans = random.randint(1, 198)
            if ans not in possible_answers:
                possible_answers.append(ans)
        random.shuffle(possible_answers)
        self.setup_balloons(possible_answers)

    def setup_balloons(self, possible_answers):
        self.balloon_positions = []
        self.balloon_answers = []
        self.balloon_directions = []
        start_x = 50
        y = 300
        for ans in possible_answers:
            rect = pygame.Rect(start_x, y, 80, 120)
            self.balloon_positions.append(rect)
            self.balloon_answers.append(ans)
            self.balloon_directions.append(1 if len(self.balloon_positions) % 2 == 0 else -1)
            start_x += 120  # Spacing between balloons
     
# Level 3 (Multiplication)
class Level3(BaseLevelScene):
    def __init__(self):
        super().__init__(10000, best_scores, "Level2")  # 10 seconds for multiplication
    
    def generate_operation(self):
        self.reset_timer()
        A = random.randint(1, 9)  # Multiplicand
        B = random.randint(1, 9)  # Multiplier
        self.current_operation = f"{A} * {B} = ?"
        self.correct_answer = A * B
        self.generate_answers()
    
    def generate_answers(self):
        possible_answers = [self.correct_answer]
        while len(possible_answers) < 6:
            ans = random.randint(1, 198)
            if ans not in possible_answers:
                possible_answers.append(ans)
        random.shuffle(possible_answers)
        self.setup_balloons(possible_answers)

    def setup_balloons(self, possible_answers):
        self.balloon_positions = []
        self.balloon_answers = []
        self.balloon_directions = []
        start_x = 50
        y = 300
        for ans in possible_answers:
            rect = pygame.Rect(start_x, y, 80, 120)
            self.balloon_positions.append(rect)
            self.balloon_answers.append(ans)
            self.balloon_directions.append(1 if len(self.balloon_positions) % 2 == 0 else -1)
            start_x += 120  # Spacing between balloons        

# Level 4 (Division)
class Level4(BaseLevelScene):
    def __init__(self):
        super().__init__(10000, best_scores, "Level2")  # 10 seconds for multiplication
    
    def generate_operation(self):
        self.reset_timer()
        A = random.randint(10, 99)  # Dividend
        B = random.randint(1, 9)  # Divisor
        A = A - (A % B)  # Ensure clean division without remainders
        self.current_operation = f"{A} / {B} = ?"
        self.correct_answer = A // B  # Quotient
        self.generate_answers()
    
    def generate_answers(self):
        possible_answers = [self.correct_answer]
        while len(possible_answers) < 6:
            ans = random.randint(1, 198)
            if ans not in possible_answers:
                possible_answers.append(ans)
        random.shuffle(possible_answers)
        self.setup_balloons(possible_answers)

    def setup_balloons(self, possible_answers):
        self.balloon_positions = []
        self.balloon_answers = []
        self.balloon_directions = []
        start_x = 50
        y = 300
        for ans in possible_answers:
            rect = pygame.Rect(start_x, y, 80, 120)
            self.balloon_positions.append(rect)
            self.balloon_answers.append(ans)
            self.balloon_directions.append(1 if len(self.balloon_positions) % 2 == 0 else -1)
            start_x += 120  # Spacing between balloons          

# Level 5 (Random)
class Level5(BaseLevelScene):
    def __init__(self):
        super().__init__(5000, best_scores, "Level5")  # Random operation
        self.generate_operation()  # Initialize the first operation

    def generate_operation(self):
        # Randomly select an operation and set correct_answer
        operation_types = ["+", "-", "*", "/"]
        op_type = random.choice(operation_types)
        self.reset_timer()

        # Set timer duration based on operation type
        if op_type in ["+", "-"]:
            self.timer_duration = 5000  # 5 seconds for addition and subtraction
        elif op_type in ["*", "/"]:
            self.timer_duration = 10000  # 10 seconds for multiplication and division

        # Generate the correct operation and the correct answer
        if op_type == "+":
            A = random.randint(1, 99)
            B = random.randint(1, 99)
            self.current_operation = f"{A} + {B} = ?"
            self.correct_answer = A + B
            self.generate_answers()
        elif op_type == "-":
            A = random.randint(10, 99)
            B = random.randint(1, A - 1)
            self.current_operation = f"{A} - {B} = ?"
            self.correct_answer = A - B
            self.generate_answers()
        elif op_type == "*":
            A = random.randint(1, 9)
            B = random.randint(1, 9)
            self.current_operation = f"{A} * {B} = ?"
            self.correct_answer = A * B
            self.generate_answers()            
        elif op_type == "/":
            A = random.randint(10, 99)
            B = random.randint(1, 9)
            A = A - (A % B)  # Ensure clean division
            self.current_operation = f"{A} / {B} = ?"
            self.correct_answer = A // B
            self.generate_answers()            

    def generate_answers(self):
        possible_answers = [self.correct_answer]
        while len(possible_answers) < 6:
            ans = random.randint(1, 198)
            if ans not in possible_answers:
                possible_answers.append(ans)
        random.shuffle(possible_answers)
        self.setup_balloons(possible_answers)

    def setup_balloons(self, possible_answers):
        self.balloon_positions = []
        self.balloon_answers = []
        self.balloon_directions = []
        start_x = 50
        y = 300
        for ans in possible_answers:
            rect = pygame.Rect(start_x, y, 80, 120)
            self.balloon_positions.append(rect)
            self.balloon_answers.append(ans)
            self.balloon_directions.append(1 if len(self.balloon_positions) % 2 == 0 else -1)
            start_x += 120  # Spacing between balloons 

# Main game loop
current_scene = MainMenuScene()  # Start with main menu
pygame.mixer.music.play(-1)  # Play background music in loop
while current_scene:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            current_scene = None
        else:
            current_scene = current_scene.handle_event(event)
    
    # Update and draw the current scene
    if current_scene:
        current_scene.update()
        current_scene.draw(win)
        pygame.display.update()

# Quit Pygame
pygame.quit()