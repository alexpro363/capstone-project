from transformers import pipeline
from database import (
    get_reviews_by_product_id,
    update_product_sentiment_score,
    fetch_products_with_reviews
)

# Load model
sentiment_analysis = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(review_text):
    # Analyze sentiment of the given review text and return score.
    try:
        # Analyze sentiment using the pretrained model
        result = sentiment_analysis(review_text)
        label = result[0]['label']  # 'POSITIVE' or 'NEGATIVE'
        score = result[0]['score']  # Confidence score between 0 and 1

        # Convert sentiment score to a normalized value for averaging
        if label == "POSITIVE":
            normalized_score = score  # Keep positive scores as is
        else:
            normalized_score = -score  # Make negative scores negative

        return normalized_score
    except Exception as e:
        print(f"Error processing sentiment: {e}")
        return 0  # Default to 0 if there's an error

def compute_average_sentiment(reviews):
    #Compute average sentiment score from a list of reviews.
    average_sentiment = 0
    total_score = 0
    for review in reviews:
        sentiment_score = analyze_sentiment(review['Review Text'])
        total_score += sentiment_score
    
    # Calculate the average sentiment score
    if len(reviews) > 0:
        average_sentiment = total_score / len(reviews)
    else:
        average_sentiment = 0  # Handle the case when there are no reviews
    
    return average_sentiment

def update_product_sentiment_scores():
    """
    Fetch products with reviews and compute the average sentiment score for each product.
    Update the product's sentiment score in the 'products' table.
    """
    # Step 1: Fetch products that have reviews
    products_with_reviews = fetch_products_with_reviews()

    # Step 2: Loop through each product and compute average sentiment score
    for product in products_with_reviews:
        product_id = product[0]  # 'id' from products table
        asin = product[1]        # 'asin' from products table
        title = product[2]       # 'title' from products table
        
        # Step 3: Fetch reviews for this product using your function
        reviews = get_reviews_by_product_id(product_id)
        
        # Step 4: Convert the reviews to the format expected by compute_average_sentiment
        review_texts = [{'Review Text': review[1]} for review in reviews]  # Assuming index 1 is the review_text
        
        # Step 5: Compute average sentiment score using the reviews
        avg_sentiment_score = compute_average_sentiment(review_texts)
        
        # Step 6: Update the sentiment score in the 'products' table
        update_product_sentiment_score(product_id, avg_sentiment_score)
        
        print(f"Updated product {title} (ASIN: {asin}) with an average sentiment score of {avg_sentiment_score}.")
