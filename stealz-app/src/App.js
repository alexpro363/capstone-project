import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import SearchBar from './search_bar';
import ProductList from './product_list';

function App() {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async (query) => {
    setLoading(true);  // Start loading before the axios call
    setError(null);    // Reset any previous error messages
  
    try {
      // Make POST request to Flask backend
      const response = await axios.post('http://localhost:5000/search', { query });
      console.log(response.data);  // Add this to see the response object

  
      // Check for a successful response and update state
      if (response.data.success) {
        setProducts(response.data.best_products);  // Update the products state with best_products array
      } else {
        setError('No products found or an error occurred.');
      }
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Failed to fetch products. Please try again.');
    }
  
    setLoading(false);  // Stop loading after data is fetched or if an error occurs
  };
  

  return (
    <div className="app">
      <h1 className="app-title">Stealz</h1>
      <SearchBar onSearch={handleSearch} />
      
      {loading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading products...</p>
        </div>
      ) : (
        
        <ProductList products={products} />
        
      )}
      {error && <p className="error-message">{error}</p>}
      
    </div>
  );
}

export default App;