# async_parser.py
import os
import asyncio
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup
import asyncpg
from utils.queries.queries import INSERT_HTML, FETCH_INSTRUCTIONS, INSERT_INSTRUCTION
from psycopg2.extras import Json
import json
load_dotenv()


db_credentials = {'host': os.getenv('HOST'),
                  'port': os.getenv('PORT'),
                  'database': os.getenv('DATABASE'),
                  'user': os.getenv('USER'),
                  'password': os.getenv('PASSWORD')}


async def get_pool():
    return await asyncpg.create_pool(**db_credentials)


async def fetch_db(pool, query, params=None):
    async with pool.acquire() as conn:
        return await conn.fetch(query, *(params or []))


async def insert_db(pool, query, params=None):
    async with pool.acquire() as conn:
        await conn.execute(query, *(params or []))


semaphore = asyncio.Semaphore(10)

async def fetch_html(url):
    async with semaphore:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

from playwright.async_api import async_playwright

async def scrap_with_async_playwright(link):
    async with semaphore:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(link, timeout=30000)
            await page.wait_for_timeout(5000)  # Можно увеличить
            content = await page.content()
            await browser.close()
            return content


async def process_instruction(pool, instruction):
    date, id, url, child_attribute, type_, parent_id = instruction

    for n in range(1, 9999):
        await asyncio.sleep(1)
        url_page = f'{url}?page={n}'
        try:
            raw_html = await fetch_html(url_page)
        except Exception as e:
            print(f"Error fetching {url_page}: {e}")
            break

        soup = BeautifulSoup(raw_html, 'html.parser')
        category_tag = soup.find(attrs={"data-marker": "Disabled Breadcrumb"})
        category = category_tag.text if category_tag else "Unknown"

        shop_name = url_page.replace('https://', '').split('.')[0]

        items_container_tag = soup.find(attrs=json.loads(child_attribute))


        if items_container_tag is None:
            print(f"No items found at {url_page}")
            break

        items_container = items_container_tag.prettify()

        print(f"Inserting: {id}, {shop_name}, {category}, page {n}")
        await insert_db(pool, INSERT_HTML, [id, items_container, shop_name, category, n])

async def main():
    pool = await get_pool()

    scrap_instructions = await fetch_db(pool, FETCH_INSTRUCTIONS,  ['shop_categories'])

    # ⚡️ Создаём задачи по каждой инструкции
    tasks = [process_instruction(pool, instruction) for instruction in scrap_instructions]
    await asyncio.gather(*tasks)

    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())


# with open('index.html', 'r', encoding='UTF-8') as f:
#     soup = BeautifulSoup(f.read(), 'html.parser')
    # print(soup.find(attrs={"data-marker": "Products Box"}))