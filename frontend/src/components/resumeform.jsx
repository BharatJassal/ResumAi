import { useState, useRef } from 'react';

export default function ResumeForm() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [score, setScore] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are allowed.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('File size exceeds 5MB.');
      return;
    }
    setError('');
    setResumeFile(file);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!resumeFile) {
      setError('Please upload a PDF resume.');
      return;
    }
    if (!jobDesc.trim()) {
      setError('Please enter a job description.');
      return;
    }

    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDesc);

    setLoading(true);
    setError('');
    setScore(null);

    try {
      const response = await fetch('http://localhost:5000/api/match', {
        method: 'POST',
        body: formData
        // Don't set Content-Type header - let browser set it for FormData
      });

      // Check if response is ok
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else if (data.success === false) {
        setError(data.error || 'Unknown error occurred');
      } else {
        setScore(data.score);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setResumeFile(null);
    setJobDesc('');
    setScore(null);
    setError('');
    setLoading(false);
    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center text-blue-600">ResumAi</h1>

      <div className="space-y-6">
        <div>
          <label htmlFor="resumeFile" className="block text-sm font-medium text-gray-700 mb-2">
            Upload Resume (PDF):
          </label>
          <input
            ref={fileInputRef}
            id="resumeFile"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {resumeFile && (
            <p className="text-green-600 text-sm mt-2">
              Selected: {resumeFile.name}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="jobDesc" className="block text-sm font-medium text-gray-700 mb-2">
            Job Description:
          </label>
          <textarea
            id="jobDesc"
            value={jobDesc}
            onChange={e => setJobDesc(e.target.value)}
            rows={8}
            className="w-full p-3 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 resize-y"
            placeholder="Paste the job description here..."
            required
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        <div className="flex space-x-4">
          <button 
            onClick={handleSubmit}
            disabled={loading}
            className={`px-6 py-2 rounded-md font-medium ${
              loading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
            } text-white transition-colors`}
          >
            {loading ? 'Processing...' : 'Analyze'}
          </button>
          <button 
            onClick={handleReset}
            disabled={loading}
            className={`px-6 py-2 rounded-md font-medium ${
              loading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-gray-600 hover:bg-gray-700 cursor-pointer'
            } text-white transition-colors`}
          >
            Reset
          </button>
        </div>
      </div>

      {score !== null && (
        <div className="mt-8 bg-green-50 border border-green-200 rounded-md p-6 text-center">
          <h2 className="text-2xl font-bold text-green-800 mb-2">
            Match Score: {score}%
          </h2>
        </div>
      )}
    </div>
  );
}