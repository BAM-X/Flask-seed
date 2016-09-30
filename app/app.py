from flask import Flask, jsonify
from flask.views import MethodView

app = Flask(__name__)

class HelloWorldView(MethodView):
    def get(self):
        return jsonify(data="Hello, World!")

app.add_url_rule('/', view_func=HelloWorldView.as_view('hello_world'), methods=['GET',])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
