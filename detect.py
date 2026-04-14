import cv2
from ultralytics import YOLO
from datetime import datetime
from db import *
from notifier import send_alert
from picamera2 import Picamera2



def open_camera():
    counter = 0
    
    create_db()
    
    model = YOLO('yolov8n.pt')
    
    # Displays the webcam
    # camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
    camera.start()
    
    # I added detect shadows to be true so we can differentiate a shadow from movement
    fgbg = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=200, detectShadows=True)

    # if not camera.isOpened():
    #     print('No Camera Detected.')
    #     exit()
    # Placeholder for drawing rectangle around movement
    last_box = None
    last_label = None
    # Used for providing a cooldown timer for messages sent to Telegram
    last_alert_time = None
    
    while True:
        frame = camera.capture_array()
        print(f"Frame captured, counter: {counter}")
        
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        
        # threshold allows for us to determine what movement will be determined or converted to a white color in each frame
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                
        # if not ret:
        #     print('No more stream')
        #     break
            
        # Apply the mask for the background subtractor
        fgmask = fgbg.apply(thresh)
        
        # Set this condition to ignore the backgroundsubtractor's startup so we dont track any unnecessary movemetn
        if counter > 200:  
              
            # will detect contours for each binary in each frame
            contours, hierarchy = cv2.findContours(image=fgmask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
            
            motion_detected = False
            # Filter out any noise in each frame and only detect when there is movement on the screen
            # Sets the condition for drawing contours around movement
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 500:
                    motion_detected = True
            
            # YOLO should happen every 5 frames when motion is confirmed
            if motion_detected and counter % 5 == 0:
                results = model(frame)
                timestamp = datetime.now()
                timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                # Go through the results list to then filter out data we want
                for rslts in results:
                    boxes = rslts.boxes
                    # Go through individual detections
                    for box in boxes:
                        coords = box.xyxy[0].tolist() 

                        # Take id from YOLO to then display name of object identified
                        class_id_tensor = box.cls[0]
                        class_id = int(class_id_tensor.item())
                    
                        # Find confidence interval from YOLOv8 
                        confidence_tensor = box.conf[0]
                        confidence = float(confidence_tensor.item())

                        class_name = model.names[class_id]
                        # We only want to output when YOLO's conf interval is more 70 or more
                        if confidence >= .75 and class_name == 'person':
                            last_box = coords
                            last_label = f"{class_name} {confidence:.2f}"
            
                            print(f'Detected object: {class_name}, Timestamp: {timestamp_formatted}, Confidence: {confidence:.2f}, Coordinates: {coords}')
                            # Notification gets sent to telegram app on users phone
                            if last_alert_time is None or (datetime.now() - last_alert_time).seconds >= 5: 
                                send_alert(f"Intruder Alert! \n Detected: {class_name} \n Time: {timestamp_formatted} \n Confidence: {(confidence * 100):.2f}%")
                                last_alert_time = datetime.now()
                            # Convert list of floats from coords into a string so that we can ingest into our db
                            db_coords = ", ".join(str(round(c, 2)) for c in coords)                        
                            insert_row(timestamp_formatted, class_name, round(confidence, 2), db_coords)
            # Rectangle around the detection will persist and be drawn around the movement detection        
            if last_box is not None:
                cv2.rectangle(frame, (int(last_box[0]), int(last_box[1])), (int(last_box[2]), int(last_box[3])), (0, 255, 0), 2)
                cv2.putText(frame, last_label, (int(last_box[0]), int(last_box[1]) - 10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 2)
                
                
        # cv2.imshow("Webcam", frame)
        # Press q key to exit program
        # if cv2.waitKey(1) == ord('q'):
        #     break
         
        try:
            while True:
            # your existing loop code
                counter += 1
        except KeyboardInterrupt:
            print("Stopping...")
            camera.stop()   
        # counter += 1
        
    # camera.release()
    
    # cv2.destroyAllWindows()

def main():
    open_camera()
    

if __name__ == "__main__":
    main()