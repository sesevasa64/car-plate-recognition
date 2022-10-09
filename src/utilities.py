import cv2
import json


def load_json(filename):
    with open(filename) as file:
        result = json.load(file)
    return result

# Создание потока для чтения на основе входящего потока
def create_output_stream(cap, filename):
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter(
        filename, cv2.VideoWriter_fourcc(*"mp4v"), 
        fps, (frame_width, frame_height)
    )
    return out
