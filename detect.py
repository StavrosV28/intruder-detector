import cv2


def open_camera():
    counter = 0
    
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
                
            # Filter out any noise in each frame and only detect when there is movement on the screen
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 500:
                    cv2.drawContours(frame, [cnt], -1, (0,255,0), 2)
                    print(f"Area of contour: {area}")
                        
            
                
            new_detect = cv2.drawContours(image=frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                
            # flip the camera so its easier to test
            flipped_frame = cv2.flip(new_detect, 1)
                    
                    
            cv2.imshow("Webcam", flipped_frame)
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
    
