from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "Flask app is running!"

print("🚀 Flask App is starting...")

SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")

headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

@app.route("/products", methods=["GET"])
def get_products():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products.json?limit=250"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
