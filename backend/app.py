from flask import Flask, request, jsonify
from flask_cors import CORS
from matcher import get_match_score

app = Flask(__name__)
CORS(app)

@app.route('/match', methods=['POST'])
def match():
    data = request.get_json()
    resume = data.get('resume')
    job_desc = data.get('job_description')

    if not resume or not job_desc:
        return jsonify({'error': 'Missing fields'}), 400

    score = get_match_score(resume, job_desc)
    return jsonify({'score': score})

if __name__ == '__main__':
    app.run(debug=False)
