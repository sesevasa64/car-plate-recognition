from .app import App
from .pipeline import Pipeline


def main():
    pipeline = Pipeline.default()
    app = App("settings.json", pipeline)
    app.run()

if __name__ == "__main__":
    main()
