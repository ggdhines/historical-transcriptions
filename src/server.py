from flask import Flask, redirect, url_for, request,jsonify
from flask_cors import CORS
import sqlalchemy as db
import pandas as pd

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

    df = pd.DataFrame.from_records(payload["identified_characters"])
    df["tesseract_language_model"] = payload["language_model"]
    df["tile_index"] = payload["index_wrt_lang_model"]
    df["page_number"] = payload["page_id"]
    print(df)

    df.to_sql("human_results",engine.connect(),if_exists="append",index=False)


    # with engine.connect() as connection:
    #     print(payload)
    #     print()
    #     # for a in payload["identified_characters"]:
    #     #     if a["character"] is not None:
    #     #         c = "'" + a["character"] + "'"
    #     #     else:
    #     #         c = None
    #     #
    #     #     columns = "(tesseract_language_model,tile_index,upper,left,lower,right,character_s,page_number)"
    #     #
    #     #     if a["upper"] is not None:
    #     #         upper = a["upper"]
    #     #     else:
    #     #         upper = "Null"
    #     #     connection.execute(f"insert into human_results values ('{payload['language_model']}',{payload['index_wrt_lang_model']},{upper},{a['left']},{a['lower']},{a['right']},{c},{payload['page_id']})")
    #     # connection.commit()
    return 'JSON Object Example'

if __name__ == '__main__':
    app.run(debug = True)