from flask import Flask, redirect, url_for, request,jsonify
from flask_cors import CORS
import pandas as pd

fn = "/home/ggdhines/PycharmProjects/historical-transcriptions/dataframes/latent1.cvs"
tiles_to_process = pd.read_csv(fn,delimiter=" ",error_bad_lines=False, engine="python",quoting=3)

app = Flask(__name__)
CORS(app)


@app.route("/getTile", methods=['POST', 'GET'])
def helloWorld():
    return jsonify({"ship": "Bear-AG-29",
                    "year": "1940",
                    "month": "01",
                    "page": "39",
                    "upper_left_corner_x": 5987,
                    "upper_left_corner_y": 1245,
                    "width": 6045 - 5987,
                    "height": 1341 - 1245,
                    "character_index": 50})


if __name__ == '__main__':
    app.run(debug = True)