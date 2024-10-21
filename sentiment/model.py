from transformers import pipeline

# Load model and initialize tokenizer for sentiment analysis
sentiment_analysis = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Func: Analyze sentiment of the given review text and return a normalized score.
# Parameters: review_text (str) - The text of the review to analyze.
# Returns: A normalized sentiment score. Positive for positive sentiment and negative for negative sentiment.
def analyze_sentiment(review_text):
    
    try:
        # Truncate the review if it's too long for the model to handle
        result = sentiment_analysis(review_text, truncation=True, max_length=512)

        label = result[0]['label']  # 'POSITIVE' or 'NEGATIVE' sentiment label
        score = result[0]['score']  # Confidence score between 0 and 1

        # Normalize sentiment score: positive values for 'POSITIVE', negative for 'NEGATIVE'
        if label == "POSITIVE":
            normalized_score = score  # Keep positive scores as is
        else:
            normalized_score = -score  # Convert negative scores to negative values

        return normalized_score
    except Exception as e:
        print(f"Error processing sentiment: {e}")
        return 0  # Return 0 if there's an error during sentiment processing