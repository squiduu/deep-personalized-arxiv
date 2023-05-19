from flask import Flask, request
from flask_restx import Api, Resource
import pickle


app = Flask(__name__, template_folder="./templates")
api = Api(app)


@api.route("/api/create_centroid")
class CreateCentroid(Resource):
    def get(self):
        with open("./data/centroid.pkl", "r") as f:
            centroid = pickle.load(f)

        return centroid


@api.route("/api/embed_search")
class EmbedSearch(Resource):
    def post(self):
        cat1 = request.json["cat1"]
        cat2 = request.json["cat2"]
        query = request.json["query"]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
