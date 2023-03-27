import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import math
import string
from csv import writer


# Initialize Pygame window
pygame.init()
video = cv2.VideoCapture("background2.mp4")
success, video_image = video.read()
fps = video.get(cv2.CAP_PROP_FPS)
screen = pygame.display.set_mode(video_image.shape[1::-1])
WIDTH = screen.get_width()
HEIGHT = screen.get_height()
pygame.display.set_caption("Endless Runner")

# set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

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
    if euclidean_distance < 130:  
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
    def update(self,landmarks):
        self.landmarks = Player.pygame_landmarks(landmarks)
    def pygame_landmarks(landmarks):
        # If landmarks are detected, draw them on frame
        if landmarks is not None:
            old = landmarks
            # Scale landmarks to make character smaller
            
            landmarks = np.array([(landmark.x, landmark.y, landmark.z) for landmark in landmarks.landmark])
            landmarks = landmarks[:, :2]
            
            factor = 0.4
            center_x = screen.get_width() / 2
            center_y = screen.get_height() * (1.2-factor)
    
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
# define the Obstacle class
class Obstacle(pygame.sprite.Sprite):
    s_line = 34 / 2
    b_line = 752 / 2
    distance = 370
    side = (distance) / (1-(s_line/b_line))
    speed = 5
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
            return BLACK
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
        self.y += Obstacle.speed + self.height / 10
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
font = pygame.font.Font('Dream MMA.ttf',22)
font2 = pygame.font.Font('Dream MMA.ttf',32)
obstacle_counter = 0

game_started = False
nose_y = 0
ankle_y = 0
# Main loop
while True:
    # Read frame from camera
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    
    # Convert frame to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    success, video_image = video.read()
    if success: 
        video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
    screen.blit(video_surf, (0, 0))
    # Detect pose landmarks
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(rgb)
        landmarks = results.pose_landmarks
        player.update(landmarks)
        obstacles.update()
            
        # Draw landmarks as circles on Pygame window
        if player.landmarks:
            for landmark in player.landmarks:
                pygame.draw.circle(screen, (255, 0, 0), landmark, 5)
                
    if game_started:
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
                                player.lives -= 1
                            elif player.lives == 0:
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
        
       # drawing the collision zone
        pygame.draw.polygon(screen, BLUE, vertices)
        
        # drawing the obstacles
        for obstacle in obstacles:
            pygame.draw.rect(screen, obstacle.color, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
            
    else:
        if landmarks:
            game_started = checkHandsJoined(landmarks)
            nose_y, ankle_y = player.landmarks[0][1], player.landmarks[28][1]
        text = font.render("join your hands to start", True, WHITE)
        screen.blit(text, (WIDTH / 2 - text.get_rect().width / 2, HEIGHT / 4))
     

    screen.blit(font.render(f"score: {int(score)}", True, WHITE), (10, 10))
    screen.blit(font.render(f"lives: {player.lives}", True, WHITE), (WIDTH - 150, 10))
    
    # Display frame in Pygame window
    pygame.display.update()
    clock.tick(160)
    
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            exit(0)
