from flask import Flask, request, jsonify
import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
STORE_DOMAIN = os.getenv('STORE_DOMAIN')

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

app = Flask(__name__)

def fetch_data(url, key, retries=3):
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            retries -= 1
            if retries == 0:
                return []
            time.sleep(2)
            continue
        data = response.json()
        yield from data.get(key, [])
        url = data.get('links', {}).get('next')

def get_collection_id_by_title(title):
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/custom_collections.json'
    for collection in fetch_data(url, 'custom_collections'):
        if collection['title'].lower() == title.lower():
            return collection['id']
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/smart_collections.json'
    for collection in fetch_data(url, 'smart_collections'):
        if collection['title'].lower() == title.lower():
            return collection['id']
    return None

def fetch_products_in_collection(collection_id):
    url = f'https://{STORE_DOMAIN}/admin/api/2023-10/products.json?collection_id={collection_id}'
    return list(fetch_data(url, 'products'))

@app.route('/get_products', methods=['GET'])
def get_products():
    collection_name = request.args.get('collection_name')
    collection_id = get_collection_id_by_title(collection_name)
    if collection_id:
        products = fetch_products_in_collection(collection_id)
        if products:
            return jsonify(products)
        return jsonify({"error": f"No products found in collection '{collection_name}'"}), 404
    return jsonify({"error": f"Collection '{collection_name}' not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)