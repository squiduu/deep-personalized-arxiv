import requests
from db import Db
from flask import jsonify, request
from flask_restx import Namespace, Resource
from utils import MODEL_CONTAINER_URL, token_required

Papers = Namespace("Papers")


@Papers.route("/search")
class PaperSearch(Resource):
    def __init__(self):
        super(PaperSearch).__init__()
        conn = Db()
        self.db = conn.db

    @token_required
    def post(self, current_user):
        user_id = current_user["user_id"]

        json_data = request.get_json()
        category1 = json_data["cat1"]
        category2 = json_data["cat2"]

        if "text" in json_data:
            query = json_data["text"]
            embed_search_url = MODEL_CONTAINER_URL + "embed_search"

            papers = requests.post(
                embed_search_url,
                json={"cat1": category1, "cat2": category2, "query": query},
            )

            return jsonify({"result": papers}), 200

        else:
            user_info = self.db.users.find_one({"user_id": user_id})

            if category2 == "all":
                cluster_centroids = [c for c in user_info["centroids"][category1]]
                document_ids = requests.post(
                    MODEL_CONTAINER_URL + "document_search",
                    json={"centroids": cluster_centroids},
                )
                papers = self.db.papers.find({"_id": {"$in": document_ids}})

                return jsonify({"result": papers}), 200

            else:
                cluster_centroid = user_info["centroids"][category2]
                document_ids = requests.post(
                    MODEL_CONTAINER_URL + "document_search",
                    json={"centroids": cluster_centroid},
                )
                papers = self.db.papers.find({"_id": {"$in": document_ids}})

                return jsonify({"result": papers}), 200


@Papers.route("/like")
class PaperLike(Resource):
    def __init__(self):
        super(PaperLike).__init__()
        conn = Db()
        self.db = conn.db

    @token_required
    def post(self, current_user):
        json_data = request.get_json()
        paper_cat2 = json_data["cat2"]
        paper_id = json_data["paper_id"]

        user_info = self.db.users.find_one({"user_id": current_user["user_id"]})

        user_centroid = user_info["centroids"][paper_cat2]

        centroid_move_url = MODEL_CONTAINER_URL + "move_centroid"
        new_centroid = requests.post(
            centroid_move_url, json={"centroid": user_centroid, "paper_id": paper_id}
        )

        user_info["centroids"][paper_cat2] = new_centroid

        self.db.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": {"centroids": user_info["centroids"]}},
        )
