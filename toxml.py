import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import time
from dotenv import load_dotenv

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
STORE_DOMAIN = os.getenv('STORE_DOMAIN')

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def fetch_data(url, key, retries=3):
    while url:
        for attempt in range(retries):
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                data = response.json().get(key, [])
                yield data
                last_id = data[-1]['id'] if data else None
                url = f'{url.split("?")[0]}?limit=250&since_id={last_id}' if last_id else None
                break
            else:
                print(f'Error fetching {key}: {response.status_code} - {response.text}. Retrying... ({attempt + 1}/{retries})')
                time.sleep(2 ** attempt)
        else:
            print(f'Failed to fetch {key} after {retries} attempts.')
            break

def get_all_collections():
    print("Fetching all collections.")
    all_collections = []
    for collection_type in ["custom_collections", "smart_collections"]:
        url = f'https://{STORE_DOMAIN}/admin/api/2023-10/{collection_type}.json?limit=250'
        all_collections.extend(collection for collections in fetch_data(url, collection_type) for collection in collections)
    print(f"Total collections fetched: {len(all_collections)}")
    return all_collections

def get_collection_id_by_title(collection_title):
    collection = next((c for c in get_all_collections() if c.get('title', '').lower() == collection_title.lower()), None)
    if collection:
        print(f"Collection found: ID {collection.get('id')} for title '{collection_title}'")
        return collection.get('id')
    print(f"Collection '{collection_title}' not found.")
    return None

def fetch_products_in_collection(collection_id):
    print(f"Fetching products for collection ID: {collection_id}")
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/collections/{collection_id}/products.json?limit=250'
    products = [product for products in fetch_data(url, 'products') for product in products]
    print(f"Total products fetched: {len(products)}")
    return products

def export_products_to_xml(products, collection_name):
    print(f"Exporting {len(products)} products to XML for collection: '{collection_name}'")
    root = ET.Element('STORE')
    products_elem = ET.SubElement(root, 'PRODUCTS')

    for product in products:
        product_elem = ET.SubElement(products_elem, 'PRODUCT')
        mappings = {
            'PRODUCT_URL': f"https://{STORE_DOMAIN}/products/{product.get('handle', '')}",
            'PRODUCTCODE': str(product.get('id', '')),
            'PRODUCT_NAME': product.get('title', ''),
            'MODEL': product.get('variants', [{}])[0].get('sku', ''),
            'DETAILS': product.get('body_html', ''),
            'CATALOG_NUMBER': product.get('variants', [{}])[0].get('sku', ''),
            'PRICE': product.get('variants', [{}])[0].get('price', ''),
            'SHIPMENT_COST': '15.00',
            'DELIVERY_TIME': '7',
            'MANUFACTURER': product.get('vendor', ''),
            'WARRANTY': '1',
            'IMAGE': product.get('images', [{}])[0].get('src', ''),
            'PRODUCT_TYPE': '0'
        }
        for tag, text in mappings.items():
            ET.SubElement(product_elem, tag).text = text

    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml()
    filename = f"{collection_name.replace(' ', '_')}.xml"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print(f"Product data saved to '{filename}'.")
    return filename

def create_index_html():
    print("Creating index.html with links to all XML files.")
    xml_files = [f for f in os.listdir('.') if f.endswith('.xml')]
    if not xml_files:
        print("No XML files found in the current directory.")
        return

    html_content = "<html><head><title>XML Index</title></head><body><h1>XML Files Index</h1><ul>"
    html_content += ''.join(f'<li><a href="{xml_file}">{xml_file}</a></li>' for xml_file in xml_files)
    html_content += "</ul></body></html>"

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Index file 'index.html' created successfully.")

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

    if input("Do you want to create index.html? (yes/no): ").lower() == 'yes':
        create_index_html()

    print("Shopify XML export script finished.")

if __name__ == '__main__':
    main()
