import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import math
import string
from csv import writer
import pandas as pd
import ptext

#Initialize background music 
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag

pygame.mixer.init()

pygame.mixer.music.load('background.mp3')

pygame.mixer.music.play(-1)

# Initialize Pygame window
pygame.init()

#set up the video randomization
environments = ["oceanscape.mp4","desertscape.mp4"]
start_environment = random.choice(environments)
video = cv2.VideoCapture(start_environment)
success, video_image = video.read()
fps = video.get(cv2.CAP_PROP_FPS)
screen = pygame.display.set_mode(video_image.shape[1::-1])
WIDTH = screen.get_width()
HEIGHT = screen.get_height()
pygame.display.set_caption("Endless Runner")



print(130 / HEIGHT)

# set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (56, 239, 245)
GREEN = (0, 255, 0)
RED = (255,0,0)

#set up the fonts 
font = pygame.font.Font('Dream MMA.ttf',22)
font2 = pygame.font.Font('Dream MMA.ttf',32)
font_name = 'Dream MMA.ttf'

# setting up the leaderboard
# to put each row below the other
offset = 0 
data = pd.read_csv("leaderboard.csv")

fps = video.get(cv2.CAP_PROP_FPS)
# for video loop 
frame_counter = 0 

# setting up the restart countdown 
#countdown to restart
countdown, countdown_seconds = 15, '15'
pygame.time.set_timer(pygame.USEREVENT, 1500)
reset = False

#setting up the tutorial

# Initialize variables to store the state of the tutorial.
tutorial_completed = False 
tutorial_hands_joined = False
tutorial_point = "not started"

random_landmark = (0,0)

obstacles_avoided = 0


# Initialize Mediapipe Pose Detection
mp_pose = mp.solutions.pose

# Start video capture
cap = cv2.VideoCapture(0)

def checkHandsJoined(landmarks): 
    # Get the left wrist landmark x and y coordinates.
    left_wrist_landmark = (landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * WIDTH,
                          landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * HEIGHT)

    # Get the right wrist landmark x and y coordinates.
    right_wrist_landmark = (landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * WIDTH,
                           landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * HEIGHT)
    
    # Calculate the euclidean distance between the left and right wrist.
    euclidean_distance = int(math.hypot(left_wrist_landmark[0] - right_wrist_landmark[0],
                                   left_wrist_landmark[1] - right_wrist_landmark[1]))
    # Compare the distance between the wrists with a appropriate threshold to check if both hands are joined.
    if euclidean_distance < HEIGHT * 0.07:  
        return True
    return False

def interpolate_points(point1,point2, n):
    (x1,y1) = point1
    (x2,y2) = point2
    dx = (x2 - x1) / (n - 1)
    dy = (y2 - y1) / (n - 1)
    return list(zip([x1 + i*dx for i in range(1,n-1)], [y1 + i*dy for i in range(1,n-1)]))

 
def addObstacle():
    global obstacle_counter
    position = ["center","left","right"][obstacle_counter % 3]
    style = random.choice(["stand","jump","crouch"])
    new_obstacle = Obstacle(position,style)
    obstacles.add(new_obstacle)
    obstacle_counter += 1


class Player():
    def __init__(self):
        self.lives = 3
        self.landmarks = None
        self.username =  ''.join(random.choices(string.ascii_uppercase, k=5))
    def update(self,landmarks):
        self.landmarks = Player.pygame_landmarks(landmarks)
    def pygame_landmarks(landmarks):
        # If landmarks are detected, draw them on frame
        if landmarks is not None:
            old = landmarks
            # Scale landmarks to make character smaller
            
            landmarks = np.array([(landmark.x, landmark.y, landmark.z) for landmark in landmarks.landmark])
            landmarks = landmarks[:, :2]
            
            factor = 0.5
            center_x = screen.get_width() / 2
            center_y = screen.get_height() * (1.45-factor)
    
            # Map landmarks to Pygame coordinates
            x = landmarks[:, 0]
            y = landmarks[:, 1]
            x = np.interp(x, (0, 1), (0, screen.get_width()))
            y = np.interp(y, (0, 1), (0, screen.get_height()))
            dist_x = x - center_x
            dist_y = y - center_y
            # Apply the dilation factor to the distances
            dist_x *= factor
            dist_y *= factor
            # Add the dilated distances to the center of dilation coordinates
            x = dist_x + center_x
            y = dist_y + center_y
            x = [i for i in x]
            y = [i for i in y]
            landmarks_pygame = list(zip(x, y))
            
            # Add points to fill the character more
            left_shoulder = landmarks_pygame[12]
            left_elbow = landmarks_pygame[14]
            left_arm = interpolate_points(left_shoulder,left_elbow, int(10*factor))
            left_hip = landmarks_pygame[24]
            left_body = interpolate_points(left_shoulder,left_hip, int(10*factor))
            left_knee = landmarks_pygame[26]
            left_thigh = interpolate_points(left_knee,left_hip, int(10*factor))
            landmarks_pygame += left_arm + left_body + left_thigh
            right_shoulder = landmarks_pygame[11]
            right_elbow = landmarks_pygame[13]
            right_arm = interpolate_points(right_shoulder, right_elbow, int(10*factor))
            right_hip = landmarks_pygame[23]
            right_body = interpolate_points(right_shoulder, right_hip, int(10*factor))
            right_knee = landmarks_pygame[25]
            right_thigh = interpolate_points(right_knee, right_hip, int(10*factor))
            landmarks_pygame += right_arm + right_body + right_thigh
            return landmarks_pygame
        return None
    
    

def size(s,b,d):
    return (d*b) / s
class Obstacle(pygame.sprite.Sprite):
    s_line = 34 / 2
    b_line = 752 / 2
    distance = 370
    side = (distance) / (1-(s_line/b_line))
    speed = 8
    def __init__(self, position, style):
        super().__init__()
        self.style = style
        self.position = position
        self.color = self.get_color()
        self.height = self.get_height()
        self.width = self.get_width()
        self.y = self.get_position_y()
        self.x = self.get_position_x()
        
    def get_colision_line(self,nose_y,ankle_y):
        if self.style == "crouch":
            return ankle_y - 20
        elif self.style == "jump":
            return nose_y 
        else: 
            return (nose_y + ankle_y) / 2
    
    def get_color(self):
        if self.style == "stand":
            return BLUE
        elif self.style == "crouch":
            return WHITE
        else:
            return GREEN
    def get_height(self):
        initial_size = HEIGHT * 0.01
        if self.style == "stand":
            return initial_size
        else:  # Crouching or Jumping
            return initial_size / 4
        
    def get_width(self):
        if self.style == "stand":
            return self.height / 2
        else:  # Crouching or Jumping
            return self.height * 14
    
    def get_position_y(self):
        self.start_point = HEIGHT - Obstacle.distance
        if  self.style == "jump":
            self.start_point =  HEIGHT / 2 - 100
            return HEIGHT / 2 - 100
        return self.start_point
    
    def get_position_x(self):
        center_x = WIDTH / 2 - self.width / 2
        if self.style == "stand":
            if self.position == "left":
                return center_x - self.width * 3.5
            elif self.position == "right":
                return center_x + self.width * 3.5
            else:  # center
                return center_x
        else:
            return center_x

    def update(self):
        # start_point = HEIGHT - Obstacle.distance - self.height
        # move the obstacle down the screen
        self.y += Obstacle.speed + self.height 
        d = (self.y - self.start_point) + (Obstacle.side - Obstacle.distance)
        rate = (size(Obstacle.side,Obstacle.b_line,d)) / (Obstacle.s_line)
        self.height = self.get_height() * rate
        self.width = self.get_width()
        self.x = self.get_position_x()
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


player = Player()
obstacles = pygame.sprite.Group()

# Set up the clock
clock = pygame.time.Clock()

# set up the score and the username
username = None
score = 0
obstacle_counter = 0

game_started = False

# Initialize a variable to store the index of the current horizontal position of the person.
# At Start the character is at center so the index is 1 and it can move left (value 0) and right (value 2).
x_pos_index = 1

nose_y = 0
ankle_y = 0

# Main loop
while True:
    frame_counter+=1
    print(f"environment: {start_environment} \n tutorial_hands_joined: {tutorial_hands_joined} \n tutorial_point: {tutorial_point} \n tutorial_completed: {tutorial_completed} \n game started: {game_started} \n player lives: {player.lives} \n player username: {player.username}")
    # Read frame from camera
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    
    # Convert frame to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # start_environment = random.choice(environments)
    # video = cv2.VideoCapture(start_environment)
    success, video_image = video.read()
    if success: 
        video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
    screen.blit(video_surf, (0, 0))
    
    #video loop 
    if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
        start_environment = random.choice(environments)
        print("??????????????????",start_environment)
        frame_counter = 0
        video = cv2.VideoCapture(start_environment)

    # Detect pose landmarks
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(rgb)
        landmarks = results.pose_landmarks
        player.update(landmarks)
        obstacles.update()
            
    # Draw character
    if player.landmarks:
        x1, y1 = player.landmarks[0]
        x2, y2 = player.landmarks[8]
        r = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
        color = WHITE
        line_width = 15
        pygame.draw.polygon(screen, color, [player.landmarks[11],player.landmarks[12],player.landmarks[24],player.landmarks[23]])
        pygame.draw.circle(screen, color, player.landmarks[0], r * 1.3, width=0)
        pygame.draw.line(screen, color, player.landmarks[12], player.landmarks[14], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[14], player.landmarks[16], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[16], player.landmarks[22], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[16], player.landmarks[18], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[16], player.landmarks[20], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[18], player.landmarks[20], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[12], player.landmarks[24], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[24], player.landmarks[26], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[26], player.landmarks[28], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[28], player.landmarks[30], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[28], player.landmarks[32], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[30], player.landmarks[32], width=line_width)
        
        pygame.draw.line(screen, color, player.landmarks[11], player.landmarks[13], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[13], player.landmarks[15], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[15], player.landmarks[21], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[15], player.landmarks[17], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[15], player.landmarks[19], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[17], player.landmarks[19], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[11], player.landmarks[23], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[23], player.landmarks[25], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[25], player.landmarks[27], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[27], player.landmarks[29], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[27], player.landmarks[31], width=line_width)
        pygame.draw.line(screen, color, player.landmarks[29], player.landmarks[31], width=line_width)
    
    # Check if the left and right hands are joined & the tutorial is completed.
    if tutorial_hands_joined == False:
        if landmarks:
        
            if checkHandsJoined(landmarks):
            #if hands joined for the first time or after reset, set tutorial hands completed to actually start tutorial and move from welcome screen
                tutorial_hands_joined = True
                #store initial position of random landmark 
                random_landmark = player.landmarks[12]
                #change tutorial point to first point, the motion detection highlight
                tutorial_point = "motion detection highlight"

        welcome = "welcome..."
        welcome_rect = font2.render(f"{welcome}", True, WHITE)
        join = "join your hands to start"
        join_rect = font2.render(f"{join}", True, WHITE)
        ptext.draw(welcome, (WIDTH / 2 - welcome_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=32,shadow=(1.0,1.0))
        ptext.draw(join, (WIDTH / 2 - join_rect.get_rect().width / 2, HEIGHT / 2), color=WHITE, fontname=font_name, fontsize=32,shadow=(1.0,1.0))

        if landmarks:
            # game_started = checkHandsJoined(landmarks)
            nose_y, ankle_y = player.landmarks[0][1], player.landmarks[28][1]
    # All the different points and screens of the tutorial, past welcome screen
    if tutorial_completed == False:
            if tutorial_point=="motion detection highlight":
                #encourage user to move left and right and move arms around
                tutorial = "this experience is based on motion detection, try moving around!"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=22,shadow=(1.0,1.0))
                
                #check that they moved around
                if player.landmarks:
                    #store state of that random landmark
                    movement_check = player.landmarks[12]
                    #check that the landmark has moved around enough, hence player moved around
                    if abs(movement_check[0]-random_landmark[0]) >=HEIGHT * 0.1 :
                        #move to next point in tutorial
                        tutorial_point = "obstacles highlight"
                    # tutorial_completed = True
            if tutorial_point == "obstacles highlight":
                 #show users standing obstacles and concept of game
                tutorial = "you will have to avoid different incoming obstacles, get ready!"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=22,shadow=(1.0,1.0))

                if len(obstacles) == 0:
                    position = ["center","left","right"][obstacle_counter % 3]
                    style = "stand"
                    new_obstacle = Obstacle(position,style)
                    obstacles.add(new_obstacle)
                    obstacle_counter += 1
                for obstacle in obstacles: # this loop is used to store the obstacle in a variable
                    pass
                # seting up the colison zone
                y1 = y2 = obstacle.get_colision_line(nose_y,ankle_y)
                # y1 -= r*2
                # y2 -= r*2
                y3 = y4 = y1 + 10
                d1 = (y1 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
                d2 = (y3 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
                w1 = (d1 * Obstacle.b_line) / Obstacle.side
                w2 = (d2 * Obstacle.b_line) / Obstacle.side
                w1 *= 2
                w2 *= 2
                x1 = WIDTH / 2 - w1 / 2 
                x2 = WIDTH / 2 + w1 / 2 
                x3 = WIDTH / 2 - w2 / 2 
                x4 = WIDTH / 2 + w2 / 2 
                vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                hit_obstacle = False
                # colision handling
                if player.landmarks:
                    if obstacle.y > y1 and obstacle.y < y3:
                        for x, y in player.landmarks:
                            temp_rect = pygame.Rect(x, y, 1, 1)
                            if temp_rect.colliderect(obstacle.get_rect()):
                                    hit_obstacle = True
                                    # print("player hit obstacle, warn next time")
                                    obstacles.empty()
                                    break
                        if hit_obstacle == False:
                                obstacles_avoided+=1
                        else:
                            #reset variable for next obstacle
                            hit_obstacle = False  
                #TO DO:play around with number
                if obstacles_avoided == 1:
                    obstacles.empty()
                    tutorial_point = "crouch obstacle highlight" 
                    obstacles_avoided = 0  
                # remove obstacles that have gone off the bottom of the screen and add new obstacles
                for obstacle in obstacles:
                    if obstacle.y > HEIGHT:
                        obstacles.remove(obstacle)
                        position = ["center","left","right"][obstacle_counter % 3]
                        style = "stand"
                        new_obstacle = Obstacle(position,style)
                        obstacles.add(new_obstacle)
                        obstacle_counter += 1
                
            # drawing the collision zone
                pygame.draw.polygon(screen, BLUE, vertices)
                
                # drawing the obstacles
                for obstacle in obstacles:
                    pygame.draw.rect(screen, obstacle.color, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
            
            if tutorial_point == "crouch obstacle highlight": 
                tutorial = "to avoid this type of obstacle, squat below the line"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=22,shadow=(1.0,1.0))


                if len(obstacles) == 0:
                    position = ["center","left","right"][obstacle_counter % 3]
                    # TO DO: SWITCH JUMP AND CROUCH STYLE NAMES -> what is "jump" is actually the crouch one
                    style = "jump"
                    new_obstacle = Obstacle(position,style)
                    obstacles.add(new_obstacle)
                    obstacle_counter += 1
                for obstacle in obstacles: # this loop is used to store the obstacle in a variable
                    pass
                # seting up the colison zone
                y1 = y2 = obstacle.get_colision_line(nose_y,ankle_y)
                y3 = y4 = y1 + 30
                d1 = (y1 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
                d2 = (y3 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
                w1 = (d1 * Obstacle.b_line) / Obstacle.side
                w2 = (d2 * Obstacle.b_line) / Obstacle.side
                w1 *= 2
                w2 *= 2
                x1 = WIDTH / 2 - w1 / 2 
                x2 = WIDTH / 2 + w1 / 2 
                x3 = WIDTH / 2 - w2 / 2 
                x4 = WIDTH / 2 + w2 / 2 
                vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                hit_obstacle = False

                # notify player when to do exercise/when obstacle is coming up
                if (y1-obstacle.y)<=110 and obstacle.y <y3:
                        notif = "squat now!"
                        notif_rect = font.render(f"{notif}", True, RED)
                        ptext.draw(notif, (WIDTH / 2 - notif_rect.get_rect().width / 2, HEIGHT / 2), color=RED, fontname=font_name, fontsize=22,shadow=(1.0,1.0))

                # colision handling
                if player.landmarks:
                    if obstacle.y > y1 and obstacle.y < y3:  
                        for x, y in player.landmarks:
                            temp_rect = pygame.Rect(x, y, 1, 1)
                            if temp_rect.colliderect(obstacle.get_rect()):
                                    hit_obstacle = True
                                    # print("player hit obstacle, warn next time")
                                    # the player has collided with an obstacle, so lose a life
                                    obstacles.empty()
                                    break
                        if hit_obstacle == False:
                                obstacles_avoided+=1
                        else:
                            #reset variable for next obstacle
                            hit_obstacle = False  
                #TO DO:play around with number
                if obstacles_avoided == 3:
                    obstacles.empty()
                    tutorial_point = "jump obstacle highlight"  
                    obstacles_avoided = 0   
                # remove obstacles that have gone off the bottom of the screen and add new obstacles
                for obstacle in obstacles:
                    if obstacle.y > HEIGHT:
                        obstacles.remove(obstacle)
                        position = ["center","left","right"][obstacle_counter % 3]
                        style = "jump"
                        new_obstacle = Obstacle(position,style)
                        obstacles.add(new_obstacle)
                        obstacle_counter += 1
                
                # drawing the collision zone
                pygame.draw.polygon(screen, BLUE, vertices)
                
                # drawing the obstacles
                for obstacle in obstacles:
                    pygame.draw.rect(screen, obstacle.color, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

            if tutorial_point == "jump obstacle highlight": 
                tutorial = "to avoid this type of obstacle, do a jumping jack high above the line"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=22,shadow=(1.0,1.0))

                if len(obstacles) == 0:
                    position = ["center","left","right"][obstacle_counter % 3]
                    # TO DO: SWITCH JUMP AND CROUCH STYLE NAMES -> what is "jump" is actually the crouch one
                    style = "crouch"
                    new_obstacle = Obstacle(position,style)
                    obstacles.add(new_obstacle)
                    obstacle_counter += 1
                for obstacle in obstacles: # this loop is used to store the obstacle in a variable
                    pass
                # seting up the colison zone
                y1 = y2 = obstacle.get_colision_line(nose_y,ankle_y)
                y3 = y4 = y1 + 30
                d1 = (y1 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
                d2 = (y3 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
                w1 = (d1 * Obstacle.b_line) / Obstacle.side
                w2 = (d2 * Obstacle.b_line) / Obstacle.side
                w1 *= 2
                w2 *= 2
                x1 = WIDTH / 2 - w1 / 2 
                x2 = WIDTH / 2 + w1 / 2 
                x3 = WIDTH / 2 - w2 / 2 
                x4 = WIDTH / 2 + w2 / 2 
                vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                hit_obstacle = False

                # notify player when to do exercise/when obstacle is coming up
                if (y1-obstacle.y)<=110 and obstacle.y <y3:
                    notif = "jump now!"
                    notif_rect = font.render(f"{notif}", True, RED)
                    ptext.draw(notif, (WIDTH / 2 - notif_rect.get_rect().width / 2, HEIGHT / 2), color=RED, fontname=font_name, fontsize=22,shadow=(1.0,1.0))

                # colision handling
                if player.landmarks:
                    if obstacle.y > y1 and obstacle.y < y3:  
                        for x, y in player.landmarks:
                            temp_rect = pygame.Rect(x, y, 1, 1)
                            if temp_rect.colliderect(obstacle.get_rect()):
                                    hit_obstacle = True
                                    
                                    obstacles.empty()  
                                    #For testing purposes since jumping jacks were hard to complete
                                    # tutorial_completed = True            
                                    # tutorial_point = "done"
                                    break
                        if hit_obstacle == False:
                                obstacles_avoided+=1
                        else:
                            #reset variable for next obstacle
                            hit_obstacle = False  
                #TO DO:play around with number
                if obstacles_avoided == 1:
                    obstacles.empty()
                    tutorial_completed = True            
                    tutorial_point = "done"
                    obstacles_avoided = 0 
                      
                # remove obstacles that have gone off the bottom of the screen and add new obstacles
                for obstacle in obstacles:
                    if obstacle.y > HEIGHT:
                        obstacles.remove(obstacle)
                        position = ["center","left","right"][obstacle_counter % 3]
                        style = "crouch"
                        new_obstacle = Obstacle(position,style)
                        obstacles.add(new_obstacle)
                        obstacle_counter += 1
                
            # drawing the collision zone
                pygame.draw.polygon(screen, BLUE, vertices)
                
                # drawing the obstacles
                for obstacle in obstacles:
                    pygame.draw.rect(screen, obstacle.color, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

    
     #(game not started)join hands for the game to start after tutorial is completed
    if tutorial_completed == True:
        if game_started == False:
            game_join = "join your hands to start"
            game_rect = font.render(f"{game_join}", True, GREEN)
            ptext.draw(game_join, (WIDTH / 2 - game_rect.get_rect().width / 2, HEIGHT / 4), color=GREEN, fontname=font_name, fontsize=22,shadow=(1.0,1.0))


            if results.pose_landmarks:
                if checkHandsJoined(landmarks):
                    game_started = True
                    # if player.lives >0:
                    #     screen.blit(font.render(f"score: {int(score)}", True, WHITE), (10, 10))
                    #     screen.blit(font.render(f"lives: {player.lives}", True, WHITE), (WIDTH - 150, 10))
    
    
     #should be fine to keep just as game started bc & tutorial_completed is safety measure           
    if game_started:
        if player.lives !=0:
            screen.blit(font.render(f"score: {int(score)}", True, WHITE), (10, 10))
            screen.blit(font.render(f"lives: {player.lives}", True, WHITE), (WIDTH - 150, 10))
            if len(obstacles) == 0:
                addObstacle()
            for obstacle in obstacles: # this loop is used to store the obstacle in a variable
                pass
            # seting up the colison zone
            y1 = y2 = obstacle.get_colision_line(nose_y,ankle_y)
            y3 = y4 = y1 + 30
            d1 = (y1 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
            d2 = (y3 - HEIGHT + Obstacle.distance) + (Obstacle.side - Obstacle.distance)
            w1 = (d1 * Obstacle.b_line) / Obstacle.side
            w2 = (d2 * Obstacle.b_line) / Obstacle.side
            w1 *= 2
            w2 *= 2
            x1 = WIDTH / 2 - w1 / 2 
            x2 = WIDTH / 2 + w1 / 2 
            x3 = WIDTH / 2 - w2 / 2 
            x4 = WIDTH / 2 + w2 / 2 
            vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
            # colision handling
            if player.landmarks:
                if obstacle.y > y1 and obstacle.y < y3:
                    for x, y in player.landmarks:
                        temp_rect = pygame.Rect(x, y, 1, 1)
                        if temp_rect.colliderect(obstacle.get_rect()):
                                # the player has collided with an obstacle, so lose a life
                                if player.lives !=0:
                                    # print("hit player, warn next time")
                                    player.lives -= 1
                                elif player.lives == 0:
                                    # player has no lives left
                                    # Create randomly generated username for player
                                    # generating random strings
                                    if username ==None:
                                        username = player.username
                                        user_score = [username,int(score)]
                                        #!! in the end, this needs to be modified for the leaderboard to store the top 10
                                        with open('leaderboard.csv', 'a+', newline='\n') as write_obj:
                                            # Create a writer object from csv module
                                            csv_writer = writer(write_obj)
                                            # Add contents of list as last row in the csv file
                                            csv_writer.writerow(user_score)
                                    #end the game
                                    # to-do
                                obstacles.empty()
                                break
                                
            # remove obstacles that have gone off the bottom of the screen and add new obstacles
            for obstacle in obstacles:
                if obstacle.y > HEIGHT:
                    obstacles.remove(obstacle)
                    addObstacle()
                    score += 5
                    
            score += 0.1
            
            if score == 10:
                Obstacle.speed *= 1.5
            if score == 20:
                Obstacle.speed *= 1.5
            if score == 30:
                Obstacle.speed *= 1.5
                
        # drawing the collision zone
            pygame.draw.polygon(screen, BLUE, vertices)
            
            # drawing the obstacles
            for obstacle in obstacles:
                pygame.draw.rect(screen, obstacle.color, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
            
    if player.lives == 0: 
        #player lost, show leaderboard
        obstacles.empty()
        #restart option - 15 seconds 
        if countdown > 0:
            game_over = f"game over.. join hands in {countdown_seconds} seconds to restart"
            game_over_rect = font.render(f"{game_over}", True, GREEN)
            ptext.draw(game_over, (WIDTH / 2 - game_over_rect.get_rect().width / 2, HEIGHT / 4), color=GREEN, fontname=font_name, fontsize=22,shadow=(1.0,1.0))

            
            #order dataset based on highest scores
            data = data.sort_values(by=['Score'], ascending=False)
            # get the top 10 scores 
            data = data.head(10)
            usernames = data.loc[:,"Username"]
            #offset so the rows show one after the other
            offset=0
            for row in usernames:
                score = data.loc[data['Username'] == row]['Score'].values[0]
                #Highlight the users score if they make it on the leaderboard
                if row == username:
                    user_row = f"{row.lower()}.................{str(score)}"
                    user_row_rect = font.render(f"{user_row}", True, GREEN)
                    ptext.draw(user_row, (WIDTH / 2 - user_row_rect.get_rect().width / 2, (HEIGHT / 3)+offset), color=GREEN, fontname=font_name, fontsize=22,shadow=(1.0,1.0))


                else:
                    leader_row = f"{row.lower()}.................{str(score)}"
                    leader_row_rect = font.render(f"{leader_row}", True, WHITE)
                    ptext.draw(leader_row, (WIDTH / 2 - leader_row_rect.get_rect().width / 2, (HEIGHT / 3)+offset), color=WHITE, fontname=font_name, fontsize=22,shadow=(1.0,1.0))

                offset+=30
            #save the leaderboard to the updated csv so there will always be only 10 rows stored
            csv_save = data
            csv_save.to_csv("leaderboard.csv", index=False)       

            #Player chooses to restart experience
            if player.landmarks:
                if checkHandsJoined(landmarks):
                    start_environment = random.choice(environments)
                    print("!!!!!!!!!!!!!!!!!!!",start_environment)
                    player.lives+=3
                    score = 0
                    
                    #reset countdown - test later
                    #countdown, countdown_seconds = 15, '15'
                    #pygame.time.set_timer(pygame.USEREVENT, 1500)
        #Player has not restarted, reset experience
        if countdown == 0:
            start_environment = random.choice(environments)
            print("!!!!!!!!!!!!!!!!!!!",start_environment)
            #reset the players attributes
            player.username =  ''.join(random.choices(string.ascii_uppercase, k=5))
            player.lives +=3
            score = 0
            
            #reset the tutorial attributes
            tutorial_completed = False 
            tutorial_hands_joined = False
            tutorial_point = "not started"
            game_started = False
            reset = True
            obstacles_avoided = 0
            #reset countdown 
            countdown, countdown_seconds = 15, '15'
            pygame.time.set_timer(pygame.USEREVENT, 1500)
    
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            exit(0)
         # countdown for restarting
        if player.lives == 0:
            if event.type == pygame.USEREVENT: 
                countdown -= 1
                if countdown > 0:
                    countdown_seconds = str(countdown)
    
    
    # Display frame in Pygame window
    pygame.display.update()
    clock.tick(160)
