import React from 'react';

function ProductList({ products }) {
  return (
    <div className="product-list">
      {products.map((product, index) => (
        <div key={index} className="product-card">
          <img src={product.image_url} alt={product.title} className="product-image" />
          <div className="product-info">
            <h2>{product.title}</h2>
            <p>Price: ${product.price}</p>
            <p>Sentiment Score:{product.sentiment_score} / 100</p> {/* Displaying sentiment score */}
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