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
from PIL import Image

#Initialize background music 
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag

pygame.mixer.init()

pygame.mixer.music.load('background.mp3')

pygame.mixer.music.play(-1)

# Initialize Pygame window
pygame.init()

#set up the video randomization
environments = ["oceanscape.mp4","desertscape.mp4","mountainscape.mp4"]
start_environment = random.choice(environments)
video = cv2.VideoCapture(start_environment)
success, video_image = video.read()
fps = video.get(cv2.CAP_PROP_FPS)
screen = pygame.display.set_mode(video_image.shape[1::-1])
WIDTH = screen.get_width()
HEIGHT = screen.get_height()
pygame.display.set_caption("Immersive Fitness Experience")



# set up the colors
WHITE = (255, 255, 255)
BLACK = (20,20,20)
BLUE = (56, 239, 245)
GREEN = (0, 255, 0)
RED = (255,0,0)

#set up the fonts 
font = pygame.font.Font('blade.ttf',24)
font2 = pygame.font.Font('blade.ttf',32)
font_name = 'blade.ttf'

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

random_landmarks = [[0],[0]]
moved_check = False

skip_timer = 0
motion_timer = 0
collision_timer = 0

show_obstacle_point = False
obstacles_avoided = 0


# Initialize Mediapipe Pose Detection
mp_pose = mp.solutions.pose

# Start video capture
cap = cv2.VideoCapture(0)

def checkHandsJoined(landmarks): 
    if landmarks:
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

 
def addObstacle(style = None,position = None):
    global obstacle_counter
    global start_environment
    if style == None:
        position = ["center","left","right"][obstacle_counter % 3]
        style = random.choice(["stand","jump","crouch"])
    if start_environment == "oceanscape.mp4" and style == "jump":
        img_style = "crouch"
    else:
        img_style = style
    img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"

    img = Image.open(img_file)
    r = 15/img.size[1]
    initial_width = img.size[0] * r 
    initial_height = img.size[1] * r
    new_obstacle = Obstacle(position,style,initial_width,initial_height,img)
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
    speed = 7
    def __init__(self, position, style,initial_width,initial_height,img):
        super().__init__()
        self.img = img
        self.style = style
        self.position = position
        self.color = self.get_color()
        self.height = self.initial_height = initial_height
        self.width = self.initial_width = initial_width
        self.y = self.get_position_y()
        self.x = self.get_position_x()
        
    def get_colision_zone(self,nose_y,ankle_y):
        size = 30
        if self.style == "crouch":
            y1 = ankle_y + 5
            size = 40
        elif self.style == "jump":
            y1 = nose_y - 12
        else: 
            y1 = (nose_y + ankle_y) / 2
        y2 = y1
        y3 = y4 = (y1 + size)
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
        return x1,y1,x2,y2,x4,y4,x3,y3
        
    
    def get_color(self):
        if self.style == "stand":
            return BLUE
        elif self.style == "crouch":
            return WHITE
        else:
            return GREEN
    
    def get_position_y(self):
        self.start_point = HEIGHT - Obstacle.distance
        if  self.style == "jump":
            self.start_point =  HEIGHT / 2 - 100
            return HEIGHT / 2 - 100
        return self.start_point
    
    def get_position_x(self):
        global start_environment
        if start_environment == "oceanscape.mp4":
            l = 1.6
            r = 1.5
        elif start_environment == "desertscape.mp4":
            l = 1.05
            r = 1.05
        else:
            l = 1.3
            r = 1.3
        center_x = WIDTH / 2 - self.width / 2
        if self.style == "stand":
            if self.position == "left":
                return center_x - self.width * l
            elif self.position == "right":
                return center_x + self.width * r
            else:  # center
                return center_x
        else:
            return center_x

    def update(self):
        # start_point = HEIGHT - Obstacle.distance - self.height
        # move the obstacle down the screen
        self.y += Obstacle.speed
        d = (self.y - self.start_point) + (Obstacle.side - Obstacle.distance)
        rate = (size(Obstacle.side,Obstacle.b_line,d)) / (Obstacle.s_line)
        self.height = self.initial_height * rate
        self.width = self.initial_width * rate
        self.x = self.get_position_x()
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y+self.height*0.9, self.width, self.height*0.1)


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
lvl = 1
# Main loop
while True:
    frame_counter+=1
    # Read frame from camera
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    
    # Convert frame to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    success, video_image = video.read()
    if success: 
        video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
    screen.blit(video_surf, (0, 0))
    
    #video loop 
    if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
        video = cv2.VideoCapture(start_environment)
        frame_counter = 0

    # Detect pose landmarks
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(rgb)
        landmarks = results.pose_landmarks
        player.update(landmarks)
        obstacles.update()
    
    # Draw character
    if player.landmarks and show_obstacle_point == False:
        xa, ya = player.landmarks[0]
        xb, yb = player.landmarks[8]
        r = math.sqrt((xb - xa)**2 + (yb - ya)**2)  
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
    
    # Initial part of tutorial: hands are not joined and tutorial did not start
    if tutorial_hands_joined == False:
        ### TESTING 
        welcome = f"welcome.."
        if player.username != None:
            welcome = f"welcome.. {player.username.lower()}"
        welcome_rect = font2.render(f"{welcome}", True, WHITE)
        join = "join your hands to start"
        join_rect = font2.render(f"{join}", True, WHITE)
        ptext.draw(welcome, (WIDTH / 2 - welcome_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE,fontname=font_name, fontsize=32,shadow=(1.0,1.0))
        ptext.draw(join, (WIDTH / 2 - join_rect.get_rect().width / 2, HEIGHT / 2), color=WHITE, fontname=font_name, fontsize=32,shadow=(1.0,1.0))

        #accordance to data and privacy laws notice 
        law = "this experience acts in accordance with \n qatar's data protection and privacy laws"
        law_rect = font.render(f"{law}", True, WHITE)
        ptext.draw(law, (10, HEIGHT - 40), color=WHITE, fontname=font_name, fontsize=8,shadow=(1.0,1.0))
        #if hands joined for the first time or after reset, set tutorial hands completed to actually start tutorial and move from welcome screen
        if landmarks:
            if checkHandsJoined(landmarks):
                tutorial_hands_joined = True
                #store initial position of random landmarks 
                random_landmarks[0] = player.landmarks[12]
                random_landmarks[1] = player.landmarks[2]
                #change tutorial point to first point, the motion detection highlight
                tutorial_point = "skip tutorial"
                # set-up the collision zone
                nose_y, ankle_y = player.landmarks[0][1], player.landmarks[28][1]

                #store the skip timer for the tutorial 
                skip_timer = pygame.time.get_ticks()

    # All the different points and screens of the tutorial, past welcome screen
    elif tutorial_completed == False:
            if tutorial_point == "skip tutorial":
                now = pygame.time.get_ticks()
                delay = 5000 #5 seconds
                tutorial = "if you would like to skip the tutorial, join your hands again."
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                
                if ( now < skip_timer + delay ) and ( now > skip_timer + delay/2 ):
                    if checkHandsJoined(landmarks):
                        tutorial_completed = True            
                        tutorial_point = "done"
                elif ( now > skip_timer + delay ):
                    tutorial_point = "motion detection highlight"

                    #store the motion timer for the tutorial 
                    motion_timer = pygame.time.get_ticks()
                

            if tutorial_point=="motion detection highlight":
                now = pygame.time.get_ticks()
                delay = 5000 #5 seconds
                #encourage user to move left and right and move arms around
                tutorial = "this experience is based on motion detection, try moving around!"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                
                
                #check that they moved around
                if player.landmarks:
                    #store state of the random landmarks
                    movement_check= [player.landmarks[12], player.landmarks[2]]
                    #check that the first stored landmark has moved around enough, hence player moved around
                    if abs(movement_check[0][0]-random_landmarks[0][0]) >=HEIGHT * 0.08 :
                        moved_check = True
                    
                    # a second check of another landmark to lengthen tutorial !keep adding checks to lengthen even more
                    if moved_check:
                        if abs(movement_check[1][0]-random_landmarks[1][0]) >=HEIGHT * 0.08 and ( now > motion_timer + delay ) :
                            #move to next point in tutorial
                            tutorial_point = "collision line highlight"
                            collision_timer = pygame.time.get_ticks() 
                    
            if tutorial_point == "collision line highlight":
                    style = "stand"
                    position = "center"
                    if style == "jump": #don't need to change since obstacle image wont actually show
                        img_style = "crouch"
                    else:
                        img_style = style
                    img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                    img = Image.open(img_file)
                    r = 15/img.size[1]
                    initial_width = img.size[0] * r 
                    initial_height = img.size[1] * r
                    dummy_obstacle = Obstacle(position,style,initial_width,initial_height,img)
                    now = pygame.time.get_ticks()           
                    #timer variables so the text shows for x seconds
                    now = pygame.time.get_ticks()
                    delay = 3000 #3 seconds

                    #parts are sequential - follow one another based on multiplaction of delay
                    if ( now < collision_timer + delay ):
                        tutorial = "in this experience, different obstacles will come towards you"
                        tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                        ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 4), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                        
                    if (now > collision_timer + (delay)) & (now < collision_timer + (delay*4)):
                        tutorial = "if your character touches the obstacle \n while in the colored line, you get hit!"
                        tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                        ptext.draw(tutorial, (WIDTH / 4, HEIGHT / 6), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))

                        x1,y1,x2,y2,x4,y4,x3,y3 = dummy_obstacle.get_colision_zone(nose_y,ankle_y)
                        vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                        # drawing the collision zone
                        pygame.draw.polygon(screen, BLUE, vertices)
                    
                    if (now > collision_timer + (delay*4)) & (now < collision_timer + (delay*8)):
                        tutorial = "the position of the line changes based on the obstacle coming \n towards you, you'll have to do different exercises to avoid them!"
                        tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                        ptext.draw(tutorial, (WIDTH/10, HEIGHT / 6), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                        
                        x1,y1,x2,y2,x4,y4,x3,y3 = dummy_obstacle.get_colision_zone(nose_y,ankle_y)
                        vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                        # drawing the collision zone - no need for this point?
                        # pygame.draw.polygon(screen, BLUE, vertices)
                    if (now > collision_timer + (delay*8)) & (now < collision_timer + (delay*9)):
                        position = "this line is created based on your mid range"
                        position_rect = font.render(f"{position}", True, WHITE)
                        ptext.draw(position, (WIDTH / 2 - position_rect.get_rect().width / 2,HEIGHT / 6), color=GREEN, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                        
                        x1,y1,x2,y2,x4,y4,x3,y3 = dummy_obstacle.get_colision_zone(nose_y,ankle_y)
                        vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                        # drawing the collision zone
                        pygame.draw.polygon(screen, BLUE, vertices)
                    
                    
                    if now > (collision_timer + (delay*9)):
                        if dummy_obstacle.style == "stand":
                            obstacles.empty()
                            #update dummy obstacle to show collision zone of different locations e.g. head, mid, ankles
                            style = "jump"
                            position = "center"
                            if start_environment == "oceanscape.mp4" and style == "jump":
                                img_style = "crouch"
                            else:
                                img_style = style
                            img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                            img = Image.open(img_file)
                            r = 15/img.size[1]
                            initial_width = img.size[0] * r 
                            initial_height = img.size[1] * r
                            dummy_obstacle = Obstacle(position,style,initial_width,initial_height,img)    
                    if (now > collision_timer + (delay*9)) & (now < collision_timer + (delay*10)):
                        tutorial = "this line is created based on your head range"
                        tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                        ptext.draw(tutorial, (WIDTH/6, HEIGHT / 6), color=GREEN, fontname=font_name, fontsize=24,shadow=(1.0,1.0))

                        x1,y1,x2,y2,x4,y4,x3,y3 = dummy_obstacle.get_colision_zone(nose_y,ankle_y)
                        vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                        # drawing the collision zone
                        pygame.draw.polygon(screen, BLUE, vertices)
                    
                    if now > (collision_timer + (delay*10)):
                        if dummy_obstacle.style == "jump":
                            obstacles.empty()
                            #update dummy obstacle to show collision zone of different locations e.g. head, mid, ankles
                            style = "crouch"
                            position = "center"
                            if start_environment == "oceanscape.mp4" and style == "jump":
                                img_style = "crouch"
                            else:
                                img_style = style
                            img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                            img = Image.open(img_file)
                            r = 15/img.size[1]
                            initial_width = img.size[0] * r 
                            initial_height = img.size[1] * r
                            dummy_obstacle = Obstacle(position,style,initial_width,initial_height,img)   
                    if (now > collision_timer + (delay*10)) & (now < collision_timer + (delay*11)):
                        tutorial = "and this line is created based on your ankle range"
                        tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                        ptext.draw(tutorial, (WIDTH/6.5, HEIGHT / 6), color=GREEN, fontname=font_name, fontsize=24,shadow=(1.0,1.0))

                        x1,y1,x2,y2,x4,y4,x3,y3 = dummy_obstacle.get_colision_zone(nose_y,ankle_y)
                        vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                        # drawing the collision zone
                        pygame.draw.polygon(screen, BLUE, vertices)
                    if (now > collision_timer + (delay*11)) & (now < collision_timer + (delay*15)):
                        tutorial = "so, you don't have to move backwards or forwards just:"
                        tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                        ptext.draw(tutorial, (WIDTH/8.5, HEIGHT / 6), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))

                        if (now > collision_timer + (delay*12)) & (now < collision_timer + (delay*15)):
                             stand = "do a jump to the left, center, or right"
                             stand_rect = font.render(f"{stand}", True, WHITE)
                             col = GREEN 
                             drop = (1.0,1.0)
                             if start_environment == "mountainscape.mp4":
                                 col = BLACK
                                 drop = (0,0)
                             ptext.draw(stand, (WIDTH/6, (HEIGHT / 6)+100), color=col, fontname=font_name, fontsize=24,shadow=drop)
                        
                        if (now > collision_timer + (delay*13)) & (now < collision_timer + (delay*15)):
                             crouch = "do a squat"
                             crouch_rect = font.render(f"{crouch}", True, WHITE)
                             ptext.draw(crouch, (WIDTH/6, (HEIGHT / 6)+200), color=col, fontname=font_name, fontsize=24,shadow=drop)
                        
                        if (now > collision_timer + (delay*14)) & (now < collision_timer + (delay*14.9)):
                             jump = "do a jumping jack"
                             jump_rect = font.render(f"{jump}", True, WHITE)
                             ptext.draw(jump, (WIDTH/6, (HEIGHT / 6)+300), color=col, fontname=font_name, fontsize=24,shadow=drop)

                    if (now > collision_timer + (delay*14.9)):
                        show_obstacle_point = True
                    if (now > collision_timer + (delay*15)) & (now < collision_timer + (delay*19)):
                        explain = "these are the different obstacles you will see \nand what action they mean"
                        explain_rect = font.render(f"{explain}", True,WHITE)
                        ptext.draw(explain, (WIDTH /2 - explain_rect.get_rect().width / 2.5, HEIGHT / 10), color=WHITE, fontname=font_name, fontsize=30,shadow=(1.5,2.0))
                            
                        style = ["stand","jump","crouch"]
                        position = "center"
                        
                        if (now > collision_timer + (delay*15.5)) & (now < collision_timer + (delay*19)):
                            
                            img_style = style[0]
                            img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                            img = Image.open(img_file)
                            r = 15/img.size[1]
                            initial_width = img.size[0] * r 
                            initial_height = img.size[1] * r

                            # resize image
                            pos = 50
                            pic_width = 200
                            pic_height = 175

                            img_resized = img.resize((pic_width, pic_height))
                            # Convert the resized image to a Pygame surface and blit it
                            cube = pygame.image.frombuffer(img_resized.tobytes(), img_resized.size, "RGBA")
                            screen.blit(cube, (pos, HEIGHT /2.5 ))
                            
                            #print the corresponding text below it
                            obs_type = ["move"]
                            text = f"{obs_type[0]}"
                            text_rect = font.render(f"{obs_type[0]}", True,WHITE)
                            ptext.draw(text, (pos+(pic_width/4), HEIGHT / 1.5), color=WHITE, fontname=font_name, fontsize=30,shadow=(1.5,2.0))
                                            
                        if (now > collision_timer + (delay*16)) & (now < collision_timer + (delay*19)):
                            if start_environment == "oceanscape.mp4":
                                img_style = "crouch"
                            else:
                                img_style = style[1]
                            
                            img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                            img = Image.open(img_file)
                            r = 15/img.size[1]
                            initial_width = img.size[0] * r 
                            initial_height = img.size[1] * r

                            # resize image
                            pic_width = 300
                            pic_height = 150
                            pos = (WIDTH / 2) - (pic_width/2)

                            img_resized = img.resize((pic_width, pic_height))
                            # Convert the resized image to a Pygame surface and blit it
                            cube = pygame.image.frombuffer(img_resized.tobytes(), img_resized.size, "RGBA")
                            screen.blit(cube, (pos, HEIGHT /2.5 ))
                            
                            #print the corresponding text below it
                            obs_type = ["squat"]
                            text = f"{obs_type[0]}"
                            text_rect = font.render(f"{obs_type[0]}", True,WHITE)
                            ptext.draw(text, (pos+(pic_width/4), HEIGHT / 1.5), color=WHITE, fontname=font_name, fontsize=30,shadow=(1.5,2.0))
                                            
                        
                        if (now > collision_timer + (delay*17)) & (now < collision_timer + (delay*19)):
                            img_style = style[2]
                            img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                            img = Image.open(img_file)
                            r = 15/img.size[1]
                            initial_width = img.size[0] * r 
                            initial_height = img.size[1] * r

                            # resize image
                            pic_width = 300
                            pic_height = 150
                            pos = WIDTH - 350

                            img_resized = img.resize((pic_width, pic_height))
                            # Convert the resized image to a Pygame surface and blit it
                            cube = pygame.image.frombuffer(img_resized.tobytes(), img_resized.size, "RGBA")
                            screen.blit(cube, (pos, HEIGHT /2.5 ))
                            
                            #print the corresponding text below it
                            obs_type = ["jump"]
                            text = f"{obs_type[0]}"
                            text_rect = font.render(f"{obs_type[0]}", True,WHITE)
                            ptext.draw(text, (pos+(pic_width/4), HEIGHT / 1.5), color=WHITE, fontname=font_name, fontsize=30,shadow=(1.5,2.0))

                    
                    if (now > collision_timer + (delay*19)):
                        show_obstacle_point = False
                        obstacles.empty()
                        tutorial_point = "obstacles highlight"
                        
            if tutorial_point == "obstacles highlight":
                 #show users standing obstacles and concept of game
                tutorial = "now, try to avoid the different incoming obstacles.. get ready!"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 6), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                style = "stand"
                
            if tutorial_point == "crouch obstacle highlight": 
                #PRESENTATION DEMO ONLY 
                tutorial_completed = True 
                tutorial_point = "done"  
                tutorial = "to avoid this type of obstacle, squat below the line"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 6), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                style = "jump"
                
            if tutorial_point == "jump obstacle highlight": 
                tutorial = "to avoid this type of obstacle, do a jumping jack high above the line"
                tutorial_rect = font.render(f"{tutorial}", True, WHITE)
                ptext.draw(tutorial, (WIDTH / 2 - tutorial_rect.get_rect().width / 2, HEIGHT / 6), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                style = "crouch"
                
            if tutorial_point != "skip tutorial" and tutorial_point!="done":
                if tutorial_point!= "motion detection highlight" and tutorial_point != "collision line highlight":
                    if len(obstacles) == 0:
                        position = ["center","left","right"][obstacle_counter % 3]
                        if start_environment == "oceanscape.mp4" and style == "jump":
                            img_style = "crouch"
                        else:
                            img_style = style
                        img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                        img = Image.open(img_file)
                        r = 15/img.size[1]
                        initial_width = img.size[0] * r 
                        initial_height = img.size[1] * r
                        new_obstacle = Obstacle(position,style,initial_width,initial_height,img)
                        obstacles.add(new_obstacle)
                        obstacle_counter += 1
                        for obstacle in obstacles:
                            pass
                        x1,y1,x2,y2,x4,y4,x3,y3 = obstacle.get_colision_zone(nose_y,ankle_y)
                        vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                    # drawing the collision zone
                    pygame.draw.polygon(screen, BLUE, vertices)
                    # notify player when to do exercise/when obstacle is coming up
                    if (y1-(obstacle.y + obstacle.height))<=20 and obstacle.y <y3:
                        text_col = RED
                        if start_environment == "mountainscape.mp4":
                                #Maroon color, for improved contrast
                                text_col = (80,0,0)
                        elif start_environment == "oceanscape.mp4":
                                text_col = (204, 255, 0)
                        if style == "crouch":
                            notif = "jump now!"
                        elif style == "jump":
                            notif = "squat now!"
                        else:
                            notif = "move now!"
                        notif_rect = font.render(f"{notif}", True, text_col)
                        ptext.draw(notif, (WIDTH / 2 - notif_rect.get_rect().width / 2, HEIGHT / 4), color=text_col, fontname=font_name, fontsize=24,shadow=(1.0,1.0))
                            
                    # colision handling
                    hit_obstacle = False
                    if player.landmarks:
                        for obstacle in obstacles:
                            pass
                        if obstacle.get_rect().y > y1 and obstacle.get_rect().y < y3:
                            for x, y in player.landmarks:
                                temp_rect = pygame.Rect(x, y, 10, 10)
                                # pygame.draw.rect(screen,GREEN,temp_rect)
                                if temp_rect.colliderect(obstacle.get_rect()):
                                        hit_obstacle = True
                                        obstacles.empty()
                                        break
                            if hit_obstacle == False:
                                    obstacles_avoided+=1
                            else:
                                #reset variable for next obstacle
                                hit_obstacle = False  
                if obstacles_avoided == 2:
                    obstacles_avoided = 0 
                    obstacles.empty()
                    if style == "stand":
                        tutorial_point = "crouch obstacle highlight" 
                    elif style == "jump":
                        tutorial_point = "jump obstacle highlight"
                    else:
                        tutorial_completed = True            
                        tutorial_point = "done" 
                    
                # remove obstacles that have gone off the bottom of the screen and add new obstacles
                for obstacle in obstacles:
                    if obstacle.y > HEIGHT:
                        obstacles.remove(obstacle)
                        position = ["center","left","right"][obstacle_counter % 3]
                        if start_environment == "oceanscape.mp4" and style == "jump":
                            img_style = "crouch"
                        else:
                            img_style = style
                        img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
                        img = Image.open(img_file)
                        r = 15/img.size[1]
                        initial_width = img.size[0] * r 
                        initial_height = img.size[1] * r
                        new_obstacle = Obstacle(position,style,initial_width,initial_height,img)
                        obstacles.add(new_obstacle)
                        obstacle_counter += 1
            
            # drawing the obstacles
            for obstacle in obstacles:
                # resize image
                img_resized = obstacle.img.resize((int(obstacle.width), int(obstacle.height)))
                # Convert the resized image to a Pygame surface and blit it
                cube = pygame.image.frombuffer(img_resized.tobytes(), img_resized.size, "RGBA")
                screen.blit(cube, (obstacle.x, obstacle.y ))
                pygame.draw.rect(screen,RED,obstacle.get_rect())

            
    
     #(game not started)join hands for the game to start after tutorial is completed
    if tutorial_completed == True:
        if game_started == False:
            now = pygame.time.get_ticks()
            delay = 5000 #5 seconds
            if ( now > skip_timer + delay ):
            
                game_join = "join your hands to start"
                game_rect = font.render(f"{game_join}", True, GREEN)
                ptext.draw(game_join, (WIDTH / 2 - game_rect.get_rect().width / 2, HEIGHT / 4), color=GREEN, fontname=font_name, fontsize=24,shadow=(1.0,1.0))


                if results.pose_landmarks:
                    if checkHandsJoined(landmarks):
                        game_started = True
                
    if game_started:
        if player.lives !=0:
            screen.blit(font.render(f"score: {int(score)}", True, WHITE), (10, 10))
            screen.blit(font.render(f"lives: {player.lives}", True, WHITE), (WIDTH - 150, 10))
            if len(obstacles) == 0:
                addObstacle()
                for obstacle in obstacles:
                    pass
                x1,y1,x2,y2,x4,y4,x3,y3 = obstacle.get_colision_zone(nose_y,ankle_y)
                vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
            # colision handling
            if player.landmarks:
                # notify player when to do exercise/when obstacle is coming up
                if (y1-(obstacle.y + obstacle.height))<=20 and obstacle.y <y3:
                    text_col = RED
                    if start_environment == "mountainscape.mp4":
                        text_col = (80,0,0)
                    elif start_environment == "oceanscape.mp4":
                            text_col = (204, 255, 0)
                    if obstacle.style == "jump":
                        notif = "squat now"
                    elif obstacle.style == "crouch":
                        notif = "jump now!"
                    else:
                        notif = "move now!"
                    notif_rect = font.render(f"{notif}", True, text_col)
                    ptext.draw(notif, (WIDTH / 2 - notif_rect.get_rect().width / 2, HEIGHT / 4), color=text_col, fontname=font_name, fontsize=24,shadow=(1.0,1.0))

                if obstacle.get_rect().y > y1 and obstacle.get_rect().y < y3:
                    for x, y in player.landmarks:
                        temp_rect = pygame.Rect(x, y, 10, 10)
                        if temp_rect.colliderect(obstacle.get_rect()):
                                # the player has collided with an obstacle, so lose a life
                                if player.lives !=0:
                                    player.lives -= 1
                                if player.lives == 0:
                                    # player has no lives left
                                    # Create randomly generated username for player
                                    # generating random strings
                                        username = player.username
                                        user_score = [username,int(score)]
                                        #!! in the end, this needs to be modified for the leaderboard to store the top 10
                                        with open('leaderboard.csv', 'a+', newline='\n') as write_obj:
                                            # Create a writer object from csv module
                                            csv_writer = writer(write_obj)
                                            # Add contents of list as last row in the csv file
                                            csv_writer.writerow(user_score)
                                        data.loc[len(data)] = user_score
                                    #end the game
                                    # to-do
                                obstacles.empty()
                                break
                                
            # remove obstacles that have gone off the bottom of the screen and add new obstacles
            for obstacle in obstacles:
                if obstacle.y > HEIGHT:
                    obstacles.remove(obstacle)
                    addObstacle()
                    for obstacle in obstacles:
                        pass
                    x1,y1,x2,y2,x4,y4,x3,y3 = obstacle.get_colision_zone(nose_y,ankle_y)
                    vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
                    score += 5
                    
            score += 0.1
            
      
            if score > 20 and lvl == 1:
                Obstacle.speed *= 1.5
                lvl = 2
            if score > 40 and lvl ==2:
                Obstacle.speed *= 1.5
                lvl = 3
                
        # drawing the collision zone
            pygame.draw.polygon(screen, BLUE, vertices)
            
            # drawing the obstacles
            for obstacle in obstacles:
                # resize image
                img_resized = obstacle.img.resize((int(obstacle.width), int(obstacle.height)))
                # Convert the resized image to a Pygame surface and blit it
                cube = pygame.image.frombuffer(img_resized.tobytes(), img_resized.size, "RGBA")
                screen.blit(cube, (obstacle.x, obstacle.y ))
            
    if player.lives == 0: 
        #player lost, show leaderboard
        obstacles.empty()
        #restart option - 15 seconds 
        if countdown > 0:
            game_over = f"game over.. join hands in {countdown_seconds} seconds to restart"
            game_over_rect = font.render(f"{game_over}", True, GREEN)
            ptext.draw(game_over, (WIDTH / 2 - game_over_rect.get_rect().width / 2, HEIGHT / 4), color=GREEN, fontname=font_name, fontsize=24,shadow=(1.0,1.0))

            
            #order dataset based on highest scores
            data = data.sort_values(by=['Score'], ascending=False)
            # get the top 10 scores 
            data = data.head(10)
            #save the leaderboard to the updated csv so there will always be only 10 rows stored
            csv_save = data
            csv_save.to_csv("leaderboard.csv", index=False) 
            usernames = data.loc[:,"Username"]
            #offset so the rows show one after the other
            offset=0
            for row in usernames:
                score = data.loc[data['Username'] == row]['Score'].values[0]
                #Highlight the users score if they make it on the leaderboard
                if row == username:
                    user_row = f"{row.lower()}.................{str(score)}"
                    user_row_rect = font.render(f"{user_row}", True, GREEN)
                    ptext.draw(user_row, (WIDTH / 2 - user_row_rect.get_rect().width / 2, (HEIGHT / 3)+offset), color=GREEN, fontname=font_name, fontsize=24,shadow=(1.0,1.0))


                else:
                    leader_row = f"{row.lower()}.................{str(score)}"
                    leader_row_rect = font.render(f"{leader_row}", True, WHITE)
                    ptext.draw(leader_row, (WIDTH / 2 - leader_row_rect.get_rect().width / 2, (HEIGHT / 3)+offset), color=WHITE, fontname=font_name, fontsize=24,shadow=(1.0,1.0))

                offset+=30       

            #Player chooses to restart experience
            if player.landmarks:
                if checkHandsJoined(landmarks):
                    start_environment = random.choice(environments)
                    
                    #re-capture video and reset frame counter
                    video = cv2.VideoCapture(start_environment)                    
                    success, video_image = video.read()
                    if success: 
                        video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
                    screen.blit(video_surf, (0, 0))
                    frame_counter = 0
                    player.lives+=3
                    score = 0
                    
                    #reset countdown - test later
                    #countdown, countdown_seconds = 15, '15'
                    #pygame.time.set_timer(pygame.USEREVENT, 1500)
        #Player has not restarted, reset experience
        if countdown == 0:
            start_environment = random.choice(environments)
            #re-capture video and reset frame counter
            video = cv2.VideoCapture(start_environment)                    
            success, video_image = video.read()
            if success: 
                video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
            screen.blit(video_surf, (0, 0))
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
        if tutorial_point == "skip tutorial":
            if event.type == pygame.USEREVENT:
                skip_timer-=1
        if tutorial_point == "motion detection highlight":
            if event.type == pygame.USEREVENT:
                motion_timer-=1
        if tutorial_point == "collision line highlight":
            if event.type == pygame.USEREVENT:
                collision_timer-=1
         # countdown for restarting
        if player.lives == 0:
            if event.type == pygame.USEREVENT: 
                countdown -= 1
                if countdown > 0:
                    countdown_seconds = str(countdown)
    
    
    # Display frame in Pygame window
    pygame.display.update()
    clock.tick(360)