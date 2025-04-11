from app import create_app

app = create_app()

if __name__ == "__main__":
    # Turn off debug=True when finished. Security concern.
    app.run(debug=True, host="0.0.0.0")