# Thinkers

# Motion-Detection Based Immserive Fitness Experience for CMU-Q IS Junior Consulting Project X STA 
The code's purpose and functionality is to launch an endless runner game, in which the user can manipulate the character's actions through physical gestures.

# Softwares
The code behind the experience (excluding the environment video background) is created solely on Python 3. It has been developed on multiple versions of Python 3 including 3.1, 3.7, 3.9, and are functional on all three versions. Visual Studio Code was used to develop the python files.

# Python Libraries Required
The following libraries (and sub-libraries) were utilized during the development of the final code: 
- Pygame - 2.1.3
    Pygame is the base of the code and is used for game mechanics, obstacle creation, collision detection, font presentation, and more.
- OpenCV - 4.7.0.68
    OpenCV is a computer vision library that specializes in real-time computer vision. It is used in combination with other libraries to capture the background video and connect with the camera.
- Numpy - 1.24.1
    Numpy is a mathematical-based library and is utilized in array usage and data transformation of the motion-detected landmarks to a format that is accepted by pygame.
- Mediapipe - 0.9.1.0
    
    Mediapipe is an open-source framework that uses machine learning to read data from a video or audio source and detect poses from it. It is utilized in detecting the user, their motion, creating the landmarks, the character, and more.
- Pandas - 1.5.3
    Pandas is a python library that is focused on data manipulation and analysis. It it utilized in updating the leaderboard file and identifying the top 10 scores.

# Instructions on how to install the required libraries.
To install the required packages, navigate to the directory containing the requirements.txt file in your terminal by using the "cd" command. Once you're in the directory, execute the following command: "pip install -r requirements.txt"
# For further Information, look to the Documentation folder.
