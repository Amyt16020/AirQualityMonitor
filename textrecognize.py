import cv2

def func1(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    _, bw = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(
        bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        if w > 20 and h > 40:
            cv2.rectangle(frame, (x, y), (x+w, y+h),(255, 0, 0), 2)

    return frame
    #cv2.imshow("auto detect", frame)
