import json

from pymongo import MongoClient
from tqdm import tqdm


def read_json(path):
    with open(file=path, mode="r") as fp:
        papers = json.load(fp)

    return papers


def get_db(db_uri):
    client = MongoClient(db_uri)

    return client


def main(db_uri, db_name, collection_name, json_path):
    client = get_db(db_uri)
    db = client[db_name]
    collection = db[collection_name]

    papers = read_json(json_path)

    final_idx = len(papers)

    item_list = []

    for idx, paper in enumerate(tqdm(papers)):
        item_list.append(paper)

        if len(item_list) >= 100:
            collection.insert_many(item_list)
            item_list = []

        elif idx == final_idx - 1:
            collection.insert_many(item_list)

    print("Finished backup")

    client.close()


if __name__ == "__main__":
    db_uri = "mongodb://root:cvpr0372@arxivdb:27017/"
    db_name = "arxiv"
    collection_name = "papers"
    json_path = "./data/papers.json"

    main(db_uri, db_name, collection_name, json_path)
