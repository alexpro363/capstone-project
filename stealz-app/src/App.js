import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import SearchBar from './search_bar';
import ProductList from './product_list';

function App() {
  // State variables
  const [loading, setLoading] = useState(false); // Track loading status
  const [products, setProducts] = useState([]); // Store fetched products
  const [error, setError] = useState(null); // Store error messages
  const [recentSearches, setRecentSearches] = useState([]); // Store recent searches
  const [showRecentSearches, setShowRecentSearches] = useState(false); // Toggle recent searches display

  // Func: Handles product search by sending a query to the backend
  // Parameters: query - the user's search input
  const handleSearch = async (query) => {
    setLoading(true); // Start loading
    setError(null); // Reset any existing errors

    try {
      // Send POST request with search query
      const response = await axios.post('http://localhost:5000/search', { query });
      console.log(response.data);

      // Handle successful response
      if (response.data.success) {
        setProducts(response.data.best_products); // Set fetched products
      } else {
        setError('No products found or an error occurred.');
      }
    } catch (err) {
      // Handle any errors from the request
      console.error('Error fetching products:', err);
      setError('Failed to fetch products. Please try again.');
    }

    setLoading(false); // Stop loading
  };

  // Func: Fetches recent search data from the backend
  const fetchRecentSearches = async () => {
    try {
      const response = await axios.get('http://localhost:5000/recent_searches');
      if (response.data.success) {
        setRecentSearches(response.data.recent_searches); // Set recent searches
      } else {
        setError('Failed to fetch recent searches.');
      }
    } catch (err) {
      // Handle any errors from the request
      console.error('Error fetching recent searches:', err);
      setError('Failed to fetch recent searches.');
    }
  };

  // Fetch recent searches on component mount
  useEffect(() => {
    fetchRecentSearches();
  }, []);

  return (
    <div className="app">
      <h1 className="app-title">Stealz</h1>
      <h2 className="app-subtitle">Find the best products at the lowest prices</h2>
      
      {/* Search bar component */}
      <SearchBar onSearch={handleSearch} />
      
      {loading ? (
        // Display loading spinner while fetching products
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading products...</p>
        </div>
      ) : (
        // Display fetched products in a list
        <ProductList products={products} />
      )}

      {/* Display error message if any */}
      {error && <p className="error-message">{error}</p>}

      {/* Button to toggle recent searches visibility */}
      <button onClick={() => setShowRecentSearches(!showRecentSearches)}>
        {showRecentSearches ? 'Hide Recent Searches' : 'Show Recent Searches'}
      </button>

      {/* Display recent searches dropdown if toggled on */}
      {showRecentSearches && recentSearches.length > 0 && (
        <div className="recent-searches-dropdown">
          {recentSearches.map((search, index) => (
            <div key={index}>
              <h3>Search: {search.query_text}</h3>
              {/* Display the products related to each recent search */}
              <ProductList products={search.best_products} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;