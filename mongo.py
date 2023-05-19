import json
import re

from pymongo import MongoClient, UpdateMany
from tqdm import tqdm


def get_db(db_uri):
    client = MongoClient(db_uri)

    return client


def is_subset(list1, list2):
    return all(element in list2 for element in list1)


def read_json(path):
    meta = []
    for line in open(path, "r"):
        meta.append(json.loads(line))

    return meta


def update_db(collection, papers):
    collection.bulk_write(
        [
            UpdateMany({"_id": p["_id"]}, {"$setOnInsert": p}, upsert=True)
            for p in papers
        ]
    )


def parse_paper(meta, queries):
    info = {}

    cat = meta["categories"].split(" ")

    # if any(q in cat for q in queries):
    if is_subset(cat, queries):
        id = meta["id"]
        title = re.sub(r"\n", " ", meta["title"])
        title = re.sub(r"[\r\t]", "", title).strip()
        author = re.split(r"\s*,\s*|\s+and\s+", meta["authors"])
        author = list(map(lambda x: re.sub(r"\\", "", x), author))
        abstract = re.sub(r"[\r\t\n]", "", meta["abstract"]).strip()
        date = meta["update_date"]

        year = date[:4]

        if int(year) < 2015:
            return False

        info["_id"] = id
        info["title"] = title
        info["author"] = author
        info["category"] = cat
        info["abstract"] = abstract
        info["date"] = date

        return info

    else:
        return False


def main(db_uri, db_name, collection_name, json_path):
    client = get_db(db_uri, db_name, collection_name)
    db = client[db_name]
    collection = db[collection_name]
    print("Start parsing json file")
    meta_datas = read_json(json_path)
    print("Finished parsing json file")

    with open("query.txt", "r") as f:
        queries = f.read().splitlines()

    item_list = []

    final_idx = len(meta_datas)

    print("Start parsing papers")
    for idx, meta in enumerate(tqdm(meta_datas)):
        paper = parse_paper(meta, queries)
        if paper:
            item_list.append(paper)

        if len(item_list) >= 100:
            update_db(collection, item_list)
            item_list = []

        elif idx == final_idx - 1:
            update_db(collection, item_list)

    print("Finished parsing papers")

    client.close()


if __name__ == "__main__":
    db_uri = "mongodb://root:cvpr0372@arxivdb:27017/"
    db_name = "arxiv"
    collection_name = "papers"
    json_path = "./data/arxiv-metadata-oai-snapshot.json"

    main(db_uri, db_name, collection_name, json_path)
