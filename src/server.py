from flask import Flask, redirect, url_for, request,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/login",methods = ['POST', 'GET'])
def helloWorld():
    return jsonify({"ship": "bear",
                    "year": "1940",
                    "month": "01",
                    "page": "0002",
                    "upper_left_corner_x": 20,
                    "upper_left_corner_y": 20,
                    "width": 40,
                    "height": 40,
                    "character_index": 50})


if __name__ == '__main__':
   app.run(debug = True)