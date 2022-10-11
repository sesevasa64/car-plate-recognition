import cv2
import torch
import easyocr
from nomeroff_net.pipelines.number_plate_localization import NumberPlateLocalization


class Pipeline:
    def __init__(self, detector, reader):
        self.detector = detector
        self.reader = reader

    def __call__(self, frame):
        return NotImplementedError()

    @staticmethod
    def default():
        return NotImplementedError() 


class NomeroffPipeline(Pipeline):
    def __init__(self, detector, reader):
        super().__init__(detector, reader)

    def __call__(self, frame):
        outputs = self.detector.forward(frame)[0]
        numberplate = outputs[1]
        for *coords, conf in numberplate:
            x1, y1, x2, y2 = map(int, coords)
            cv2.rectangle(
                frame, (x1, y1), (x2, y2), (0, 0, 255), 2
            )
            cropped_image = frame[y1:y2, x1:x2]
            if len(cropped_image) == 0:
                continue
            result = self.reader.readtext(cropped_image)
            if len(result) == 0:
                continue
            numberplate = max(result, key=lambda x:x[2])
            _, content, _ = numberplate
            size = 1
            thickness = 2
            font = cv2.FONT_HERSHEY_PLAIN
            (label_width, label_height), baseline = cv2.getTextSize(content, font, size, thickness)
            offset = label_height - baseline
            cv2.rectangle(
                frame, (x1, y1 - label_height - baseline), (x1 + label_width, y1), (0, 0, 255), -1
            )
            cv2.putText(frame, content, (x1, y1 - offset), font, size, (255, 255, 255), thickness)
        return frame

    @classmethod
    def default(cls):
        detection = NumberPlateLocalization("number_plate_localization", None)
        reader = easyocr.Reader(['en'], recog_network='custom_model')
        return cls(detection, reader)
