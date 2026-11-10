from app import create_app
from waitress import serve

app = create_app()
if __name__ == "__main__":
    print("PC Parts Shop: http://localhost:5000 | Swagger: http://localhost:5000/apidocs")
    serve(app, host="127.0.0.1", port=5000, threads=16)
