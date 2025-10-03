import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AnimeListPage from './pages/AnimeListPage';
import AnimeInfoPage from "./pages/AnimeInfoPage";
import SearchResultsPage from "./pages/SearchResultsPage"; 
import MainLayout from "./layouts/MainLayout";
import './index.css';

function App() {
  return (
    <div className="min-h-screen text-white 
      bg-gradient-to-b from-[#0a0f1c] via-[#0f0f1f] to-black">
      <Router>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<AnimeListPage />} />
            <Route path="/search/:term" element={<SearchResultsPage />} />
            <Route path="/anime/:id" element={<AnimeInfoPage />} />
          </Route>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
