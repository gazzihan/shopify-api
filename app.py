from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Shopify 配置
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")

if not SHOPIFY_ACCESS_TOKEN or not SHOPIFY_STORE_DOMAIN:
    raise ValueError("❌ 缺少必要环境变量：SHOPIFY_ACCESS_TOKEN 或 SHOPIFY_STORE_DOMAIN")

headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

@app.route("/")
def index():
    return "✅ Shopify Flask 控制中心已部署成功！"

@app.route("/products", methods=["GET"])
def get_products():
    limit = request.args.get("limit", 50)
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products.json?limit={limit}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

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

@app.route("/delete_all_products", methods=["DELETE"])
def delete_all_products():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products.json?limit=250"
    try:
        response = requests.get(url, headers=headers)
        products = response.json().get("products", [])
        deleted_ids = []
        for product in products:
            product_id = product["id"]
            del_url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/products/{product_id}.json"
            del_resp = requests.delete(del_url, headers=headers)
            if del_resp.status_code == 200:
                deleted_ids.append(product_id)
        return jsonify({"message": f"已成功删除 {len(deleted_ids)} 个商品", "deleted_ids": deleted_ids})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route("/orders", methods=["GET"])
def get_orders():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/orders.json?limit=50&status=any"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/customers", methods=["GET"])
def get_customers():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/customers.json?limit=50"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/discounts/create", methods=["POST"])
def create_discount():
    data = request.get_json()
    price_rule_payload = {
        "price_rule": {
            "title": data.get("title", "auto-discount"),
            "target_type": "line_item",
            "target_selection": "all",
            "allocation_method": "across",
            "value_type": "percentage",
            "value": f"-{data.get('value', 10)}",
            "customer_selection": "all",
            "starts_at": data.get("starts_at", "2025-01-01T00:00:00Z")
        }
    }
    try:
        rule_resp = requests.post(
            f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/price_rules.json",
            headers=headers, json=price_rule_payload)
        rule_resp.raise_for_status()
        rule_id = rule_resp.json()["price_rule"]["id"]

        discount_payload = {
            "discount_code": {
                "code": data.get("code", "AUTODISCOUNT")
            }
        }
        discount_resp = requests.post(
            f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/price_rules/{rule_id}/discount_codes.json",
            headers=headers, json=discount_payload)
        discount_resp.raise_for_status()

        return jsonify({
            "message": "Discount created",
            "discount": discount_resp.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/inventory_levels", methods=["GET"])
def get_inventory_levels():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/inventory_levels.json?limit=50"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update_variant/<variant_id>", methods=["PUT"])
def update_variant(variant_id):
    update_data = request.get_json()
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/variants/{variant_id}.json"
    try:
        response = requests.put(url, headers=headers, json={"variant": update_data})
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

print("🚀 Shopify Flask 控制中心启动中...")
