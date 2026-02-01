import cv2

class MotionDetector:
    def __init__(self, blur_size, min_delta, motion_threshold):
        self.blur_size = blur_size
        self.min_delta = min_delta
        self.motion_threshold = motion_threshold
        self.prev_gray = None

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, self.blur_size, 0)

        if self.prev_gray is None:
            self.prev_gray = gray
            return False
        
        frame_delta = cv2.absdiff(self.prev_gray, gray)
        thresh = cv2.threshold(
            frame_delta, self.min_delta, 255, cv2.THRESH_BINARY
        )[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        self.prev_gray = gray

        for contour in contours:
            if cv2.contourArea(contour) > self.motion_threshold:
                return True

        return False