import argparse
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateMany

crawl_date = datetime.now().date().isoformat()
db_uri = f"mongodb://arvixdb:27017/"
client = MongoClient(db_uri)
db = client['arxiv']
collection = db['papers']


def parse_args():
    parser = argparse.ArgumentParser(description="Arxiv Crawler")
    parser.add_argument('--update', type=str,
                        help='rather it is update or not Y or N', default='N')

    args = parser.parse_args()

    return args


def get_categories():
    with open('query.txt', 'r') as f:
        categories = f.read().splitlines()

    return categories


def parse_paper_by_category(categories, update):
    base_url = 'http://export.arxiv.org/api/query?'

    for category in categories:
        params = {
            'search_query': f'cat:{category}',
            'max_results': 1000,
            'start': 0,
            'sortBy': 'lastUpdatedDate',
            'sortOrder': 'descending'
        }

        parse_paper_list(base_url, params, update)

        print("="*20, "Finished parsing category: ", category, '='*20)


def parse_paper_list(url, params, update):

    cursor = params['start']
    category = params['search_query'].split(':')[1]

    page = 1
    retry = 0
    while True:
        params['start'] = cursor
        res = requests.get(url, params=params, timeout=None)

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml-xml')
            entries = soup.find_all('entry')

            quit_parsing = False

            if not len(entries):
                if retry < 10:
                    retry += 1
                    print("Retry", retry)
                    time.sleep(3)
                    continue
                break

            paper_infos = []

            for document in entries:
                date_format = "%Y-%m-%dT%H:%M:%SZ"
                document_date = document.find('updated').text
                document_date = datetime.strptime(document_date, date_format)

                if document_date.year < 2017:
                    quit_parsing = True
                    break

                # recent_id = document.find('id').text.split('/')[-1],

                # if collection.find_one({'_id': recent_id}):
                #     break

                info = dict(
                    _id=document.find('id').text.split('/')[-1],
                    title=document.find('title').text,
                    authors=[
                        author.text for author in document.find_all('name')],
                    category=category,
                    date=document_date.isoformat(),
                    abstract=document.find('summary').text,
                    crawl_date=crawl_date
                )

                paper_infos.append(info)

            if len(paper_infos):
                update_db(paper_infos)

            if quit_parsing:
                break

            print("="*10, f"Finished parsing page {page}", category, '='*10)

            cursor += params['max_results']
            page += 1

            time.sleep(3)
            retry = 0

def update_db(papers):
    collection.bulk_write([
        UpdateMany(
            {'_id': p['_id']},
            {'$setOnInsert': p},
            upsert=True
        )
        for p in papers
    ])

def main():
    print("="*20, "Start crawler", '='*20)
    args = parse_args()
    categories = get_categories()
    update = args.update
    parse_paper_by_category(categories, update)
    print("="*20, "End crawler", '='*20)


if __name__ == '__main__':
    main()
