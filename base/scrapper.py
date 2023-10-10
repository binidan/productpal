import requests
from bs4 import BeautifulSoup
import random

def amazon_scraper(product):
    url_amazon = f"https://www.amazon.in/s?k={product}"
    product_dict = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_amazon, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            products = soup.find_all('div', {'class': 's-card-container'})

            for product in products:
                title_element = product.find('span', {'class': 'a-text-normal'})
                title = title_element.text.strip()[0:35] if title_element else None

                rate_element = product.find('span', {'class': 'a-icon-alt'})
                rate = rate_element.text.strip()[:3] if rate_element else None

                price_element = product.find('span', {'class': 'a-offscreen'})
                price = price_element.text.strip() if price_element else None

                discount_element = product.find('span', {'class': 'a-text-price'})
                discount_element = discount_element.find('span', {'class': 'a-offscreen'}) if discount_element else None
                discount = discount_element.text.strip() if discount_element else None

                link_element = product.find('a', {'class': 'a-link-normal s-no-outline'})
                link = f'https://www.amazon.in/{link_element.get("href")}' if link_element else None

                img_element = product.find('img', {'class': 's-image'})
                img = img_element.get("src") if img_element else None

                product_dict[title] = {
                    "company":"amazon",
                    "rate": rate,
                    "price": price,
                    "discount": discount,
                    "link": link,
                    "img": img
                }

        else:
            return response.status_code

    except requests.exceptions.RequestException as e:
        return e

    return product_dict

# print(product_scraper("Samsung"))
def snapdeal_scraper(product):
    url_snapdeal = f"https://www.snapdeal.com/search?keyword={product}"
    product_dict = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_snapdeal, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            products = soup.find_all('div', {'class': 'product-tuple-listing'})

            for product in products:
                title_element = product.find('p', {'class': 'product-title'})
                title = title_element.text.strip()[0:35] if title_element else None

                div_element = product.find('div', {'class': 'filled-stars'})
                if div_element:
                    style_attribute = div_element['style'] 
                    value = style_attribute.split(":")[1].strip('%')
                    float1 = (float(value)/100)*5
                    float2 = f'{float1:.1f}'
                    rate = str(float2)
                else:
                    rate = None

                price_element = product.find('span', {'class': 'product-price'})
                if price_element:
                    original_string = price_element.text.strip()
                    number_part = original_string.replace(',', '')
                    number = int(number_part.split()[-1])
                    price = f'₹{number:,}'
                else:
                    price = None

                discount_element = product.find('span', {'class': 'product-desc-price'})
                if discount_element:    
                    original_string = discount_element.text.strip() 
                    number_part = original_string.replace(',', '')
                    number = int(number_part.split()[-1])
                    discount = f'₹{number:,}'

                link_element = product.find('a', {'class': 'dp-widget-link'})
                link = link_element.get("href") if link_element else None

                img_element = product.find('source', {'class': 'product-image'})
                img = img_element.get("srcset") if img_element else None

                product_dict[title] = {
                    "company":"snapdeal",
                    "rate": rate,
                    "price": price,
                    "discount": discount,
                    "link": link,
                    "img": img
                }
                

        else:
            return response.status_code

    except requests.exceptions.RequestException as e:
        return e

    return product_dict

def product_scraper(product):
    amazon_data = amazon_scraper(product)
    snapdeal_data = snapdeal_scraper(product)

    if not amazon_data and not snapdeal_data:
        # Both dictionaries are empty, return an empty dictionary
        return {}

    if not amazon_data:
        return snapdeal_data

    if not snapdeal_data:
        return amazon_data

    # Merge the dictionaries, giving preference to Amazon data in case of conflicts
    merged_data = snapdeal_data.copy()
    merged_data.update(amazon_data)

    product_items = list(merged_data.items())
    # Shuffle the list randomly
    random.shuffle(product_items)

    # Convert the shuffled list back to a dictionary
    shuffled_product_dict = dict(product_items)

    return shuffled_product_dict
