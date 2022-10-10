from .app import App
from .pipeline import YoloPipeline, NomeroffPipeline, ClassicPipeline

def main():
    pipeline = ClassicPipeline.default()
    app = App("settings.json", pipeline)
    app.run()

if __name__ == "__main__":
    main()
