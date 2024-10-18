from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (
     manage_query,
     fetch_and_store_products,
     fetch_and_store_reviews,
     best_products
)
from sentiment import update_product_sentiment_scores

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Route to search for products
@app.route('/search', methods=['POST'])
def search_product():
    try:
        # Get user input from request
        data = request.get_json()
        
        # Log the received request JSON
        print("Received JSON data:", data)

        user_search = data['query']

        # Manage query and get query ID
        query_id = manage_query(user_search)

        # Fetch and store products and reviews
        fetch_and_store_products(user_search, query_id)
        fetch_and_store_reviews(query_id)

        # Update sentiment scores for the products
        update_product_sentiment_scores(query_id)

        # Fetch the best products based on sentiment and price
        best = best_products(query_id)

        # Prepare the response data
        response_data = {"success": True, "best_products": best}

        # Log the outgoing JSON response
        print("Sending JSON response:", response_data)

        # Return the response as JSON
        return jsonify(response_data), 200

    except Exception as e:
        error_response = {"success": False, "error": str(e)}

        # Log the error response
        print("Sending error response:", error_response)

        return jsonify(error_response), 500

# Basic route to check if the API is working
@app.route('/')
def index():
    return "Welcome to the Product Search API!"

if __name__ == "__main__":
    app.run(debug=True)