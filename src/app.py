import cv2
import time
from threading import Event
from queue import Queue, Empty, Full
from concurrent.futures import Future, ThreadPoolExecutor
from .utilities import load_json, create_output_stream
from .pipeline import Pipeline


class App:
    def __init__(self, settings_filename, pipeline: Pipeline) -> None:
        self.opt = load_json(settings_filename)
        self.event = Event()
        self.frame_queue = Queue(maxsize=60)
        self.output_queue = Queue(maxsize=60)
        self.executor = ThreadPoolExecutor()
        self.pipeline = pipeline

    # Read from sources
    def __producer(self, source, filename):
        cap = cv2.VideoCapture(source)
        out = create_output_stream(cap, filename)
        while cap.isOpened() and not self.event.is_set():
            result, frame = cap.read()
            if not result: 
                break
            try:
                self.frame_queue.put((frame, out), timeout=1)
            except Full:
                break
            cv2.waitKey(1)
        out.release()
        if __debug__:
            print("producer done")

    # Proceed through pipeline
    def __consumer(self):
        durations = []
        while not self.event.is_set():
            try:
                frame, out = self.frame_queue.get(timeout=1)
            except Empty:
                break
            start = time.time()
            image = self.pipeline(frame)
            end = time.time()
            durations.append(end - start)
            try:
                self.output_queue.put((image, out))
            except Full:
                break
            self.frame_queue.task_done()
            cv2.waitKey(1)
        if __debug__:
            fps = int(1 / (sum(durations) / len(durations)))
            print(f"\nPipeline FPS: {fps}")
            print("consumer done")

    # Write to files
    def __writer(self):
        while True:
            try:
                frame, out = self.output_queue.get(timeout=1)
            except Empty:
                break
            if self.event.is_set():
                self.output_queue.task_done()
                break
            self.output_queue.task_done()
            out.write(frame)
            if self.opt["show"]:
                cv2.imshow(str(out), frame)
            cv2.waitKey(1)
        if __debug__:
            print("writer done")

    def run(self):
        def callback(fut: Future):
            fut.result()
        # Start threads
        futures = []
        sources = self.opt["sources"]
        for values in sources:
            source, filename = values.values()
            future = self.executor.submit(self.__producer, source, filename)
            future.add_done_callback(callback)
            futures.append(future)
            if __debug__:
                print(source, filename)
        future = self.executor.submit(self.__consumer)
        future.add_done_callback(callback)
        futures.append(future)
        future = self.executor.submit(self.__writer)
        future.add_done_callback(callback)
        futures.append(future)
        # Run application
        try:
            start = time.monotonic()
            while True:
                time.sleep(1)
                if __debug__:
                    end = time.monotonic()
                    print(f"\rElapsed: {end - start:.2f}", end="")
        except KeyboardInterrupt:
            self.event.set()
            self.executor.shutdown()
