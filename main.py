from dataclasses import replace

import httpx
from bs4 import BeautifulSoup
import time
import csv
import re
import json






# response = httpx.get("https://eko.zakaz.ua/uk/categories/dairy-and-eggs-ekomarket/?page=1")

start_link = httpx.get("https://eko.zakaz.ua/uk/")
main_link = 'https://eko.zakaz.ua'
main_page_categories_dict = {}


def get_weight_from_product_name(product_name):
    weight = re.findall(r'\b\d+(?:[.,]\d+)?\D*$', product_name)
    return weight


def convert_kg_to_g(text):
    text = text.replace(",", ".")
    pattern = r'^\s*\d+(?:[.,]\d+)?\|\s*\S.*$'
    if not bool(re.match(pattern, text)):
        return None

    weight = text.split('|')[0]
    weight_type = text.split('|')[1]

    if text.split('|')[1] == 'кг':
        weight = round(float(weight) * 1000, 2)
        weight_type = 'г'
    if text.split('|')[1] == 'л':
        weight = round(float(weight) * 1000, 2)
        weight_type = 'мл'
    return str(weight) + '|' + weight_type


def write_name_shop_and_category_to_json(data):
    formatted_json = json.dumps(data, ensure_ascii=False, indent=4)
    with open('zakaz/zakaz.json', 'w', encoding='UTF-8') as f:
        f.write(formatted_json)


def get_soup(link, file=False):
    if file:
        return BeautifulSoup(link, 'html.parser')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    start_link = httpx.get(link, headers=headers, timeout=10)
    return BeautifulSoup(start_link.text, 'html.parser')


def get_shops_name_from_main_page():
    shops_name_dict = {}
    with open("zakaz/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = get_soup(html, file=True)
    shop_items = soup.find_all("a", class_="RetailInfoCard RetailInfoCard_large css-phm2lx")

    for i in shop_items:
        shop_name = i.get('data-marker')
        shop_link = i.get('href').rsplit('?')
        shops_name_dict[shop_name] = shop_link[0]
    return shops_name_dict


def get_categories_from_shops(shops_name_dict):
    shops_categories = {}
    print(shops_name_dict)
    for shop in shops_name_dict:
        shops_categories[shop] = {}

        soup = get_soup(shops_name_dict[shop])
        categories_items = soup.find_all("li", class_="jsx-b32d37443fcf1322 CategoriesMenuListItem")

        for item in categories_items:
            categories_name = item.get('title')
            categories_link = item.find('a').get('href')
            shops_categories[shop][categories_name] = f'{shops_name_dict[shop]}{categories_link.rsplit('/uk/')[1]}'

            print(shop+ '__' + categories_name+ '__' + categories_link)
    print(shops_categories)
    return shops_categories


def main():
    shops_name_dict = get_shops_name_from_main_page()
    category_name_dict = get_categories_from_shops(shops_name_dict)

    write_name_shop_and_category_to_json(category_name_dict)


main()




def pars_main_page(link):
    soup = BeautifulSoup(link, 'html.parser')
    categories_tag = soup.find_all("li", class_="jsx-b32d37443fcf1322 CategoriesMenuListItem")

    for category in categories_tag:
        main_page_categories_dict[str(category.get('title'))] = str(category.find('a').get('href'))
        # print(f'{category.get('title')} --- {category.find('a').get('href')}')
    print(main_page_categories_dict)



def pars_one_category():
    # test_link = '/uk/custom-categories/promotions/'
    test_link = '/uk/custom-categories/promotions/'

    for i in range(1, 90):
        print(i)
        time.sleep(0.5)
        link = httpx.get(f'{main_link}{test_link}?page={i}', timeout=10)
        soup = BeautifulSoup(link, 'html.parser')
        products_title_details = soup.find_all("div", class_="jsx-b98800c5ccb0b885 ProductsBox__listItem")

        if not products_title_details:
            break

        for productTile in products_title_details:

            print(productTile)

            old_price_tag = productTile.find("span", class_="jsx-a1615c42095f26c8 Price__value_body Price__value_minor")
            discount_price_tag = productTile.find("span", class_="jsx-a1615c42095f26c8 Price__value_caption Price__value_discount")
            actual_price_tag = productTile.find("span", class_="jsx-a1615c42095f26c8 Price__value_caption")

            date_promo_tag = productTile.find("span", class_="jsx-d912e3a91a90a075 DiscountDisclaimer DiscountDisclaimer_productTile")
            product_name_tag = productTile.find("span", class_="jsx-12c0bb202e78d6b5 ProductTile__title")
            weight_tag = productTile.find("div", class_="jsx-12c0bb202e78d6b5 ProductTile__weight")
            product_link_tag = productTile.find("a", class_="ProductTileLink")


            old_price = old_price_tag.text if old_price_tag else None
            discount_price = discount_price_tag.text if discount_price_tag else None
            actual_price = actual_price_tag.text if actual_price_tag else None
            date_promo = date_promo_tag.text if date_promo_tag else None
            product_name = product_name_tag.text if product_name_tag else None

            weight = weight_tag.text if weight_tag else product_name_tag.text.strip().split()[-1]
            product_link = product_link_tag.get('href') if product_link_tag.get('href') else None

            print(weight)
            current_weight = convert_kg_to_g(split_number_unit(get_from_last_number(weight)))

            print(f'{product_name}|{old_price}|{discount_price}|{actual_price}|{date_promo}|{weight}|{current_weight}')

            with open('../product.csv', 'a', encoding='UTF-8', newline='') as file:
                spamwriter = csv.writer(file, delimiter='|',
                                        quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([product_name, old_price, discount_price, actual_price, date_promo, weight, main_link+product_link, current_weight])


        # main_page_categories_dict[str(category.get('title'))] = str(category.find('a').get('href'))
        # print(f'{category.get('title')} --- {category.find('a').get('href')}')
    print(main_page_categories_dict)




# pars_main_page(start_link)
# pars_one_category()
# jsx-12c0bb202e78d6b5 ProductTile__details



