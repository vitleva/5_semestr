from flask import Flask
app = Flask(__name__)

@app.route("/")
def start():
    return """<!DOCTYPE html>
        <html>
           <body>
               <h1>web-сервер на flask</h1>
           </body>
        </html>"""


