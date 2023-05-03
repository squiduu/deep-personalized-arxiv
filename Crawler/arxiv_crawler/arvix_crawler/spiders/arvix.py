import re
from datetime import datetime

import scrapy
from arvix_crawler.items import ArvixCrawlerItem


class ArvixSpider(scrapy.Spider):
    name = "arxiv"

    def start_requests(self):

        with open('/home/workspace/arvix/arvix_crawler/arvix_crawler/query.txt', 'r') as f:
            queries = f.read().splitlines()


        for q in queries:
            start_url = f'https://arxiv.org/list/{q}/'

            for i in range(17, 23): 
                url = start_url + str(i) + '?skip=0&show=1000'
                yield scrapy.Request(url=url, callback=self.parse_month, meta={'cat': q, 'year': str(i)})


    def parse_month(self, response):
        base_url = 'https://arxiv.org/list/'
        cat = response.meta['cat']
        year = response.meta['year']

        total = response.xpath('//*[@id="dlpage"]/small/text()').extract_first()
        total_num = re.findall(r'\d+', total)[0]

        pages = int(total_num) // 1000


        for p in range(pages+1):
            url = base_url + cat + '/' + year + f'?skip={p*1000}&show=1000'
            yield scrapy.Request(url=url, callback=self.parse_list, meta={'cat': cat})

    def parse_list(self, response):
        not_avail = ['ieee', 'acm']
        urls = response.xpath('//a[contains(@href, "abs")]/@href').extract()
        urls = [url for url in urls if not any(na in url for na in not_avail)]
        _id = [i.split('/')[-1] for i in urls]
        cat = response.meta['cat']

        for u, id in zip(urls, _id):
            url = 'https://arxiv.org' + u
            yield scrapy.Request(url=url, callback=self.parse, meta={'_id': id, 'cat': cat})


    def parse(self, response):
        item=ArvixCrawlerItem()

        _id = response.meta['_id']
        cat = response.meta['cat']
        title = response.xpath('//*[@id="abs"]/h1/text()').extract_first()
        authors = response.xpath('//*[@id="abs"]/div[2]/a/text()').extract()
        
        abstract = response.xpath('//*[@id="abs"]/blockquote/text()').extract()[1]
        abstract = re.sub(r'[\r\n\t]', '', abstract).strip()

        date_string = response.css('.submission-history ::text').extract()[-1]
        date_string = re.sub(r'[\n\r\t]|\([^)]*\)', '', date_string).strip()
        date_object = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
        date = date_object.date().isoformat()

        item['_id'] = _id
        item['titles'] = title
        item['authors'] = authors
        item['abstract'] = abstract
        item['category'] = cat
        item['date'] = date

        yield item