import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import time
from dotenv import load_dotenv
import json  # Added for debugging purposes

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

def fetch_data(url, key, retries=3):
    while url:
        print(f"Attempting to connect to URL: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            retries -= 1
            if retries == 0:
                print("Maximum retry attempts reached. Could not fetch data.")
                return []
            print(f"Retrying... {retries} attempts left.")
            time.sleep(2)
            continue
        print("Connection established successfully.")
        data = response.json()
        yield from data.get(key, [])
        url = data.get('links', {}).get('next', {}).get('href')
        if url:
            url = f"https://{STORE_DOMAIN}{url}"

def get_collection_id_by_title(title):
    print(f"Searching for collection titled '{title}'...")
    # Fetch custom collections
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/custom_collections.json'
    for collection in fetch_data(url, 'custom_collections'):
        if collection['title'].lower() == title.lower():
            print(f"Collection '{title}' found as a custom collection.")
            return collection['id']
    
    # Fetch smart collections if not found in custom collections
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/smart_collections.json'
    for collection in fetch_data(url, 'smart_collections'):
        if collection['title'].lower() == title.lower():
            print(f"Collection '{title}' found as a smart collection.")
            return collection['id']

    print(f"Collection '{title}' not found. Please check the collection name and try again.")
    return None

def fetch_products_in_collection(collection_id):
    print(f"Fetching products for collection ID: {collection_id}...")
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/products.json?collection_id={collection_id}&limit=250'
    products = list(fetch_data(url, 'products'))
    print(f"Fetched {len(products)} products from collection ID: {collection_id}.")
    return products

def export_products_to_xml(products, collection_name):
    print(f"Starting XML export for collection '{collection_name}'...")
    root = ET.Element('STORE')
    products_elem = ET.SubElement(root, 'PRODUCTS')

    archived_count = 0
    price_zero_count = 0
    exported_count = 0
    total_products_count = 0

    for product in products:
        total_products_count += 1
        # Skip archived products
        if product.get('status') == 'archived':
            archived_count += 1
            continue
        
        for variant in product.get('variants', []):
            # Skip products with price 0.00
            if variant.get('price', '0.00') == '0.00':
                price_zero_count += 1
                continue
            
            exported_count += 1
            product_elem = ET.SubElement(products_elem, 'PRODUCT')
            
            # Existing mappings for product-level details
            mappings = {
                'PRODUCT_URL': f"https://{STORE_DOMAIN}/products/{product['handle']}",
                'PRODUCTCODE': str(product['id']),
                'PRODUCT_NAME': product['title'],
                'MODEL': variant.get('sku', 'N/A'),
                'DETAILS': product.get('body_html', ''),
                'CATALOG_NUMBER': '',
                'PRICE': variant.get('price', '0.00'),
                'SHIPMENT_COST': '00.00',  # Default shipment cost, can be modified
                'DELIVERY_TIME': '7',  # Default delivery time, can be modified
                'MANUFACTURER': product.get('vendor', 'Unknown'),
                'WARRANTY': '',
                'IMAGE': product.get('image', {}).get('src', '') if product.get('image') else '',
                'PRODUCT_TYPE': '0',  # Default product type, can be modified
            }
            
            for tag, text in mappings.items():
                ET.SubElement(product_elem, tag).text = text

    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml()
    filename = f"{collection_name.replace(' ', '_')}.xml"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"XML export completed successfully. Product data saved to '{filename}'.")
    print(f"Total number of products exported: {exported_count}")
    print(f"Total number of archived products skipped: {archived_count}")
    print(f"Total number of products with price 0.00 skipped: {price_zero_count}")
    print(f"Total number of products in the collection: {total_products_count}")
    return filename

def main():
    print("Welcome to the Shopify XML Export Script!")
    print("This script will help you export product data from your Shopify collections into XML files.")
    while True:
        collection_name = input("Enter the collection name you wish to export (or type 'done' to finish): ")
        if collection_name.lower() == 'done':
            break
        collection_id = get_collection_id_by_title(collection_name)
        if collection_id:
            products = fetch_products_in_collection(collection_id)
            if products:
                export_products_to_xml(products, collection_name)
            else:
                print(f"No products found in the collection '{collection_name}'. Please try a different collection.")
        else:
            print(f"Unable to find collection '{collection_name}'. Please ensure the collection name is correct.")

    print("Thank you for using the Shopify XML Export Script. Goodbye!")

if __name__ == '__main__':
    main()
