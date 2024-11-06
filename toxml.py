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
        print(f"Establishing connection to URL: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            retries -= 1
            if retries == 0:
                return []
            time.sleep(2)
            continue
        print("Connection established successfully.")
        data = response.json()
        yield from data.get(key, [])
        url = data.get('links', {}).get('next')

def get_collection_id_by_title(title):
    # Fetch custom collections
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/custom_collections.json'
    for collection in fetch_data(url, 'custom_collections'):
        if collection['title'].lower() == title.lower():
            return collection['id']
    
    # Fetch smart collections if not found in custom collections
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/smart_collections.json'
    for collection in fetch_data(url, 'smart_collections'):
        if collection['title'].lower() == title.lower():
            return collection['id']

    print(f"Collection '{title}' not found. Please check the collection name.")
    return None

def fetch_products_in_collection(collection_id):
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/products.json?collection_id={collection_id}'
    return list(fetch_data(url, 'products'))

def export_products_to_xml(products, collection_name):
    root = ET.Element('products')

    for product in products:
        product_elem = ET.SubElement(root, 'product')
        
        # Existing mappings for product-level details
        mappings = {
            'id': str(product['id']),
            'title': product['title'],
            'body_html': product.get('body_html', ''),
            # Add more product-level fields here if needed
        }
        
        for tag, text in mappings.items():
            ET.SubElement(product_elem, tag).text = text

        # Add variant information
        variants_elem = ET.SubElement(product_elem, 'variants')
        for variant in product.get('variants', []):
            variant_elem = ET.SubElement(variants_elem, 'variant')
            variant_mappings = {
                'id': str(variant['id']),
                'title': variant.get('title', ''),
                'price': variant.get('price', ''),
                # Add other variant-level fields here if needed
            }
            for tag, text in variant_mappings.items():
                ET.SubElement(variant_elem, tag).text = text

    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml()
    filename = f"{collection_name.replace(' ', '_')}.xml"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print(f"Product data saved to '{filename}'.")
    return filename

def main():
    print("Starting the Shopify XML export script.")
    while True:
        collection_name = input("Enter collection name (or type 'done' to finish): ")
        if collection_name.lower() == 'done':
            break
        collection_id = get_collection_id_by_title(collection_name)
        if collection_id:
            products = fetch_products_in_collection(collection_id)
            if products:
                export_products_to_xml(products, collection_name)
            else:
                print(f"No products found in collection '{collection_name}'.")
        else:
            print(f"Collection '{collection_name}' not found.")

    print("Shopify XML export script finished.")

if __name__ == '__main__':
    main()
