import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import SignInPage from './components/SignInPage';
import DashboardLayout from './components/dashboard/DashboardLayout';
import DeepfakeVerifier from './components/dashboard/DeepfakeVerifier';
import NewsVerifier from './components/dashboard/NewsVerifier';
import ContentChecker from './components/dashboard/ContentChecker';
import ToolsPage from './components/dashboard/ToolsPage';
import HistoryPage from './components/dashboard/HistoryPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/signup" element={<SignInPage />} />

        {/* Dashboard Routes */}
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<Navigate to="/dashboard/deepfake" replace />} />
          <Route path="deepfake" element={<DeepfakeVerifier />} />
          <Route path="news" element={<NewsVerifier />} />
          <Route path="content" element={<ContentChecker />} />
          <Route path="tools/:toolType" element={<ToolsPage />} />
          <Route path="history" element={<HistoryPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
