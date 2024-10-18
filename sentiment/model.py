from transformers import pipeline

# Load model and initialize tokenizer
sentiment_analysis = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(review_text):
    # Analyze sentiment of the given review text and return score.
    try:
        # Truncate the review if it's too long for the model
        result = sentiment_analysis(review_text, truncation=True, max_length=512)

        label = result[0]['label']  # 'POSITIVE' or 'NEGATIVE'
        score = result[0]['score']  # Confidence score between 0 and 1

        # Convert sentiment score to a normalized value for averaging
        if label == "POSITIVE":
            normalized_score = score  # Keep positive scores as is
        else:
            normalized_score = -score  # Make negative scores negative

        score = normalized_score * 100
        return score
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

def update_product_sentiment_scores(query_id):
    """
    Fetch products with reviews linked to a specific query and compute the average sentiment score for each product.
    Update the product's sentiment score in the 'products' table.
    """
    from database import fetch_products_with_reviews, get_reviews_by_product_id, update_product_sentiment_score

    # Fetch products with reviews linked to the given query ID
    products_with_reviews = fetch_products_with_reviews(query_id)

    # Loop through each product and compute average sentiment score
    for product in products_with_reviews:
        product_id = product[0]  # 'id' from products table
        asin = product[1]        # 'asin' from products table
        title = product[2]       # 'title' from products table
        
        # Fetch reviews for this product
        reviews = get_reviews_by_product_id(product_id)
        
        if not reviews:
            # Handle the case where no reviews exist for the product
            avg_sentiment_score = 0
        else:
            # Convert the reviews to the format expected by compute_average_sentiment
            review_texts = [{'Review Text': review[1]} for review in reviews]  # Assuming index 1 is the review_text
            
            # Compute average sentiment score using the reviews
            avg_sentiment_score = compute_average_sentiment(review_texts)
        
        # Ensure avg_sentiment_score is scaled between -100 and 100
        avg_sentiment_score = avg_sentiment_score * 100 if avg_sentiment_score else 0
        
        # Update the sentiment score in the 'products' table
        update_product_sentiment_score(product_id, avg_sentiment_score)
        
        print(f"Updated product {title} (ASIN: {asin}) with an average sentiment score of {avg_sentiment_score}.")