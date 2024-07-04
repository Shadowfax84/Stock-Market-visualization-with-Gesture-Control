import cv2
import mediapipe as mp
import pyautogui

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Get screen size for scaling mouse movements
screen_width, screen_height = pyautogui.size()

# Function to normalize hand landmark positions


def normalize_landmark(x, y, frame_shape):
    return int(x * frame_shape[1]), int(y * frame_shape[0])


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB and flip horizontally for a mirrored view
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 1)
    frame.flags.writeable = False

    # Process the frame with MediaPipe Hands
    results = hands.process(frame)

    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the index finger tip position
            index_finger_tip_x, index_finger_tip_y = normalize_landmark(
                hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y, frame.shape)

            # Scale to screen size
            screen_x = screen_width * hand_landmarks.landmark[8].x
            screen_y = screen_height * hand_landmarks.landmark[8].y

            # Move the mouse cursor to the index finger tip position
            pyautogui.moveTo(screen_x, screen_y)

            # Color the tip of the index finger as red
            cv2.circle(frame, (index_finger_tip_x,
                       index_finger_tip_y), 5, (0, 0, 255), -1)

            # Get positions of thumb, index, middle, and little fingers
            thumb_tip_y = hand_landmarks.landmark[4].y
            thumb_tip_x = hand_landmarks.landmark[4].x
            thumb_ip_y = hand_landmarks.landmark[3].y
            thumb_ip_x = hand_landmarks.landmark[3].x
            index_finger_pip_y = hand_landmarks.landmark[6].y
            middle_finger_tip_y = hand_landmarks.landmark[12].y
            middle_finger_pip_y = hand_landmarks.landmark[10].y
            little_finger_tip_y = hand_landmarks.landmark[20].y
            little_finger_pip_y = hand_landmarks.landmark[18].y

            # Detect scroll up (index and middle fingers up, thumb to the right 90 degrees to the index finger)
            if (hand_landmarks.landmark[8].y < index_finger_pip_y and
                hand_landmarks.landmark[12].y < middle_finger_pip_y and
                abs(thumb_tip_y - thumb_ip_y) < 0.05 and
                    thumb_tip_x > thumb_ip_x):
                pyautogui.scroll(10)

            # Detect scroll down (index and middle fingers down, thumb to the right 90 degrees to the index finger)
            elif (hand_landmarks.landmark[8].y > index_finger_pip_y and
                  hand_landmarks.landmark[12].y > middle_finger_pip_y and
                  abs(thumb_tip_y - thumb_ip_y) < 0.05 and
                  thumb_tip_x > thumb_ip_x):
                pyautogui.scroll(-10)

            # Detect right click (index and little fingers up)
            elif (hand_landmarks.landmark[8].y < index_finger_pip_y and
                  hand_landmarks.landmark[20].y < little_finger_pip_y and
                  abs(thumb_tip_y - thumb_ip_y) >= 0.05):
                pyautogui.rightClick()

            # Detect left click (index and little fingers up, thumb to the right 90 degrees to the index finger)
            elif (hand_landmarks.landmark[8].y < index_finger_pip_y and
                  hand_landmarks.landmark[20].y < little_finger_pip_y and
                  abs(thumb_tip_y - thumb_ip_y) < 0.05 and
                  thumb_tip_x > thumb_ip_x):
                pyautogui.click()

    # Show the frame
    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
