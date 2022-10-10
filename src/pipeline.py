import cv2
import torch
import easyocr


class Pipeline:
    def __init__(self, detector, reader):
        self.detector = detector
        self.reader = reader
    def __call__(self, frame):
        with torch.no_grad():
            outputs = self.detector(frame)
        image = outputs.ims[0]
        for *coords, _, _ in outputs.xyxy[0].to("cpu"):
            x1, y1, x2, y2 = map(int, coords)
            cv2.rectangle(
                image, (x1, y1), (x2, y2), (0,0,255), 2
            )
        return image
    @staticmethod
    def default():
        # Detection
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        model.train(False)
        # Recognition
        reader = easyocr.Reader(["en"])
        return Pipeline(model, reader)
