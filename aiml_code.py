from tkinter import *
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import pyttsx3

# Initialize the main window
win = Tk()
width = win.winfo_screenwidth()
height = win.winfo_screenheight()
win.geometry("%dx%d" % (width, height))
win.configure(bg="#FFFFF7")
win.title('SIGN LANGUAGE CONVERTER')

# Global variables
global img, finalImage, finger_tips, thumb_tip, cap, image, rgb, hand, results, _, w, \
    h, status, mpDraw, mpHands, hands, label1, upCount, cshow

cap = None

# Heading label
Label(win, text='SIGN LANGUAGE CONVERTER', font=('Helvetica', 18, 'bold'), bd=5, bg='black', fg='white', relief=SOLID, width=200) \
    .pack(pady=15, padx=300)

# Initialize hand detection and video capture
def wine():
    global finger_tips, thumb_tip, mpDraw, mpHands, cap, w, h, hands, label1, img
    finger_tips = [8, 12, 16, 20]  # Finger landmarks
    thumb_tip = 4  # Thumb landmark
    w = 500  # Width of the video frame
    h = 400  # Height of the video frame

    if cap:
        cap.release()  # Release the previous video capture

    label1 = Label(win, width=w, height=h, bg="#FFFFF7")
    label1.place(x=40, y=200)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)  # Start video capture

# Hand gesture detection
def live():
    global v, upCount, cshow, img
    cshow = ""
    upCount = StringVar()
    _, img = cap.read()

    img = cv2.resize(img, (w, h))
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm_list = [lm for lm in hand.landmark]
            finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky tips
            finger_fold_status = [lm_list[tip].y > lm_list[tip - 2].y for tip in finger_tips]  # Check Y-axis for folding

            thumb_tip = lm_list[4]
            thumb_base = lm_list[2]
            index_tip = lm_list[8]
            middle_tip = lm_list[12]
            ring_tip = lm_list[16]
            pinky_tip = lm_list[20]

            # Letter Conditions (Order matters!)
            # A: Fist (thumb out)
            if all(finger_fold_status) and thumb_tip.y < thumb_base.y:
                cshow = "A"
            # B: Flat hand (all fingers up)
            elif not any(finger_fold_status) and thumb_tip.y < thumb_base.y:
                cshow = "B"
            # C: Curved hand (partial bend)
            elif (lm_list[8].y > lm_list[6].y and lm_list[8].y < lm_list[5].y) and \
                    (lm_list[12].y > lm_list[10].y and lm_list[12].y < lm_list[9].y):
                cshow = "C"
            # D: Index up, others folded
            elif finger_fold_status == [False, True, True, True] and thumb_tip.y < thumb_base.y:
                cshow = "D"
            # E: All fingers folded (thumb tucked)
            elif all(finger_fold_status) and thumb_tip.y > thumb_base.y:
                cshow = "E"
            # F: OK sign (thumb-index touch, others up)
            elif ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5 < 0.05 \
                    and not any(finger_fold_status[1:]):
                cshow = "F"
            # G: Index pointing, thumb tucked
            elif finger_fold_status == [False, True, True, True] and thumb_tip.y > thumb_base.y:
                cshow = "G"
            # H: Index and middle up (close)
            elif finger_fold_status == [False, False, True, True] and \
                    abs(index_tip.x - middle_tip.x) < 0.05:
                cshow = "H"
            # I: Pinky up, others folded
            elif finger_fold_status == [True, True, True, False] and thumb_tip.y < thumb_base.y:
                cshow = "I"
            # J: (Static approximation: Pinky up + thumb out)
            elif finger_fold_status == [True, True, True, False] and thumb_tip.x < thumb_base.x:
                cshow = "J"
            # K: Thumb and index extended (like gun)
            elif finger_fold_status == [False, True, True, True] and thumb_tip.y < thumb_base.y and \
                    thumb_tip.x > index_tip.x:
                cshow = "K"
            # L: Index and thumb extended (L-shape)
            elif finger_fold_status == [False, True, True, True] and thumb_tip.x < thumb_base.x:
                cshow = "L"
            # M: Thumb tucked under index
            elif all(finger_fold_status) and thumb_tip.y > lm_list[9].y:
                cshow = "M"
            # N: Thumb tucked under middle
            elif all(finger_fold_status) and thumb_tip.y > lm_list[10].y:
                cshow = "N"
            # O: All fingertips touching thumb
            elif ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5 < 0.05 and \
                    ((thumb_tip.x - middle_tip.x) ** 2 + (thumb_tip.y - middle_tip.y) ** 2) ** 0.5 < 0.05:
                cshow = "O"
            # P: Thumb and middle extended (downward)
            elif finger_fold_status == [True, False, True, True] and thumb_tip.y < thumb_base.y:
                cshow = "P"
            # Q: Thumb and pinky extended
            elif finger_fold_status == [True, True, True, False] and thumb_tip.y < thumb_base.y:
                cshow = "Q"
            # R: Crossed index and middle
            elif finger_fold_status == [False, False, True, True] and middle_tip.x < index_tip.x:
                cshow = "R"
            # S: Fist (thumb over fingers)
            elif all(finger_fold_status) and thumb_tip.y > thumb_base.y:
                cshow = "S"
            # T: Thumb between index and middle
            elif all(finger_fold_status) and thumb_tip.y < index_tip.y and thumb_tip.y < middle_tip.y:
                cshow = "T"
            # U: Index and middle up (apart)
            elif finger_fold_status == [False, False, True, True] and \
                    abs(index_tip.x - middle_tip.x) > 0.1:
                cshow = "U"
            # V: Peace sign
            elif finger_fold_status == [False, False, True, True]:
                cshow = "V"
            # W: Three fingers up (index, middle, ring)
            elif finger_fold_status == [False, False, False, True]:
                cshow = "W"
            # X: Index finger bent
            elif finger_fold_status == [True, True, True, True] and index_tip.y > lm_list[6].y:
                cshow = "X"
            # Y: Thumb and pinky out
            elif finger_fold_status == [True, True, True, False] and thumb_tip.y < thumb_base.y:
                cshow = "Y"
            # Z: (Static approximation: Index out, thumb crossed)
            elif finger_fold_status == [False, True, True, True] and thumb_tip.x < index_tip.x:
                cshow = "Z"
            else:
                cshow = ""

            upCount.set(cshow)
            mpDraw.draw_landmarks(rgb, hand, mpHands.HAND_CONNECTIONS)

    # Overlay the detected letter on the video feed
    cv2.putText(rgb, f"Detected Letter: {cshow}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    # Display the processed image
    image = Image.fromarray(rgb)
    finalImage = ImageTk.PhotoImage(image)
    label1.configure(image=finalImage)
    label1.image = finalImage

    # Repeat the live function
    win.after(1, live)

# Speak the detected letter
def voice():
    engine = pyttsx3.init()
    engine.say(upCount.get())
    engine.runAndWait()

# Initialize the GUI
wine()

# Buttons
button_width = 15  # Width of the buttons
button_height = 2   # Height of the buttons
button_font = ('Helvetica', 12, 'bold')  # Font for the buttons

# Calculate the vertical center for the buttons
button_y_start = height // 2 - 100  # Start 100 pixels above the center

# Live Button
Button(win, text='Live', bg='black', fg='white', relief=RAISED, width=button_width, height=button_height, font=button_font, command=live) \
    .place(x=width - 250, y=button_y_start)

# Sound Button
Button(win, text='Sound', bg='black', fg='white', relief=RAISED, width=button_width, height=button_height, font=button_font, command=voice) \
    .place(x=width - 250, y=button_y_start + 100)

# Exit Button
Button(win, text='Exit', bg='black', fg='white', relief=RAISED, width=button_width, height=button_height, font=button_font, command=win.destroy) \
    .place(x=width - 250, y=button_y_start + 200)

# Run the main loop
win.mainloop()