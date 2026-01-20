# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from datetime import datetime
from scrapy import signals
import signal
import os


# Clean data pipe
class VneconPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Clean Content col
        raw_content = adapter.get('Content')
        if raw_content:
            raw_content = str(raw_content)
            cleaned_val = " ".join(raw_content.split())
            adapter['Content'] = cleaned_val.strip()

        # Clean Date col
        raw_date = adapter.get('Date')
        if raw_date:
            if ',' in raw_date:
                date_part, time_part = raw_date.split(',')
                dt_object = datetime.strptime(f"{date_part.strip()} {time_part.strip()}", "%d/%m/%Y %H:%M")
                adapter['Date'] = dt_object

        return item

# Handle cases where keyboardinterrupt error in place
class KI_ExcelExport:
    def __init__(self):
        self.jsonl_file = "vnecon_articles.jsonl"
        self.excel_file = "vneconomy_articles.xlsx"
        self.registered = False

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        return pipeline


    def spider_opened(self, spider):
       # Register atexit handler -> both cases of Ctrl+C and IDE stop
        if not self.registered:
            # atexit.register(self.convert_to_excel)
            signal.signal(signal.SIGTERM, self.handle_signal)  # IDE stop button
            signal.signal(signal.SIGINT, self.handle_signal)  # Ctrl+C
            self.registered = True

    def handle_signal(self, signum, frame):
        # Handle termination signals
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)









