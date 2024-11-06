import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
STORE_DOMAIN = os.getenv('STORE_DOMAIN')

if not ACCESS_TOKEN or not STORE_DOMAIN:
    raise ValueError("ACCESS_TOKEN and STORE_DOMAIN must be set in the environment.")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def get_product_by_id(product_id):
    # Fetch the product by ID from the Shopify API
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/products/{product_id}.json'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Error fetching product: {response.status_code} - {response.text}')
        return None
    product = response.json().get('product', None)
    if not product:
        print('Product not found.')
        return None
    return product

def main():
    product_id = input("Please enter the product ID: ")
    product = get_product_by_id(product_id)
    if product:
        with open('product_details.txt', 'w') as file:
            file.write(str(product))
        print("Product details saved to product_details.txt")
    else:
        print("Failed to retrieve product.")

if __name__ == '__main__':
    main()
