from flask import Flask, jsonify, request
app = Flask(__name__)

products = {}
    
# Endpoint 1: Get all products
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify({"products": list(products.values())})

# Endpoint 2: Get a specific product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = products.get(product_id)
    if product:
        return jsonify({"product": product})
    else:
        return jsonify({"error": "Product not found"}), 404

# Endpoint 3: Create a new product  
@app.route('/products', methods=['POST'])
def create_product():
    product_id = request.json.get('id', len(products) + 1)
    new_product = {
        "id": product_id,
        "name": request.json.get('name'),
        "price": request.json.get('price'), 
        "quantity": request.json.get('quantity')
    }
    products[product_id] = new_product
    return jsonify({"message": "Product created", "product": new_product}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
