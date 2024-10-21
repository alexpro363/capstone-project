import React, { useState } from 'react';

// Func: Component that renders a search bar to input product search queries.
// Parameters: `onSearch` - a callback function passed from the app to trigger a product search.
// Returns: A search form with an input field and a search button.
function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('');  // State to store the current search query

  // Func: Handles form submission by preventing default form behavior and triggering the search with the current query.
  // Parameters: `e` - the event object.
  // Returns: N/A
  const handleSubmit = (e) => {
    e.preventDefault();  // Prevent default form submission behavior
    onSearch(query);  // Trigger the search function passed down from the parent component with the query state
  };

  return (
    <form onSubmit={handleSubmit} className="search-bar">
      {/* Input field for entering search queries */}
      <input 
        type="text"
        placeholder="Search for products..."  // Placeholder text in the input field
        value={query}  // Controlled input value linked to the query state
        onChange={(e) => setQuery(e.target.value)}  // Update query state as user types
        className="search-input"
      />

      {/* Submit button to initiate the search */}
      <button type="submit" className="search-button">Search</button>
    </form>
  );
}

export default SearchBar;
