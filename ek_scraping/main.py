#Import libraries

import requests
from bs4 import BeautifulSoup
import lxml
from lxml import html

import json
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.'
                  '0.0 Safari/537.36'
}

products_dict = {

}
def editing_url(url):
    if not "?katalog_=" in url:
        url_arg = url.split("/")
        url = f"https://e-catalog.co.uk/ek-list.php?katalog_={url_arg[-2]}"
    else:
        print("URL not edited")
    return url

#writing info about product
def writing_info_json(file_name):
    with open(f"data/{file_name}.json", "w", encoding="utf-8") as file:
        json.dump(products_dict, file, indent=4, ensure_ascii=False)

#Get all pages of categoryfunc
def get_all_pages(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    pages = soup.select("div.page-num a")
    pages = [page.text.strip() for page in pages if page.text.strip().isdigit()]
    print(f"[DEBUG] {pages}")
    #Checking for pages,
    if pages:
        pages = max(map(int, pages))
    else:
        pages = 0

    return pages


#Func for get all info about product
def get_info(url):
    #Connecting to the Ek
    total_pages= get_all_pages(url)
    print(total_pages)
    empty_pages = 0
    for page in range(0, total_pages + 1):
        counter = total_pages - page
        req = requests.get(f"{url}&page_={page}&", headers=headers)
        if req.status_code >= 200 or req.status_code <= 299:
            print(f"[!] Starting of scraping page: {page}")
            src = req.text
            soup = BeautifulSoup(src, 'lxml')
            products = soup.select("div[id^='mr_']")
            if products:
                #Searching info in all products at the page
                for product in products:
                    specifications_dict = {

                    }
                    name = product.select_one("a.model-short-title") or product.select_one("div.model-short-title")
                    name = str.strip(name.text).replace("\xa0", "") if name else "Name not available"
                    name = str.strip(name).replace("\"", "")
                    price_min = product.select_one(".model-price-range span[id]").text.strip() if product.select_one(
                        ".model-price-range span[id]") else "Price not available" #minimal price on the product
                    price_max = product.select_one(".model-price-range span:not([id])").text.strip() if product.select_one(
                        ".model-price-range span:not([id])") else "Price not available" #maximal price on the product
                    href = product.find("a", class_="model-short-title")
                    href = "e-catalog.co.uk" + href.get("href") if href else "Link not available"
                    #Short specifications of the product
                    short_specifications = product.find_all("div", class_='m-s-f2')
                    short_specifications = short_specifications if short_specifications else "Specifications not available"
                    for spec_block in short_specifications:
                        divs = spec_block.find_all("div")  # Getting all <div> inside m-s-f2
                        for div in divs:
                            title = div.get("title")  # Getting attr title

                            if title and ": " in title:
                                key, value = title.split(": ", 1)
                                specifications_dict[key] = value  # Add spec in dict
                                specifications_dict[key] = specifications_dict[key].replace("\xa0", " ")

                    #Printing all scraped info
                    products_dict[name] = {
                        "Min price": price_min,
                        "Max price": price_max,
                        "Link": href,
                        "Short specifications": specifications_dict
                    }
                    print(f"[+] Saved new product: {name}")
                counter -= 1
                print(f"[!] Pages to go: {counter}")
            else:
                print(f"[!] Page {page} empty")
                empty_pages += 1
                print(empty_pages)
                if empty_pages == 10:
                    print("[!] Function execution closed due to too many empty pages")
                    return
#main func
def main():
    all_info_for_a_scraper = ()
    while len(all_info_for_a_scraper) != 2:
        all_info_for_a_scraper = input("Enter link on category, and the name of the file to which you want to write scraped"
                                       " info (separated by a comma): ").strip()
        all_info_for_a_scraper = all_info_for_a_scraper.split(",")
    url = all_info_for_a_scraper[0]
    file_name = all_info_for_a_scraper[1]
    url = editing_url(url)
    get_info(url)
    writing_info_json(file_name)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("[!] The programm was stopped")