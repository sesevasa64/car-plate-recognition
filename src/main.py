from .app import App
from .pipeline import YoloPipeline, NomeroffPipeline

def main():
    pipeline = NomeroffPipeline.default()
    app = App("settings.json", pipeline)
    app.run()

if __name__ == "__main__":
    main()
