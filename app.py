

# ✅ 获取订单
@app.route("/orders", methods=["GET"])
def get_orders():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/orders.json?limit=50&status=any"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# ✅ 获取客户列表
@app.route("/customers", methods=["GET"])
def get_customers():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/customers.json?limit=50"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# ✅ 创建折扣码（基于 Price Rule）
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
        # 创建 Price Rule
        rule_resp = requests.post(
            f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/price_rules.json",
            headers=headers, json=price_rule_payload)
        rule_resp.raise_for_status()
        rule_id = rule_resp.json()["price_rule"]["id"]

        # 创建 Discount Code
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

# ✅ 获取库存数量（基于 location）
@app.route("/inventory_levels", methods=["GET"])
def get_inventory_levels():
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/2024-04/inventory_levels.json?limit=50"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ 修改变体价格
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
