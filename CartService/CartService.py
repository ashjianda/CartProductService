from flask import Flask, jsonify, request
import requests 

app = Flask(__name__)

carts = {}

# Endpoint 1: Get all user products
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    return jsonify({"cart": carts.get(user_id, [])})

# Endpoint 2: Add specified quantity of product to cart
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):  
    quantity = request.json.get('quantity')  
    cart = carts.get(user_id, [])
    
    product_response = requests.get(f'http://localhost:5000/products/{product_id}')

    if product_response.status_code == 404:
        return jsonify({"error": "Product not found"}), 404

    product = product_response.json()

    amount_in_stock = product['product']['quantity']

    if amount_in_stock < quantity:
        return jsonify({"error": "Not enough quantity in stock"}), 400
    
    new_quantity = amount_in_stock - quantity
    new_product = {
        "id": product['product']['id'],
        "name": product['product']['name'],
        "price": product['product']['price'],
        "quantity": new_quantity
    }

    requests.post(f'http://localhost:5000/products', json=new_product)

    existing_product = next((item for item in cart if item["id"] == product_id), None)
    
    if existing_product:
        existing_product["quantity"] += quantity
    else:
        cart.append({
            "id": product_id,
            "name": product['product']['name'],
            "price": product['product']['price'],
            "quantity": quantity
        })

    carts[user_id] = cart

    return jsonify({"message": "Product added to cart", "cart": cart}), 201

# Endpoint 3: Remove specified quantity of product from cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    quantity = request.json.get('quantity')  
    
    if user_id not in carts:
        return jsonify({"error": "Cart not found"}), 404
    
    cart = carts[user_id]

    product_from_cart = next((item for item in cart if item["id"] == product_id), None)

    if not product_from_cart:
        return jsonify({"error": "Product not in cart"}), 404

    amount_removed = 0

    if product_from_cart["quantity"] > quantity:
        product_from_cart["quantity"] -= quantity
        amount_removed = quantity
    else:
        amount_removed = product_from_cart["quantity"]
        cart.remove(product_from_cart)

    carts[user_id] = cart

    product_response = requests.get(f'http://localhost:5000/products/{product_id}')
    product = product_response.json()
    amount_in_stock = product['product']['quantity']

    new_quantity = amount_in_stock + amount_removed
    new_product = {
        "id": product['product']['id'],
        "name": product['product']['name'],
        "price": product['product']['price'],
        "quantity": new_quantity
    }

    requests.post(f'http://localhost:5000/products', json=new_product)

    return jsonify({"message": "Product removed from cart", "cart": cart}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
