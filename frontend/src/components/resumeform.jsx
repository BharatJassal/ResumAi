import { useState } from 'react';
import axios from 'axios';
import * as pdfjsLib from 'pdfjs-dist';

pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export default function ResumeForm() {
  const [resumeText, setResumeText] = useState('');
  const [resumePdf, setResumePdf] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const extractPdf = async (file) => {
    const fileReader = new FileReader();
    fileReader.onload = async (e) => {
      const typedArray = new Uint8Array(e.target.result);
      const pdf = await pdfjsLib.getDocument(typedArray).promise;
      let text = '';
      for (let i = 0; i < pdf.numPages; i++) {
        const page = await pdf.getPage(i + 1);
        const content = await page.getTextContent();
        text += content.items.map(item => item.str).join(' ') + '\n';
      }
      setResumeText(text);
    };
    fileReader.readAsArrayBuffer(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMatch(null);

    if (!resumeText.trim() || !jobDesc.trim()) {
      setError('Please fill in both fields.');
      return;
    }
    if (resumeText.trim().length < 50 || jobDesc.trim().length < 50) {
      setError('Please provide more detailed resume and job description (minimum 50 characters each).');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/match', {
        resume: resumeText.trim(),
        job_description: jobDesc.trim(),
      });
      setMatch(response.data.score);
    } catch (err) {
      console.error(err);
      setError('An error occurred while processing your request.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResumeText('');
    setJobDesc('');
    setMatch(null);
    setError('');
    setLoading(false);
  };

  const getButtonText = () => (loading ? 'Processing...' : 'Check Match');

  return (
    <div>
      <h1>ResumAi</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="resumeFile">Upload Resume (PDF):</label>
          <input
            type="file"
            accept="application/pdf"
            id="resumeFile"
            onChange={(e) => {
              const file = e.target.files[0];
              if (file) extractPdf(file);
            }}
          />
        </div>

        <div>
          <label htmlFor="jobDesc">Job Description:</label>
          <textarea
            id="jobDesc"
            value={jobDesc}
            onChange={(e) => setJobDesc(e.target.value)}
            rows="10"
            cols="60"
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {getButtonText()}
        </button>
        <button
          type="button"
          onClick={handleReset}
          style={{ marginLeft: '10px' }}
        >
          Reset
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {match !== null && (
        <p>
          Match Score: <strong>{match}%</strong>
        </p>
      )}
    </div>
  );
}
