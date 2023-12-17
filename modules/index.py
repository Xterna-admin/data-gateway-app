from app import app

# Define route "/" & "/<name>"
@app.route("/")
@app.route("/<name>")
def index(name='Anonymous'):
    return f"Hello {name}!!"
