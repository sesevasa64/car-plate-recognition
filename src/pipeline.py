import cv2
import torch
import easyocr


class Pipeline:
    def __init__(self, model, reader):
        self.detection_model = model
        self.reader = reader
    def __call__(self, frame):
        with torch.no_grad():
            outputs = self.detection_model(frame)
        img = outputs.ims[0]
        h, w, _ = img.shape
        for x1, y1, x2, y2, _, _ in outputs.xyxyn[0]:
            cv2.rectangle(
                img, (int(x1*w), int(y1*h)), (int(x2*w), int(y2*h)), (0,0,255), 2
            )
        return img
    @staticmethod
    def default():
        # Detection
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        model.train(False)
        # Recognition
        reader = easyocr.Reader(["en"])
        return Pipeline(model, reader)
