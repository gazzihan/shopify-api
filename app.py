from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Shopify 配置
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")

headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# 根路由 - 测试部署是否成功
@app.route("/")
def index():
    return "✅ Shopify Flask 控制中心已部署"

# 获取全部商品（分页）
@app.route("/products", methods=["GET"])
def get_paginated_products():
    page = request.args.get("page", 1)
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products.json?limit=50&page={page}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# 创建一个新商品
@app.route("/create_product", methods=["POST"])
def create_product():
    product_data = request.get_json()
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products.json"
    try:
        response = requests.post(url, headers=headers, json={"product": product_data})
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# 删除所有商品
@app.route("/delete_all_products", methods=["DELETE"])
def delete_all_products():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products.json?limit=250"
    try:
        response = requests.get(url, headers=headers)
        products = response.json().get("products", [])
        for product in products:
            product_id = product["id"]
            del_url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products/{product_id}.json"
            requests.delete(del_url, headers=headers)
        return jsonify({"message": f"已删除 {len(products)} 个商品"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 删除指定商品
@app.route("/delete_product/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products/{product_id}.json"
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            return jsonify({"message": f"已删除商品 {product_id}"})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 修改商品标题或描述
@app.route("/update_product/<product_id>", methods=["PUT"])
def update_product(product_id):
    update_data = request.get_json()
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products/{product_id}.json"
    try:
        response = requests.put(url, headers=headers, json={"product": update_data})
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

print("🚀 Shopify Flask 控制中心启动中...")
