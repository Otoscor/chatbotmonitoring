import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import ReportDetail from './pages/ReportDetail'
import CharacterRankings from './pages/CharacterRankings'
import News from './pages/News'
import AppReviews from './pages/AppReviews'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/reports/:date" element={<ReportDetail />} />
          <Route path="/character-rankings" element={<CharacterRankings />} />
          <Route path="/news" element={<News />} />
          <Route path="/app-reviews" element={<AppReviews />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
