import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    if os.getenv("FLASK_ENV") == "development":
        import debugpy
        debugpy.listen(('0.0.0.0', 5678))
        print("Debugger is active and waiting for connection...")
        debugpy.wait_for_client()

    app.run()
