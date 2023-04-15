import pygame
import random
import cv2
import numpy as np
from math import hypot
import mediapipe as mp
import string
from csv import writer
import time

# initialize Pygame
pygame.init()

# set up the window
background_image = pygame.image.load("background.png")
WIDTH = background_image.get_width()
HEIGHT = background_image.get_height()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
video = cv2.VideoCapture("background2.mp4")
success, video_image = video.read()
video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

fps = video.get(cv2.CAP_PROP_FPS)

window = pygame.display.set_mode(video_image.shape[1::-1])
pygame.display.set_caption("Endless Runner")

# set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

### SETTING UP THE MOTION DETECTION

mp_pose = mp.solutions.pose
 
# Setup the Pose function for images.
pose_image = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=1)
 
# Setup the Pose function for videos.
pose_video = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.7,
                          min_tracking_confidence=0.7)
 
# Initialize mediapipe drawing class.
mp_drawing = mp.solutions.drawing_utils 


def detectPose(image, pose): 

    # Convert the image from BGR into RGB format.
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Perform the Pose Detection.
    results = pose.process(imageRGB)
    # Check if any landmarks are detected and are specified to be drawn.
    return results
    

def checkHandsJoined(image, results):    
    # Get the height and width of the input image.
    height, width, _ = image.shape

    # Get the left wrist landmark x and y coordinates.
    left_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * width,
                          results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * height)

    # Get the right wrist landmark x and y coordinates.
    right_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * width,
                           results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * height)
    
    # Calculate the euclidean distance between the left and right wrist.
    euclidean_distance = int(hypot(left_wrist_landmark[0] - right_wrist_landmark[0],
                                   left_wrist_landmark[1] - right_wrist_landmark[1]))
    # Compare the distance between the wrists with a appropriate threshold to check if both hands are joined.
    if euclidean_distance < 130:  
        # Set the hands status to joined.
        hand_status = 'Hands Joined'
    else:   
        # Set the hands status to not joined.
        hand_status = 'Hands Not Joined' 
    
        # Return the output image and the classified hands status indicating whether the hands are joined or not.
    return hand_status

def checkJumpCrouch(image, results, MID_Y):
    # Get the height and width of the image.
    height, width, _ = image.shape
    
    # Retreive the y-coordinate of the left shoulder landmark.
    left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height)
 
    # Retreive the y-coordinate of the right shoulder landmark.
    right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height)
 
    # Calculate the y-coordinate of the mid-point of both shoulders.
    actual_mid_y = abs(right_y + left_y) // 2
    
    # Get the left wrist landmark x and y coordinates.
    left_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * height)
 
    # Get the right wrist landmark x and y coordinates.
    right_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * height)
    
    # Calculate the upper and lower bounds of the threshold.
    lower_bound = MID_Y - WIDTH / 17
    hands_lower_bound = MID_Y - WIDTH / 6
    upper_bound = MID_Y + WIDTH / 8.65
    
    # Check if the person has jumped that is when the y-coordinate of the mid-point 
    # of both shoulders is less than the lower bound.
    if (actual_mid_y < lower_bound) and (right_wrist_landmark < hands_lower_bound and left_wrist_landmark < hands_lower_bound):
        
        # Set the posture to jumping.
        posture = 'Jumping'
    
    # Check if the person has crouched that is when the y-coordinate of the mid-point 
    # of both shoulders is greater than the upper bound.
    elif (actual_mid_y > upper_bound):
        
        # Set the posture to crouching.
        posture = 'Crouching'
    
    # Otherwise the person is standing and the y-coordinate of the mid-point 
    # of both shoulders is between the upper and lower bounds.    
    else:
        
        # Set the posture to Standing straight.
        posture = 'Standing'
        
 
        # Return the output image and posture indicating whether the person is standing straight or has jumped, or crouched.
    return posture
    

def checkLeftRight(image, results):

    # Declare a variable to store the horizontal position (left, center, right) of the person.
    horizontal_position = None
    
    # Get the height and width of the image.
    height, width, _ = image.shape
    
    # Retreive the x-coordinate of the left shoulder landmark.
    left_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width)

    # Retreive the x-corrdinate of the right shoulder landmark.
    right_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * width)
    
    # Check if the person is at left that is when both shoulder landmarks x-corrdinates
    # are less than or equal to the x-corrdinate of the center of the image.
    margin = WIDTH / 10
    left_boundry = width//2 - margin
    right_boundry = width//2 + margin
    if (right_x <= left_boundry and left_x <= left_boundry):
        
        # Set the person's position to left.
        horizontal_position = 'Left'

    # Check if the person is at right that is when both shoulder landmarks x-corrdinates
    # are greater than or equal to the x-corrdinate of the center of the image.
    elif (right_x >= right_boundry and left_x >= right_boundry):
        
        # Set the person's position to right.
        horizontal_position = 'Right'
    
    # Check if the person is at center that is when right shoulder landmark x-corrdinate is greater than or equal to
    # and left shoulder landmark x-corrdinate is less than or equal to the x-corrdinate of the center of the image.
    # elif (right_x >= width//2 and left_x <= width//2):
    else:
        
        # Set the person's position to center.
        horizontal_position = 'Center'
        

        # Return the output image and the person's horizontal position.
    return horizontal_position

# define the Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 110
        self.height = 340
        self.pos_x =  WIDTH / 2 - self.width / 3
        self.pos_y = 340
        self.color = BLACK
        self.lives = 3
        self.current_position = "center"  # start at the center position
        self.speed = 5
        self.attack_animation = False
        self.sprites = []
        self.sprites.append(pygame.image.load('character_sprite/0001.png'))
        self.sprites.append(pygame.image.load('character_sprite/0002.png'))
        self.sprites.append(pygame.image.load('character_sprite/0003.png'))
        self.sprites.append(pygame.image.load('character_sprite/0004.png'))
        self.sprites.append(pygame.image.load('character_sprite/0005.png'))
        self.sprites.append(pygame.image.load('character_sprite/0006.png'))
        self.sprites.append(pygame.image.load('character_sprite/0007.png'))
        self.sprites.append(pygame.image.load('character_sprite/0008.png'))
        self.sprites.append(pygame.image.load('character_sprite/0009.png'))
        self.sprites.append(pygame.image.load('character_sprite/0010.png'))
        self.sprites.append(pygame.image.load('character_sprite/0011.png'))
        self.sprites.append(pygame.image.load('character_sprite/0012.png'))
        self.sprites.append(pygame.image.load('character_sprite/0013.png'))
        self.sprites.append(pygame.image.load('character_sprite/0014.png'))
        self.sprites.append(pygame.image.load('character_sprite/0015.png'))
        self.sprites.append(pygame.image.load('character_sprite/0016.png'))
        self.sprites.append(pygame.image.load('character_sprite/0017.png'))
        self.sprites.append(pygame.image.load('character_sprite/0018.png'))
        self.sprites.append(pygame.image.load('character_sprite/0019.png'))
        self.sprites.append(pygame.image.load('character_sprite/0020.png'))
        self.sprites.append(pygame.image.load('character_sprite/0021.png'))
        self.sprites.append(pygame.image.load('character_sprite/0022.png'))
        self.sprites.append(pygame.image.load('character_sprite/0023.png'))
        self.sprites.append(pygame.image.load('character_sprite/0024.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = pygame.Rect(self.get_position_x(), HEIGHT - 50, 50, 50)
        self.rect.topleft = [self.pos_x,self.pos_y]

        #smaller hitbox rectangle - only goes to bottom 1/4 of character
        self.hitbox = pygame.Rect( self.get_position_x(), HEIGHT-50, 80, 80)
        self.hitbox.topleft = [self.pos_x+15,HEIGHT-120]
            
    def get_position_x(self):
        if self.current_position == "left":
            return WIDTH // 2.5 - self.width
        elif self.current_position == "right":
            return WIDTH * 2.5 // 4 - self.width // 2
        else:  # center
            return WIDTH/2 - self.width/3
        
    def move_left(self):
        if self.current_position == "center":
            self.current_position = "left"
            self.rect.x = self.get_position_x()
            self.hitbox.x = self.get_position_x()+15
        elif self.current_position == "right":
            self.current_position = "center"
            self.rect.x = self.get_position_x() 
            self.hitbox.x = self.get_position_x()+15

    def move_right(self):
        if self.current_position == "center":
            self.current_position = "right"
            self.rect.x = self.get_position_x()
            self.hitbox.x = self.get_position_x() +15
        elif self.current_position == "left":
            self.current_position = "center"
            self.rect.x = self.get_position_x()
            self.hitbox.x = self.get_position_x() +15
            
    def move_up(self):
        # Update the rectangle
        self.rect.y -= 150
        self.hitbox.y -= 150
    
    def move_down(self):
        pass

    def update(self,movement,speed=0.5):
        # move the player left or right based on arrow key presses
        if movement == "left":
            self.move_left()
        elif movement == "right":
            self.move_right()
        elif movement == "up":
            self.move_up()
        elif movement == "down":
            self.move_down()
        if self.attack_animation == True:
            self.current_sprite += speed
            if int(self.current_sprite) >= len(self.sprites):
                self.current_sprite = 0
                self.attack_animation = False
        self.image = self.sprites[int(self.current_sprite)]
        if self.rect.y < 340:
            self.rect.y += 10
            self.hitbox.y += 10
    
    def attack(self):
         self.attack_animation = True

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
moving_sprites = pygame.sprite.Group()

# Creating the sprites and groups
moving_sprites.add(player)

# Set up the clock
clock = pygame.time.Clock()
spawn_time = 2000  # 2 seconds in milliseconds
last_spawn_time = pygame.time.get_ticks() - spawn_time

# set up the score and the username
username = None
score = 0
font = pygame.font.Font('Dream MMA.ttf',22)
font2 = pygame.font.Font('Dream MMA.ttf',32)

camera_video = cv2.VideoCapture(0)
camera_video.set(3,1280)
camera_video.set(4,960)


 
# Initialize a variable to store the state of the game (started or not).
game_started = False   
 
# Initialize a variable to store the index of the current horizontal position of the person.
# At Start the character is at center so the index is 1 and it can move left (value 0) and right (value 2).
x_pos_index = 1
 
# Initialize a variable to store the index of the current vertical posture of the person.
# At Start the person is standing so the index is 1 and he can crouch (value 0) and jump (value 2).
y_pos_index = 1
 
# Declate a variable to store the intial y-coordinate of the mid-point of both shoulders of the person.
MID_Y = None
 
# Initialize a counter to store count of the number of consecutive frames with person's hands joined.
counter = 0
 
# Initialize the number of consecutive frames on which we want to check if person hands joined before starting the game.
num_of_frames = 10


# Set up the game loop
clock = pygame.time.Clock()

    

# while player.lives > 0 and camera_video.isOpened():
while camera_video.isOpened():
    
    movement = None
    
    # Read a frame.
    ok, frame = camera_video.read()
    
    # Check if frame is not read properly then continue to the next iteration to read the next frame.
    if not ok:
        continue
    
    # Flip the frame horizontally for natural (selfie-view) visualization.
    frame = cv2.flip(frame, 1)
    
    # Get the height and width of the frame of the webcam video.
    frame_height, frame_width, _ = frame.shape
    
    # Perform the pose detection on the frame.
    results = detectPose(frame, pose_video)

    
    # Check if the pose landmarks in the frame are detected.
    if results.pose_landmarks:
        
        # Check if the game has started
        if game_started:    
            # Get horizontal position of the person in the frame.
            horizontal_position = checkLeftRight(frame, results)
            
            # Check if the person has moved to left from center or to center from right.
            if (horizontal_position=='Left' and x_pos_index!=0) or (horizontal_position=='Center' and x_pos_index==2):
                
                # Press the left arrow key.
                movement = "left"
                
                # Update the horizontal position index of the character.
                x_pos_index -= 1               
 
            # Check if the person has moved to Right from center or to center from left.
            elif (horizontal_position=='Right' and x_pos_index!=2) or (horizontal_position=='Center' and x_pos_index==0):
                
                # Press the right arrow key.
                movement = "right"
                
                # Update the horizontal position index of the character.
                x_pos_index += 1
            
            #--------------------------------------------------------------------------------------------------------------
        
        # Otherwise if the game has not started    
        else:
            
            # Write the text representing the way to start the game on the frame. 
            cv2.putText(frame, 'JOIN BOTH HANDS TO START THE GAME.', (5, frame_height - 10), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 255, 0), 3)
        
        # Command to Start or resume the game.
        #------------------------------------------------------------------------------------------------------------------
        
        # Check if the left and right hands are joined.
        if checkHandsJoined(frame, results) == 'Hands Joined':
 
            # Increment the count of consecutive frames with +ve condition.
            counter += 1
 
            # Check if the counter is equal to the required number of consecutive frames.  
            if counter == num_of_frames:
 
                # Command to Start the game first time.
                #----------------------------------------------------------------------------------------------------------
                                    
                #--------------------------------------------------------------------------------------------------------------
                # Check if the game has not started yet.
                if not(game_started):
 
                    # Update the value of the variable that stores the game state.
                    game_started = True
 
                    # Retreive the y-coordinate of the left shoulder landmark.
                    left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame_height)
 
                    # Retreive the y-coordinate of the right shoulder landmark.
                    right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame_height)
 
                    # Calculate the intial y-coordinate of the mid-point of both shoulders of the person.
                    MID_Y = abs(right_y + left_y) // 2
                
                #--------------------------------------------------------------
                
                # Update the counter value to zero.
                counter = 0
 
        # Otherwise if the left and right hands are not joined.        
        else:
 
            # Update the counter value to zero.
            counter = 0
            
        #------------------------------------------------------------------------------------------------------------------
 
        # Commands to control the vertical movements of the character.
        #------------------------------------------------------------------------------------------------------------------
        
        # Check if the intial y-coordinate of the mid-point of both shoulders of the person has a value.
        if MID_Y:
            
            # Get posture (jumping, crouching or standing) of the person in the frame. 
            posture = checkJumpCrouch(frame, results, MID_Y)
            
            # Check if the person has jumped.
            if posture == 'Jumping' and y_pos_index == 1:
 
                # Press the up arrow key
                movement = "up"
                
                # Update the veritcal position index of  the character.
                y_pos_index += 1 
 
            # Check if the person has crouched.
            elif posture == 'Crouching' and y_pos_index == 1:
 
                # Press the down arrow key
                movement = "down"
                
                # Update the veritcal position index of the character.
                y_pos_index -= 1
            
            # Check if the person has stood.
            elif posture == 'Standing' and y_pos_index   != 1:
                
                # Update the veritcal position index of the character.
                y_pos_index = 1
        
        #------------------------------------------------------------------------------------------------------------------
    
    
    # Otherwise if the pose landmarks in the frame are not detected.       
    else:
 
        # Update the counter value to zero.
        counter = 0
        
    
    # Display the frame.            
    cv2.imshow('Immersive Fitness Experience', frame)
    

    
    # # handle events
    for event in pygame.event.get():
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     # Get the mouse position
        #     mouse_x, mouse_y = pygame.mouse.get_pos()
        #     print("Clicked at ({}, {})".format(mouse_x, mouse_y))
        pass

    # update the sprites
    player.update(movement)
    obstacles.update()
    if game_started:
        
        for obstacle in obstacles:
            if player.hitbox.colliderect(obstacle.get_rect()):
                # the player has collided with an obstacle, so lose a life
                if player.lives !=0:
                    player.lives -= 1
                if player.lives == 0:
                    # player has no lives left
                    # Create randomly generated username for player

                    # generating random strings
                    if username ==None:
                        username = ''.join(random.choices(string.ascii_uppercase, k=5))
                        user_score = [username,int(score)]
                        #!! in the end, this needs to be modified for the leaderboard to store the top 10
                        with open('leaderboard.csv', 'a+', newline='\n') as write_obj:
                            # Create a writer object from csv module
                            csv_writer = writer(write_obj)
                            # Add contents of list as last row in the csv file
                            csv_writer.writerow(user_score)
                    #end the game
                    break
                obstacles.empty()
       
    
        # add obstacles
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time > spawn_time:
            last_spawn_time = current_time
            position = random.choice(["center","left","right"])
            # style = random.choice(["stand","jump","crouch"])
            style = "stand"
            obstacle = Obstacle(position,style)
            obstacles.add(obstacle)
        
        # remove obstacles that have gone off the bottom of the screen
        for obstacle in obstacles:
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
                score += 5
                
        score += 0.1
    #play video
    success, video_image = video.read()
    if success: 
            video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")

    window.blit(video_surf, (0, 0))
    # draw the sprites and score to the screen
    player.attack()
    for obstacle in obstacles:
        pygame.draw.rect(screen, obstacle.color, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
    screen.blit(font.render(f"score: {int(score)}", True, WHITE), (10, 10))
    screen.blit(font.render(f"lives: {player.lives}", True, WHITE), (WIDTH - 150, 10))
    moving_sprites.draw(screen)
    moving_sprites.update(1)

    if player.lives == 0:
         times = 1200
         while times >0:
            screen.blit(font2.render(f"game over.. restarting", True, GREEN), (WIDTH//4, HEIGHT//2))
            obstacles.empty()
            passed_time = clock.tick(120)
            times -= passed_time
            if times == 0:
                player.lives+=3
                score = 0
    pygame.display.update()
        
        # control the frame rate
    clock.tick(120)
