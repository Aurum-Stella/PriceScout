# async_parser.py
import psycopg2 as pg
import os
import asyncio
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup
import asyncpg
from utils.queries.queries import INSERT_HTML, FETCH_INSTRUCTIONS, INSERT_INSTRUCTION, FETCH_HTML
from psycopg2.extras import Json
import json
load_dotenv()
# data-marker="Impressionable"

db_credentials = {'host': os.getenv('HOST'),
                  'port': os.getenv('PORT'),
                  'database': os.getenv('DATABASE'),
                  'user': os.getenv('USER'),
                  'password': os.getenv('PASSWORD')}

def fetch_db(query):
    with pg.connect(**db_credentials) as con, con.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def main():
    db_result = fetch_db(FETCH_HTML)
    for i in db_result:
        date, html, shop_name, category_name, page = i
        shop_items_soup = BeautifulSoup(html, 'html.parser').find(attrs={"data-marker": "Impressionable"})

        print(shop_items_soup)


main()
