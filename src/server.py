from flask import Flask, redirect, url_for, request,jsonify
from flask_cors import CORS
# import pyodbc
# from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import sqlalchemy as db
import psycopg2
import os

# fn = "/home/ggdhines/PycharmProjects/historical-transcriptions/dataframes/latent1.cvs"
# tiles_to_process = pd.read_csv(fn,delimiter=" ",error_bad_lines=False, engine="python",quoting=3)

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://ghines:123456@127.0.0.1:5432/historical-transcriptions"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
# connection = pyodbc.connect('Driver={Devart ODBC Driver for PostgreSQL};Server=.;Database=historical-transcriptions;uid=ghines;pwd=123456')
# db = SQLAlchemy(app)

# class User(db.Model):
#     tile_index = db.Column(db.Integer, primary_key=True)
#     top = db.Column(db.Integer, primary_key=True)
#     left = db.Column(db.Integer, primary_key=True)
#     bottom = db.Column(db.Integer, primary_key=True)
#     right = db.Column(db.Integer, primary_key=True)
#     language_model  = db.Column(db.String(40))
#
#     def __repr__(self):
#         return str(self.tile_index)

# engine = db.create_engine('postgres://ghines:123456@127.0.0.1:5432/historical-transcriptions')

# def query_db(query, args=(), one=False):
#     cur = conn().cursor()
#     cur.execute(query, args)
#     r = [dict((cur.description[i][0], value) \
#                for i, value in enumerate(row)) for row in cur.fetchall()]
#     cur.connection.close()
#     return (r[0] if r else None) if one else r
engine = db.create_engine('postgres://ghines:123456@127.0.0.1:5432/historical-transcriptions')


@app.route("/getTile", methods=['POST', 'GET'])
def helloWorld():
    # conn = psycopg2.connect("dbname='historical-transcriptions' user='ghines' host='localhost' password='123456'")
    # cur = conn.cursor(
    # cur.execute("select * from tesseractResults limit 1")
    # print(cur.fetchone())
    # engine = db.create_engine('postgres://ghines:123456@127.0.0.1:5432/historical-transcriptions')
    with engine.connect() as connection:
        result = connection.execute("select * from pages inner join tesseract_results on tesseract_results.page_id = pages.page_id where darkest_pixel < 150 limit 1")


        d = dict(list(result)[0])
        return jsonify(d)
        return jsonify({'result': [dict(row) for row in result]})
        # return jsonify(result)

    # print(pd.read_sql("pages",engine))
    # return query_db("select * from tesseractResults limit 1")
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