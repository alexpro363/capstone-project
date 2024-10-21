import React from 'react';

// Func: Component that renders a list of products with their details.
// Parameters: Takes in a list of `products` to be displayed.
// Returns: Renders a list of product cards with relevant information such as image, title, price, sentiment score, and a link to view the product on Amazon.
function ProductList({ products }) {
  return (
    <div className="product-list">
      {/* Loop through the list of products and render each one as a product card */}
      {products.map((product, index) => (
        <div key={index} className="product-card">
          {/* Display the product image */}
          <img src={product.image_url} alt={product.title} className="product-image" />

          {/* Display the product details like title, price, sentiment score, and a link to Amazon */}
          <div className="product-info">
            <h2>{product.title}</h2>

            {/* Conditionally show price or fallback message if not available */}
            <p>Price: {product.price ? `$${product.price}` : "No Price Available"}</p>

            {/* Conditionally display the sentiment score if available, otherwise show a fallback message */}
            {product.sentiment_score !== null ? (
              <p>Sentiment Score: {product.sentiment_score} / 100</p>
            ) : (
              <p>Sentiment Score: Not Available</p>
            )}

            {/* link to view the product on Amazon  */} 
            <a href={product.product_url} target="_blank" rel="noopener noreferrer">
              View on Amazon
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ProductList;
