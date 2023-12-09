
#Importing libraries
import cv2
import numpy as np

#Capturing the video from video path
video_path = "video\AI Assignment video.mp4"
cap = cv2.VideoCapture(video_path)

# Defining color ranges
color_ranges = {
    'yellow': ((16,131,47), (77,255,255)),
    'Green' : ((28, 64, 35),(95, 186, 255)),
    'orange' : ((1,122,192), (95,174,255))
    #'white' : ((11,29,70), (66,39,255))
    
}

#Extrating frame per second  and frame count from the video
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Defining output path
output_video_path = "video\output_video.avi"
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (1632,918))

# Defining function to calculate timestamp
def calculate_timestamp(frame_number, fps):
    return round(frame_number / fps,2)

#Defining a function to check whether the ball inside the quadrants
def is_inside_quadrant(point, quadrant):
    x, y = point
    x_min, y_min, x_max, y_max = quadrant
    return x_min <= x <= x_max and y_min <= y <= y_max

# Defining a function to rescale each frame in the video
def rescaleFrame(frame, scale=0.85):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width,height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

#Defining coordinate for each quadrants
quadrants = {
        1: (110, 35, 505, 410),
        2: (510, 20, 850, 410),
        3: (510, 420, 850, 800),
        4: (110, 420, 505, 800)
    }

# Initializing ball position as empty
ball_positions = {quadrant: [] for quadrant in quadrants}

color_dic = {1:[],2:[],3:[],4:[]}
events=[]
dic = {1:[],2:[],3:[],4:[]}
dic2 = {1:[],2:[],3:[],4:[]}
empty=[]



for frame_number in range(frame_count):
    ret, frame = cap.read()
    if not ret:
        break

    #Fliping the each frames of video
    flip = cv2.flip(frame, -1)
    
    # Resizing the each frames of video
    frameResized = rescaleFrame(flip)

    blank = np.zeros(frameResized.shape[:2],dtype = 'uint8')
    gray = cv2.cvtColor(frameResized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)


    circles = cv2.HoughCircles(
    blurred, 
    cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=100, param2=30, minRadius=10, maxRadius=50
    )   
    
    # Converting bgr image to hsv for detecting the color
    hsv_frame = cv2.cvtColor(frameResized, cv2.COLOR_BGR2HSV)

    for color, (lower, upper) in color_ranges.items():
        if circles is not None: 
            mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            result = cv2.bitwise_and(frameResized, frameResized, mask=mask)
            for contour in contours:
                        
                        # Finding the coordinates using cv2.moments
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])

                            for quadrant_number, quadrant_coords in quadrants.items():

                                # Checking whether the ball is inside the coordinate
                                if is_inside_quadrant((cX, cY), quadrant_coords):
                                        if (cX, cY) not in ball_positions[quadrant_number]:
                                              num1 = quadrant_number
                                              if dic2[num1] == empty:
                                                    events.append((calculate_timestamp(frame_number, fps), quadrant_number, color, "Entry"))
                                                    ball_positions[quadrant_number].append((cX, cY))
                                                    dic2[num1] =1
                                                                   
                                        num = quadrant_number
                                        if dic[num] == empty:
                                            Time=calculate_timestamp(frame_number, fps)
                                            cv2.circle(frameResized, (cX, cY), 10, (0, 255, 0), -1)
                                            cv2.putText(frameResized, f"Color: {color} Time : {Time} Sec", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                            dic[num] = 1
                 
                                else:
                                      if ball_positions[quadrant_number] != empty:
                                        #if (cX, cY) in ball_positions[quadrant_number]:
                                            
                                            events.append((calculate_timestamp(frame_number, fps), quadrant_number, color, "Exit"))
                                            ball_positions[quadrant_number].pop() 
                                            dic2 = {1:[],2:[],3:[],4:[]}
                        
                    
            out.write(frameResized)
            cv2.imshow("result",frameResized)
            if cv2.waitKey(1) & 0xFF==ord('d'):
                               break 
    #out.write(frameResized)        

    dic = {1:[],2:[],3:[],4:[]}
cap.release()

# Entering all the values into output.txt file
output_text_file = "video\output.txt"
with open(output_text_file, 'w') as file:
        for event in events:
            file.write(f"{event[0]}, {event[1]}, {event[2]}, {event[3]}\n")    