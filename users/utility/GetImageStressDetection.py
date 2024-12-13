import os
import random
import time
from django.conf import settings
from PyEmotion import *
import cv2 as cv

from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from users.models import UserImagePredictinModel

class ImageExpressionDetect:
    def __init__(self):
        # Initialize PyEmotion once when the class is instantiated
        PyEmotion()
        try:
            self.er = DetectFace(device='gpu', gpu_id=0)
        
        except Exception as e:
            print(f"GPU initialization failed, falling back to CPU. Error: {e}")
            self.er = DetectFace(device='cpu')


    def classify_stress(self, emotion):
        # Define which emotions are classified as "In Stress" or "Not in Stress"
        stress_map = {
            "Happy": "Not in Stress",
            "Neutral": "Not in Stress",
            "Sad": "In Stress",
            "Angry": "In Stress",
            "Fear": "In Stress",
            "Disgust": "In Stress",
            "Surprise": "Not in Stress"
        }
        return stress_map.get(emotion, "Unknown")

    def overlay_text(self, frame, text, position=(10, 30), text_color=(255, 255, 255), background_color=(0, 0, 0), font_scale=0.6, thickness=2):
        """Helper function to overlay text with a background on the image at a fixed position."""
        # Get the size of the text box
        (text_width, text_height), baseline = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        x, y = position

        # Draw a filled rectangle as the background for the text
        cv.rectangle(frame, (x, y - text_height - baseline), (x + text_width, y + baseline), background_color, thickness=cv.FILLED)
        
        # Overlay the text over the background
        cv.putText(frame, text, (x, y), cv.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)

    def getExpression(self, imagepath):
        filepath = os.path.join(settings.MEDIA_ROOT, imagepath)

        # Check if the image file exists
        if not os.path.exists(filepath):
            print(f"Image file not found: {filepath}")
            return None

        try:
            # Read the image and predict emotion
            frame, emotion = self.er.predict_emotion(cv.imread(filepath))
            
            # Classify the detected emotion
            stress_status = self.classify_stress(emotion)
            
            # Print emotion and stress classification in the desired format
            result = (emotion, stress_status)
            print(result)  # Example: ('Happy', 'Not in Stress')

            # Add overlay text to the frame
            self.overlay_text(frame, f"Emotion: {emotion}", position=(10, 30), text_color=(255, 255, 255), background_color=(0, 0, 0))
            self.overlay_text(frame, f"Stress Status: {stress_status}", position=(10, 60), text_color=(255, 255, 255), background_color=(0, 0, 0))

            # Set window to full screen
            cv.namedWindow('Emotion Detection', cv.WND_PROP_FULLSCREEN)
            cv.setWindowProperty('Emotion Detection', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

            # Display the image with overlay text
            cv.imshow('Emotion Detection', frame)
            cv.waitKey(0)
            cv.destroyAllWindows()

            return result
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return None



    def getLiveDetect(self, request):
        print("Live emotion detection started...")
        # Open default camera
        cap = cv.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera")
            return

        try:
            # Generate the first random interval
            next_capture_time = time.time() + random.uniform(10, 30)  # Random interval between 3 to 10 seconds
        
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # Save the original frame before processing
                original_frame = frame.copy()  

                # Check if it's time to capture an image
                if time.time() >= next_capture_time:

                    
                    stress_status = self.classify_stress(emotion)
                    result = (emotion, stress_status)

                    timestamp = int(time.time())
                    # Save the unprocessed, original frame (raw frame without emotion detection)
                    filename = f"captured_{int(time.time())}.jpg"
                    filepath = os.path.join(settings.MEDIA_ROOT, filename)
                    cv.imwrite(filepath, original_frame)  # Save the raw frame (no emotion detection or bounding box)
                    print(f"Captured and saved original image: {filepath}")

                    # Get user details from session
                    username = request.session.get('loggeduser', 'Anonymous')
                    email = request.session.get('email', 'unknown@example.com')
                    loginid = request.session.get('loginid', 'unknown')

                    # Save to database
                    file_url = os.path.join('/media', filename).replace("\\", "/")  # Relative file path for FileField
                    UserImagePredictinModel.objects.create(
                        username=username,
                        email=email,
                        loginid=loginid,
                        filename=filename,
                        emotions=str(result),
                        file=file_url,
                        cdate=now()
                    )
                    print(f"Original image saved to database for user: {username}")
            
                    # Set the next random capture time
                    next_capture_time = time.time() + random.uniform(10, 30)  # Random interval between 3 to 10 seconds
                    continue  # Skip emotion detection for this frame, just save it

                # Predict emotion (processed frame with overlays)
                processed_frame, emotion = self.er.predict_emotion(frame)
                stress_status = self.classify_stress(emotion)

                # Set window to full screen
                cv.namedWindow('Live Emotion Detection', cv.WND_PROP_FULLSCREEN)
                cv.setWindowProperty('Live Emotion Detection', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

                # Resize the frame to fit the screen while maintaining aspect ratio
                screen_width = cv.getWindowImageRect('Live Emotion Detection')[2]
                screen_height = cv.getWindowImageRect('Live Emotion Detection')[3]
                h, w = frame.shape[:2]
                aspect_ratio = w / h

                if screen_width / screen_height > aspect_ratio:
                    new_width = int(screen_height * aspect_ratio)
                    new_height = screen_height
                else:
                    new_width = screen_width
                    new_height = int(screen_width / aspect_ratio)

                resized_frame = cv.resize(frame, (new_width, new_height))

                # Center the image in the window
                top = (screen_height - new_height) // 2
                bottom = screen_height - new_height - top
                left = (screen_width - new_width) // 2
                right = screen_width - new_width - left

                # Add black borders to center the image
                bordered_frame = cv.copyMakeBorder(resized_frame, top, bottom, left, right, cv.BORDER_CONSTANT, value=(0, 0, 0))

                # Add overlay text after resizing and centering
                self.overlay_text(bordered_frame, f"Emotion: {emotion}", (10, 30), text_color=(255, 255, 255), background_color=(0, 0, 0))
                self.overlay_text(bordered_frame, f"Stress Status: {stress_status}", (10, 60), text_color=(255, 255, 255), background_color=(0, 0, 0))

                # Show the live feed with text
                cv.imshow('Live Emotion Detection', bordered_frame)
                print(f"Emotion detected: {emotion} | Stress classification: {stress_status}")

                # Exit on pressing 'q'
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            # Release resources
            cap.release()
            cv.destroyAllWindows()
            print("Live emotion detection stopped.")
