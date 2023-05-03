import json
import re

from pymongo import MongoClient, UpdateMany
from tqdm import tqdm


def get_db(db_uri, db_name, collection_name):
    client = MongoClient(db_uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection

def read_json(path):
    meta = []
    for line in open(path, 'r'):
        meta.append(json.loads(line))

    return meta

def update_db(collection, papers):
    collection.bulk_write([
        UpdateMany(
            {'_id': p['_id']},
            {'$setOnInsert': p},
            upsert=True
        )
        for p in papers
    ])

def parse_paper(meta, queries):

    info = {}

    cat = meta['categories'].split(' ')

    if any(q in cat for q in queries):
        id = meta['id']
        title = re.sub(r'[\r\n\t]', '', meta['title']).strip()  
        author = re.split(r'\s*,\s*|\s+and\s+', meta['authors'])
        author = list(map(lambda x: re.sub(r'\\', '',x), author))
        abstract = re.sub(r'[\r\t\n]','',meta['abstract']).strip()
        date = meta['update_date']


        info['_id'] = id
        info['title'] = title
        info['author'] = author
        info['category'] = cat
        info['abstract'] = abstract
        info['date'] = date

        return info
    
    else:
        return False

def main(db_uri, db_name, collection_name, json_path):
    collection = get_db(db_uri, db_name, collection_name)
    print("Start parsing json file")
    meta_datas = read_json(json_path)
    print("Finished parsing json file")

    with open('query.txt', 'r') as f:
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

if __name__ == '__main__':
    db_uri = 'mongodb://arvixdb:27017/'
    db_name = 'arxiv'
    collection_name = 'papers'
    json_path = './data/arxiv-metadata-oai-snapshot.json'

    main(db_uri, db_name, collection_name, json_path)