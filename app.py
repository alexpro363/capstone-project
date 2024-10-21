from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary database functions
from database import (
    manage_query,
    fetch_and_store_products,
    fetch_and_store_reviews,
    best_products,
    fetch_recent_searches
)

app = Flask(__name__)
CORS(app) 

# This handles the product search, fetches products and reviews, and returns the best products.
@app.route('/search', methods=['POST'])
def search_product():
    try:
        # Parse the incoming JSON data from the request
        data = request.get_json()

        # Log the received JSON data
        print("Received JSON data:", data)

        # Extract the user search query from the JSON data
        user_search = data['query']

        # Manage the query and retrieve its query ID
        query_id = manage_query(user_search)

        # Fetch and store products and reviews associated with the search query
        fetch_and_store_products(user_search, query_id)
        fetch_and_store_reviews(query_id)

        # Retrieve the best products based on price and sentiment score
        best = best_products(query_id)

        # Fetch updated recent searches (limit to 5 recent searches)
        recent_search_results = fetch_recent_searches(limit=5)

        # Prepare the successful JSON response with the best products and recent searches
        response_data = {
            "success": True, 
            "best_products": best,
            "recent_searches": recent_search_results  # Include recent searches in the response
        }

        # Log the JSON response data
        print("Sending JSON response:", response_data)

        # Return the response as JSON with a 200 (OK) status code
        return jsonify(response_data), 200

    except Exception as e:
        # Prepare an error response if something goes wrong
        error_response = {"success": False, "error": str(e)}

        # Log the error response for debugging
        print("Sending error response:", error_response)

        # Return the error response as JSON with a 500 (Internal Server Error) status code
        return jsonify(error_response), 500

# This handles fetching and returning the recent searches along with their best products.
@app.route('/recent_searches', methods=['GET'])
def recent_searches():
    try:
        # Log that a request for recent searches was received
        print("Received request for recent searches.")

        # Fetch the recent search results from the database
        recent_search_results = fetch_recent_searches(limit=5)

        # Prepare the successful JSON response with the recent search results
        response_data = {'success': True, 'recent_searches': recent_search_results}

        # Log the response data
        print("Sending recent searches JSON response:", response_data)

        # Return the recent searches as JSON with a 200 (OK) status code
        return jsonify(response_data), 200

    except Exception as e:
        # Prepare an error response if something goes wrong
        error_response = {'success': False, 'error': str(e)}

        # Log the error response for debugging
        print("Sending error response:", error_response)

        # Return the error response as JSON with a 500 (Internal Server Error) status code
        return jsonify(error_response), 500


# This  is a check to confirm the API is running.
@app.route('/')
def index():

    return "Welcome to the Product Search API!"

# Runs the Flask app when this script is executed directly
if __name__ == "__main__":

    app.run(debug=True)
