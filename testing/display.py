#Displays the 5 cheapest products with the best average sentiment scores.

def display_best_products(products):

    print("\nTop 5 Cheapest Products with Best Sentiment Scores:")
    for index, product in enumerate(products, start=1):
        print(f"{index}. {product['Title']} - Price: ${product['Price']} - Sentiment Score: {product['Average Sentiment']:.2f}")
