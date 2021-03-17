from flask import Flask, redirect, url_for, request,jsonify
from flask_cors import CORS
import sqlalchemy as db
import pandas as pd

app = Flask(__name__)
CORS(app)

with open("/home/ggdhines/password","r") as f:
    user_id,psswd = f.read().strip().split(",")

engine = db.create_engine(f'postgres://{user_id}:{psswd}@127.0.0.1:5432/historical-transcriptions')


@app.route("/getTile", methods=['POST', 'GET'])
def get_tile():
    with engine.connect() as connection:
        with open("base_tile_query.sql", "r") as f:
            stmt = f.read()
        result = connection.execute(stmt)

        d = dict(list(result)[0])
        return jsonify(d)


@app.route("/submitTile", methods=['POST'])
def submit_tile():
    payload = request.get_json()

    df = pd.DataFrame.from_records(payload["identified_characters"])
    df["file_prefix"] = payload["file_prefix"]
    df["tesseract_model"] = payload["tesseract_model"]
    df["cvae_model"] = payload["cvae_model"]
    df["local_tile_index"] = payload["local_tile_index"]
    print(df)

    df.to_sql("user_results", engine.connect(), if_exists="append", index=False)

    return 'JSON Object Example'


if __name__ == '__main__':
    app.run(debug=True)
