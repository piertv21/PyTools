import sys
import requests
from bs4 import BeautifulSoup
import json

"""
    LEGAL NOTICE: This script is for educational purposes only.
    The author is not responsible for any misuse of this script.
    Using this script for any illegal activity is strictly prohibited.
    Usig this script frequently may lead to a temporary or permanent ban of your account.

    <<< Simple Subito items scraper >>>

    This script will scrape all the items from a Subito profile,
    then it will extract the title, price and likes of each item
    and save them to a JSON file.
"""

destination_file = "subito_items.json"
data = []

def find_elements_in_page(url, tag_name, class_name):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(tag_name, class_=class_name)
        return elements
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"HTML parsing error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: main.py subito_profile_url")
        sys.exit(1)

    subito_profile_url = sys.argv[1]
    
    print(r'''
   _____       __    _ __            _______ ____  _   __
  / ___/__  __/ /_  (_) /_____      / / ___// __ \/ | / /
  \__ \/ / / / __ \/ / __/ __ \__  / /\__ \/ / / /  |/ / 
 ___/ / /_/ / /_/ / / /_/ /_/ / /_/ /___/ / /_/ / /|  /  
/____/\__,_/_.___/_/\__/\____/\____//____/\____/_/ |_/   
''')
    print("[+] Starting profile scraping...")

    items_list = find_elements_in_page(subito_profile_url, "li", "Listing_ad_item__C2597")
    print(f"[+] {len(items_list)} items found")

    for item in items_list:
        title = item.find('h2', class_='index-module_sbt-text-atom__ed5J9 index-module_token-h6__FGmXw size-normal index-module_weight-semibold__MWtJJ ItemTitle-module_item-title__VuKDo SmallCard-module_item-title__1y5U3').text.strip()
        price = item.find('p', class_='index-module_price__N7M2x SmallCard-module_price__yERv7 index-module_small__4SyUf').text.split("€")[0].strip()

        href = item.find("a")["href"]
        item_likes = find_elements_in_page(href, "span", "index-module_counter-wrapper__number__7TsEd")[0].text
        
        data.append({"title": title, "price": price, "likes": item_likes, "link": href})
        print(f"[+] Item infos saved {items_list.index(item) + 1} / {len(items_list)}")

    with open(destination_file, "w") as file:
        json.dump(data, file, indent=4)
        print(f"[+] Data saved to '{destination_file}' file")