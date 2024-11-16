from flask import Flask, render_template, request, jsonify, make_response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

#@app.route("/process", methods = ["POST"])
#def process_inputml():
    #return jsonify()

if __name__ == "__main__":
    app.run(debug = True)