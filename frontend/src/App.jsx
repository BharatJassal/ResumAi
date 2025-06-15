import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ResumeForm from './components/ResumeForm';
import JobFinder from './components/JobFinder';

function App() {
  return (
    <Router>
      <nav>
        <Link to="/">Match My Resume</Link>
        <Link to="/find-jobs">Find Jobs</Link>
      </nav>
      <Routes>
        <Route path="/" element={<ResumeForm />} />
        <Route path="/find-jobs" element={<JobFinder />} />
      </Routes>
    </Router>
  );
}

export default App;
