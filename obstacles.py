import pygame
import random

# initialize Pygame
pygame.init()

# set up the window
background_image = pygame.image.load("background.png")
WIDTH = background_image.get_width()
HEIGHT = background_image.get_height()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Runner")

# set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# define the Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 50
        self.height = 50
        self.color = BLACK
        self.lives = 3
        self.current_position = "center"  # start at the center position
        self.rect = pygame.Rect(self.get_position_x(), HEIGHT - 50, self.width, self.height)
        self.speed = 5

    def get_position_x(self):
        if self.current_position == "left":
            return WIDTH // 4 - self.width // 2
        elif self.current_position == "right":
            return WIDTH * 3 // 4 - self.width // 2
        else:  # center
            return WIDTH / 2 - self.width / 2

    def move_left(self):
        if self.current_position == "center":
            self.current_position = "left"
            self.rect.x = self.get_position_x()
        elif self.current_position == "right":
            self.current_position = "center"
            self.rect.x = self.get_position_x() 

    def move_right(self):
        if self.current_position == "center":
            self.current_position = "right"
            self.rect.x = self.get_position_x() 
        elif self.current_position == "left":
            self.current_position = "center"
            self.rect.x = self.get_position_x()

    def update(self):
        # move the player left or right based on arrow key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move_left()
        elif keys[pygame.K_RIGHT]:
            self.move_right()

def size(s,b,d):
    return (d*b) / s
# define the Obstacle class
class Obstacle(pygame.sprite.Sprite):
    s_line = 34 / 2
    b_line = 752 / 2
    distance = 370
    side = (distance) / (1-(s_line/b_line))
    speed = 0.5
    def __init__(self, position, style):
        super().__init__()
        self.style = style
        self.position = position
        self.color = self.get_color()
        self.height = self.get_height()
        self.width = self.get_width()
        self.y = self.get_position_y()
        self.x = self.get_position_x()
    
    def get_color(self):
        if self.style == "stand":
            return BLUE
        elif self.style == "crouch":
            return BLACK
        else:
            return GREEN
    def get_height(self):
        initial_size = HEIGHT * 0.01
        if self.style == "stand":
            return initial_size
        else:  # Crouching or Jumping
            return initial_size / 2
        
    def get_width(self):
        if self.style == "stand":
            return self.height / 2
        else:  # Crouching or Jumping
            return self.height
    
    def get_position_y(self):
        start_point = HEIGHT - Obstacle.distance - self.height
        if self.style == "crouch":
            return start_point - self.height
        else:  # Standing or jumping
            return start_point
    
    def get_position_x(self):
        center_x = WIDTH / 2 - self.width / 2
        if self.position == "left":
            return center_x - self.width * 3.5
        elif self.position == "right":
            return center_x + self.width * 3.5
        else:  # center
            return center_x

    def update(self):
        start_point = HEIGHT - Obstacle.distance - self.height
        # move the obstacle down the screen
        self.y += Obstacle.speed + self.height / 100 
        d = (self.y - start_point) + (Obstacle.side - Obstacle.distance)
        rate = (size(Obstacle.side,Obstacle.b_line,d)) / (Obstacle.s_line)
        self.height = self.get_height() * rate
        self.width = self.get_width()
        self.x = self.get_position_x()
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

      



# create the sprites and groups
player = Player()
obstacles = pygame.sprite.Group()

# Set up the clock
clock = pygame.time.Clock()
spawn_time = 2000  # 2 seconds in milliseconds
last_spawn_time = pygame.time.get_ticks() - spawn_time

# set up the score
score = 0
font = pygame.font.SysFont(None, 36)


while player.lives > 0:
    # # handle events
    for event in pygame.event.get():
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     # Get the mouse position
        #     mouse_x, mouse_y = pygame.mouse.get_pos()
        #     print("Clicked at ({}, {})".format(mouse_x, mouse_y))
        pass

    # update the sprites
    player.update()
    obstacles.update()
    
    for obstacle in obstacles:
        if player.rect.colliderect(obstacle.get_rect()):
            # the player has collided with an obstacle, so lose a life
            player.lives -= 1
            if player.lives == 0:
                # player has no lives left, so end the game
                break
            obstacles.empty()
   

    # add obstacles
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time > spawn_time:
        last_spawn_time = current_time
        position = random.choice(["center","left","right"])
        style = random.choice(["stand","jump","crouch"])
        obstacle = Obstacle(position,style)
        obstacles.add(obstacle)
    
    # remove obstacles that have gone off the bottom of the screen
    for obstacle in obstacles:
        if obstacle.y > HEIGHT:
            obstacles.remove(obstacle)
            score += 5
            
    score += 0.01
    
    # draw the sprites and score to the screen
    screen.blit(background_image, (0, 0))
    for obstacle in obstacles:
        pygame.draw.rect(screen, obstacle.color, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
    screen.blit(font.render(f"Score: {int(score)}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (WIDTH - 100, 10))
    pygame.draw.rect(screen, player.color, player.rect)
            
    # pygame.display.flip()
    pygame.display.update()
    
    # control the frame rate
    clock.tick(90)
