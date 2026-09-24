from app import create_app

app = create_app()

if __name__ == "__main__":
    # Port 5555 avoids macOS AirPlay, which often occupies port 5000.
    app.run(debug=True, port=5555)
