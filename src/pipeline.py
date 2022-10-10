import cv2
import torch
import easyocr
from nomeroff_net.pipelines.number_plate_localization import NumberPlateLocalization
from nomeroff_net.pipes.number_plate_localizators.yolo_v5_detector import Detector


class Pipeline:
    def __init__(self, detector, reader):
        self.detector = detector
        self.reader = reader

    def __call__(self, frame):
        return NotImplementedError()

    @staticmethod
    def default():
        return NotImplementedError() 


class YoloPipeline(Pipeline):
    def __init__(self, detector, reader):
        super().__init__(detector, reader)

    def __call__(self, frame):
        with torch.no_grad():
            outputs = self.detector(frame)
        image = outputs.ims[0]
        for *coords, conf, cls in outputs.xyxy[0].to("cpu"):
            if cls != 2:
                break
            x1, y1, x2, y2 = map(int, coords)
            cv2.rectangle(
                image, (x1, y1), (x2, y2), (0, 0, 255), 2
            )
        return image

    @classmethod
    def default(cls):
        # Detection
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        model.train(False)
        # Recognition
        reader = easyocr.Reader(["en"])
        return cls(model, reader)


class NomeroffPipeline(Pipeline):
    def __init__(self, detector, reader):
        super().__init__(detector, reader)

    def __call__(self, frame):
        outputs = self.detector.forward(frame)[0]
        numberplate = outputs[1]
        for *coords, conf in numberplate:
            print(1)
            x1, y1, x2, y2 = map(int, coords)
            cv2.rectangle(
                frame, (x1, y1), (x2, y2), (0, 0, 255), 2
            )
        return frame

    @classmethod
    def default(cls):
        detection = NumberPlateLocalization("number_plate_localization", None)
        reader = easyocr.Reader(["en"])
        return cls(detection, reader)


class ClassicPipeline(Pipeline):
    def __init__(self, detector, reader):
        super().__init__(detector, reader)

    def __call__(self, frame):
        model_outputs = self.detector.predict(frame)
        if len(model_outputs) == 0:
            return frame
        if len(model_outputs[0]) == 0:
            return frame
        model_outputs_int = [int(i) for i in model_outputs[0][0]]
        x1_res, y1_res, x2_res, y2_res, _ = model_outputs_int
        cv2.rectangle(
            frame, (x1_res, y1_res), (x2_res, y2_res), (0, 0, 255), 2
        )
        return frame

    @classmethod
    def default(cls):
        detection = Detector()
        detection.load()
        reader = easyocr.Reader(["en"])
        return cls(detection, reader)
