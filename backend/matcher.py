import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import re
import numpy as np

# Load the model once when the module is imported
try:
    embed = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder/4",
                           input_shape=[],  
                           dtype=tf.string, 
                           trainable=False)
    print("Universal Sentence Encoder loaded successfully")
except Exception as e:
    print(f"Error loading Universal Sentence Encoder: {e}")
    embed = None

def preprocessText(text: str) -> str:
    """
    Clean and normalize text for embedding.
    Removes extra whitespace, special characters, and converts to lowercase.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove excessive punctuation but keep meaningful ones
    text = re.sub(r'[^\w\s\.\,\;\:\!\?]', ' ', text)
    
    # Remove extra spaces again after punctuation removal
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def getMatchScore(resume: str, job_description: str) -> float:
    """
    Calculate similarity score between resume and job description.
    Returns a score between 0-100.
    
    Args:
        resume (str): Resume text content
        job_description (str): Job description text
        
    Returns:
        float: Similarity score from 0-100
    """
    try:
        # Check if model is loaded
        if embed is None:
            print("Error: Universal Sentence Encoder not loaded")
            return 0.0
        
        # Preprocess texts
        resumeClean = preprocessText(resume)
        jobDescClean = preprocessText(job_description)
        
        # Validate inputs
        if not resumeClean or not jobDescClean:
            print("Error: Empty text after preprocessing")
            return 0.0
        
        if len(resumeClean) < 10 or len(jobDescClean) < 10:
            print("Warning: Very short text detected")
            return 0.0
        
        # Get embeddings
        embeddings = embed([resumeClean, jobDescClean])
        
        # Extract individual embeddings
        resume_embedding = embeddings[0]
        job_embedding = embeddings[1]
        
        # Calculate cosine similarity manually for better control
        dot_product = tf.reduce_sum(resume_embedding * job_embedding)
        norm_resume = tf.norm(resume_embedding)
        norm_job = tf.norm(job_embedding)
        
        # Avoid division by zero
        cosine_similarity = dot_product / (norm_resume * norm_job + 1e-8)
        
        # Convert to numpy and get scalar value
        cos_sim = float(cosine_similarity.numpy())
        
        # Ensure cosine similarity is in valid range [-1, 1]
        cos_sim = max(-1.0, min(1.0, cos_sim))
        
        # Convert from [-1, 1] to [0, 100] scale
        score = (cos_sim + 1) * 50
        
        # Ensure score is in valid range [0, 100]
        score = max(0.0, min(100.0, score))
        
        return round(float(score), 2)
        
    except Exception as e:
        print(f"Error calculating match score: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

def getDetailedMatchScore(resume: str, job_description: str) -> dict:
    """
    Get detailed match score with additional metrics and analysis.
    
    Args:
        resume (str): Resume text content
        job_description (str): Job description text
        
    Returns:
        dict: Detailed scoring information
    """
    try:
        score = getMatchScore(resume, job_description)
        
        # Calculate additional metrics
        resume_words = len(preprocessText(resume).split())
        job_desc_words = len(preprocessText(job_description).split())
        
        # Simple keyword overlap analysis
        resume_tokens = set(preprocessText(resume).split())
        job_tokens = set(preprocessText(job_description).split())
        common_tokens = resume_tokens.intersection(job_tokens)
        keyword_overlap = len(common_tokens) / len(job_tokens) * 100 if job_tokens else 0
        
        return {
            'overall_score': score,
            'similarity_level': (
                'Excellent' if score >= 80 else
                'Good' if score >= 65 else
                'Fair' if score >= 50 else
                'Poor'
            ),
            'keyword_overlap_percentage': round(keyword_overlap, 2),
            'resume_word_count': resume_words,
            'job_description_word_count': job_desc_words,
            'common_keywords_count': len(common_tokens),
            'recommendations': _getRecommendations(score, keyword_overlap)
        }
    except Exception as e:
        print(f"Error in detailed analysis: {e}")
        return {
            'overall_score': 0.0,
            'similarity_level': 'Error',
            'error': str(e)
        }

def _getRecommendations(score: float, keyword_overlap: float) -> list:
    """Generate recommendations based on scores."""
    recommendations = []
    
    if score < 50:
        recommendations.append("Consider tailoring your resume more closely to the job requirements")
    
    if keyword_overlap < 30:
        recommendations.append("Include more relevant keywords from the job description")
    
    if score < 70:
        recommendations.append("Highlight skills and experiences that match the job posting")
    
    if not recommendations:
        recommendations.append("Great match! Your resume aligns well with the job requirements")
    
    return recommendations

# Test function to verify the model works
def test_matcher():
    """Test function to verify the matcher is working correctly."""
    try:
        test_resume = "Software engineer with Python experience"
        test_job = "Looking for a Python software developer"
        
        score = getMatchScore(test_resume, test_job)
        print(f"Test score: {score}")
        
        if score > 0:
            print("Matcher is working correctly!")
            return True
        else:
            print("Matcher test failed - score is 0")
            return False
    except Exception as e:
        print(f"Matcher test failed: {e}")
        return False

# Run test when module is imported (optional)
if __name__ == "__main__":
    test_matcher()