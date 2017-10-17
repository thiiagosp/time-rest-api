from flask import Flask
from flask import jsonify
from flask import request
import util, app, json

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, Fuck Off!"

@app.route('/todo/times', methods=['GET'])
def get_times():
    times = json.loads(open('data/time.json').read())
    return jsonify(times)


@app.route('/todo/time/<user_id>', methods=['GET'])
def get_time(user_id):
    times = json.loads(open('data/time.json').read())
    times = util.filterUser(times, user_id)
    return jsonify(times)

# @app.route('/todo/times', methods=['POST'])
# def set_time():
#     dataa = request.get_json
#     # times = json.loads(open('data/time.json').read())
#     # return jsonify(times)
# 	return jsonify(times)

if __name__ == '__main__':
	app.run(debug=True)
