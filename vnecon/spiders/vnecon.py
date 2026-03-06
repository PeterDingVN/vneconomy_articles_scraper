import scrapy
import re

class VNEconSpider(scrapy.Spider):
    name = 'vnecon'
    allowed_domains = ['vneconomy.vn']
    custom_settings = {
        'FEEDS': {'vnecon_articles.jsonl' : {'format': 'jsonlines'}},
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inp = input('Enter your target category: ').lower().strip()
        self.max_page = int(input('Enter max page: '))

    def category(self, input):
        dict = {
            'td': 'tieu-diem.htm',
            'dt' : 'dau-tu.htm',
            'tc': 'tai-chinh.htm',
            'kts': 'kinh-te-so.htm',
            'ktx': 'kinh-te-xanh.htm',
            'tt': 'thi-truong.htm',
            'dn': 'nhip-cau-doanh-nghiep.htm',
            'bds': 'dia-oc.htm',
            'tg': 'kinh-te-the-gioi.htm',
            'ds': 'dan-sinh.htm'
        }
        try:
            out = dict[input]
        except KeyError:
            out = list(dict.keys())
            raise KeyError(f'Valid input are: {out}')
        return out

    def start_requests(self):
        base = 'https://vneconomy.vn/'
        spec = self.category(self.inp)
        start_url = base + spec
        yield scrapy.Request(url=start_url, callback=self.parse_category)

    def parse_category(self, response):

        base_url = 'https://vneconomy.vn/'
        start_url = 'https://vneconomy.vn/' + self.category(self.inp)

        # Scrape page 2 onward
        cur_url = re.search(r'(\d+)$', str(response.url))
        if cur_url and cur_url.group(1) != 1:
            articles_endpoints = response.css(
                'div.grid-new-column_item.mt-48 > div.featured-row_item.featured-column_item > a.link-layer-imt::attr(href)'
            ).getall()

        # Base case for Page 1
        else:
            article_2 = response.css('h3.name-item a::attr(href)').getall()
            article_1 = response.css('a.link-layer-imt::attr(href)').getall()
            article_3 = response.css('h3.name a::attr(href)').getall()
            articles_endpoints = article_1 + article_2 + article_3

        for article_end in articles_endpoints:
            article = base_url + article_end
            yield scrapy.Request(url=article, callback=self.parse_article)

        # Move to next page
        next_page = response.css('li.page-item a[class=page-link]::attr(href)').get()
        # cant_prev_page = response.css('li.page-item.disabled a.page-link.prev::attr(href)').get()

        if next_page is not None:
            nxt_page_num = re.search(r'(?<==)\d+', next_page)
            if nxt_page_num and int(nxt_page_num.group())<=self.max_page:
                next_page_url = start_url + next_page
                yield response.follow(url=next_page_url, callback=self.parse_category)


    def parse_article(self, response):
        # title
        title = response.css('h1.name-detail::text').get()
        if title:
            title = title.strip()

        # date
        date = response.css('p.date::text').get()
        if date:
            date = date.strip()

        # content
        marks = tuple(['.', ',', '!', ':', ';', '?', '"', '...'])

        raw_content = response.css('p.text-justify ::text').getall()

        if raw_content:
            content = raw_content[0] + "".join(
                (" " if prev.endswith(marks) else "") + curr
                for prev, curr in zip(raw_content, raw_content[1:])
            )
        else:
            content = None

        yield {
            'Title': title,
            'Date': date,
            'Content': content
        }









