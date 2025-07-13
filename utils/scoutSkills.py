from pathlib import Path
from bs4 import BeautifulSoup
import bs4.element
import httpx
import json
import os
from dotenv import load_dotenv

from utils.queries.queries import CHECK_URL, INSERT_HTML, FETCH_INSTRUCTIONS, FETCH_HTML_CONTENT
import psycopg2 as pg

load_dotenv()

class ScoutMetadataKeeper:
    def __init__(self):

        self.main_index_html = Path('../аdditional/main_index.html')
        self.shops_name_json = Path('../аdditional/shops_name.json')
        self.categories_name_json = Path('аdditional/categories_name.json')
        self.shop_path = Path('../аdditional/shop/')

        self.main_page_link = 'https://zakaz.ua/uk/'
        self.user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        self.shops_name_item = {'tag': 'a', 'tag_class': 'RetailInfoCard RetailInfoCard_large css-phm2lx'}
        self.category_items_var = {'tag': 'li', 'tag_class': 'jsx-b32d37443fcf1322 CategoriesMenuListItem'}

    db_credentials = {'host': os.getenv('HOST'),
                      'port': os.getenv('PORT'),
                      'database': os.getenv('DATABASE'),
                      'user': os.getenv('USER'),
                      'password': os.getenv('PASSWORD')}

class ScoutCooks(ScoutMetadataKeeper):
    def __init__(self):
        super().__init__()

    def get_soup(self, link: str = '', html: str ='') -> BeautifulSoup:
        if html:
            return BeautifulSoup(html, 'html.parser')

        headers = self.user_agent
        start_link = httpx.get(link, headers=headers, timeout=10)
        return BeautifulSoup(start_link.text, 'html.parser')


class ScoutWrites(ScoutMetadataKeeper):
    @staticmethod
    def write_to_file(path, file):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(file)

    @classmethod
    def write_to_db(cls):
        pass


class ScoutReads(ScoutMetadataKeeper):
    def __init__(self):
        super().__init__()

    @staticmethod
    def read_from_file(path, format_json=False):
        with open(path, "r", encoding="utf-8") as f:
            if format_json:
                return json.load(f)
            return f.read()


class ScoutDatabaseAdministrator(ScoutMetadataKeeper):
    def __init__(self, link=None, content = None):
        super().__init__()
        self.full_link = link
        self.content = content


    def insert_raw_html(self):
        with pg.connect(**self.db_credentials) as conn, conn.cursor() as cur:
            cur.execute(CHECK_URL, [self.full_link])
            if cur.fetchall():
                print(cur.fetchall())

            cur.execute(INSERT_HTML, [self.content, self.full_link])

    def fetch_instructions(self):
        print('a')
        with pg.connect(**self.db_credentials) as conn, conn.cursor() as cur:
            cur.execute(FETCH_INSTRUCTIONS)
            # a = cur.fetchall()
            # print(a)
            # if cur.fetchall():
            a = cur.fetchall()
            return a
            # self.create_category(cur)

    def fetch_html_content(self):
        with pg.connect(**self.db_credentials) as conn, conn.cursor() as cur:
            cur.execute(FETCH_HTML_CONTENT)
            a = cur.fetchall()
            return a





