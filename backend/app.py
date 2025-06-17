from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import io
from matcher import getMatchScore 

app = Flask(__name__)
CORS(app) 

def extractTextFromPDF(pdf_file):
    """Extract text from PDF file with better error handling."""
    try:
        text = ""
        # Reset file pointer to beginning
        pdf_file.seek(0)
        
        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) == 0:
                raise Exception("PDF file appears to be empty or corrupted")
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # Clean up the text
        text = text.strip()
        if not text:
            raise Exception("No readable text found in PDF")
            
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

@app.route('/api/match', methods=['POST', 'OPTIONS'])
def matchResume():
    """Match resume with job description and return similarity score."""
    
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        return ''
    
    try:
        # Validate file upload
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No resume file uploaded'
            })
        
        resume_file = request.files['resume']
        
        # Check if file was actually selected
        if resume_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            })
        
        # Validate file type
        if not resume_file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'Only PDF files are allowed'
            })
        
        # Get job description
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            return jsonify({
                'success': False,
                'error': 'Job description is required'
            })
        
        # Validate job description length
        if len(job_description) < 10:
            return jsonify({
                'success': False,
                'error': 'Job description is too short (minimum 10 characters)'
            })
        
        # Extract text from PDF
        try:
            resume_text = extractTextFromPDF(resume_file)
        except Exception as pdf_error:
            return jsonify({
                'success': False,
                'error': f'PDF processing failed: {str(pdf_error)}'
            })
        
        # Validate extracted text
        if len(resume_text.strip()) < 50:
            return jsonify({
                'success': False,
                'error': 'Resume text is too short. Please ensure your PDF contains readable text.'
            })
        
        # Calculate match score
        try:
            score = getMatchScore(resume_text, job_description)
        except Exception as match_error:
            return jsonify({
                'success': False,
                'error': f'Score calculation failed: {str(match_error)}'
            })
        
        # Validate score
        if score is None or not isinstance(score, (int, float)):
            return jsonify({
                'success': False,
                'error': 'Invalid score calculation result'
            })
        
        # Return successful response
        return jsonify({
            'success': True,
            'score': round(float(score), 2),
            'metadata': {
                'resume_text_length': len(resume_text),
                'job_desc_length': len(job_description),
                'filename': resume_file.filename
            }
        })
        
    except Exception as e:
        # Log the error for debugging
        print(f"Unexpected error in matchResume: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error. Please try again.'
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'ResumAi API is running'
    })

@app.route('/', methods=['GET'])
def index():
    """Basic index route."""
    return jsonify({
        'message': 'ResumAi API',
        'version': '1.0.0',
        'endpoints': {
            'match': '/api/match (POST)',
            'health': '/api/health (GET)'
        }
    })

if __name__ == '__main__':
    print("Starting ResumAi API server...")
    print("API will be available at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    app.run(debug=True, port=5000, host='0.0.0.0')