import cv2
import os

PERSON_CLASS_ID = 15

class PersonDetector:
    def __init__(self, model_dir, confidence=0.6):
        proto = os.path.join(model_dir, "MobileNetSSD_deploy.prototxt")
        model = os.path.join(model_dir, "MobileNetSSD_deploy.caffemodel")

        self.net = cv2.dnn.readNetFromCaffe(proto, model)
        self.confidence = confidence

    def detect(self, frame):
        (h, w) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            0.007843,
            (300, 300),
            127.5
        )

        self.net.setInput(blob)
        detections = self.net.forward()

        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            class_id = int(detections[0, 0, i, 1])

            if conf > self.confidence and class_id == PERSON_CLASS_ID:
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (x1, y1, x2, y2) = box.astype("int")

                x = max(0, x1)
                y = max(0, y1)
                w_box = max(0, x2 - x1)
                h_box = max(0, y2 - y1)

                return (x, y, w_box, h_box)
            
        return None