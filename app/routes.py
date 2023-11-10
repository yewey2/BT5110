from flask import Blueprint, render_template, request
from flask import jsonify
import pandas as pd, numpy as np, os, json, psycopg2
from sqlalchemy import create_engine


if os.environ.get('PG_PASSWORD'):
    print('password set for postgres')
else:
    print('no password set for postgres')

api_key = os.environ.get('MAPBOX_TOKEN')

# Connect to server
try:
    conn = psycopg2.connect(database="mmsi",
                            host="localhost",
                            user="postgres",
                            password=os.environ.get("PG_PASSWORD"),
                            port=5432)
except:
    print("Cannot connect to SQL server")
main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", test="testing", api_key = api_key)

@main.route("/map")
def map():
    return render_template("map.html", test="testing",  api_key = api_key)


@main.route('/querydata', methods = ['POST'])
def querydata():
    if request.method == 'POST':
        query = request.form.get('sql-query')
        print(query)
        select_index = query.lower().find("select")
        from_index = query.lower().find("from")
        select_clause = query[select_index + len('select') : from_index].strip()
        try:
            cursor = conn.cursor()
            cursor.execute("commit")
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [i.split(' as ')[-1].strip() for i in select_clause.split(',')]
            # columns = ["mmsi", "lon", "lat"]
            result = pd.DataFrame(result, columns=columns).to_json()
            cursor.close()
            return jsonify(
                {
                    'status': 'success',
                    'query': query,
                    'result': result
                }
            )
        except Exception as e:
            return jsonify(        
                {
                    'status': 'error',
                    'query': query,
                    'result': str(e),
                }
            )
    
    return jsonify(        
        {
            'status': 'not post',
            'query': query,
            'result': ''
        }
    )
    




# view2 = Blueprint("view2", __name__)
# @view2.route("/view2")
# def index():
#     return render_template("view2.html", test="testing")

# check_status = Blueprint("check_status", __name__)
# @check_status.route("/check_status", methods=['POST'])
# def index():
#     data = request.form
#     return render_template("check_status.html", test="testing", data=data)
