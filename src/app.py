from flask import Flask,request,jsonify
from main import setup, add_note

app = Flask(__name__)

@app.route("/setup", methods=["POST"])
def setup_endpoint():

    data = request.get_json()

    if not data or "bucket" not in data:
        return jsonify({"success": False,"error":"Bucket name not provided"}), 400
    
    bucket_name = data["bucket"]
    success, error = setup(bucket_name)

    if not success:
        return jsonify({"success":False,"error":error}), 500
    
    return jsonify({"success":True,"bucket":bucket_name})

@app.route("/notes", methods = ["POST"])
def add_note_endpoint():

    data = request.get_json()

    if not data:
        return jsonify({"success": False,"error":"Payload not provided."}), 400
    
    title = data.get("Title")
    content = data.get("Content")

    success, error = add_note(title,content)

    if not success:
         return jsonify({"success":False,"error":error}), 500
    
    return jsonify({"success":True})


if __name__ == "main":
    app.run(debug=True)

    
    



