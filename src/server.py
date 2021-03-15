from flask import Flask, redirect, url_for, request,jsonify
from flask_cors import CORS
import sqlalchemy as db

app = Flask(__name__)
CORS(app)

engine = db.create_engine('postgres://ghines:123456@127.0.0.1:5432/historical-transcriptions')

@app.route("/getTile", methods=['POST', 'GET'])
def get_tile():
    with engine.connect() as connection:
        result = connection.execute("select * from pages inner join tesseract_results on tesseract_results.page_id = pages.page_id order by confidence limit 1")

        d = dict(list(result)[0])
        return jsonify(d)

@app.route("/submitTile", methods=['POST'])
def submit_tile():
    payload = request.get_json()

    for a in payload["identified_characters"]:
        print(a)
    return 'JSON Object Example'

if __name__ == '__main__':
    app.run(debug = True)