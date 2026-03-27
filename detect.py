import cv2
from ultralytics import YOLO
from datetime import datetime




def open_camera():
    counter = 0
    
    model = YOLO('yolov8n.pt')
    
    # Displays the webcam
    camera = cv2.VideoCapture(0)
    
    # I added detect shadows to be true so we can differentiate a shadow from movement
    fgbg = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=200, detectShadows=True)

    if not camera.isOpened():
        print('No Camera Detected.')
        exit()
            
    while True:
        ret, frame = camera.read()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # threshold allows for us to determine what movement will be determined or converted to a white color in each frame
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                
        if not ret:
            print('No more stream')
            break
            
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
                    cv2.drawContours(frame, [cnt], -1, (0,255,0), 2)
                    motion_detected = True
                    print(f"Area of contour: {area}")
            
            timestamp = datetime.now()
            timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            # YOLO should happen every 10 frames when motion is confirmed
            if motion_detected and counter % 10 == 0:
                results = model(frame)
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
                    
                        print(f'Detected object: {class_name}, Timestamp: {timestamp_formatted}, Confidence: {confidence:.2f}, Coordinates: {coords}')
                    
            # detect_contours = cv2.drawContours(image=frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                
        frame = cv2.flip(frame, 1)
        cv2.imshow("Webcam", frame)
        # Press q key to exit program
        if cv2.waitKey(1) == ord('q'):
            break
            
        counter += 1
        
    camera.release()
    cv2.destroyAllWindows()

def main():
    open_camera()
    

if __name__ == "__main__":
    main()