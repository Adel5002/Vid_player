import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AnimeListPage from './pages/AnimeListPage';
import AnimeInfoPage from "./pages/AnimeInfoPage";
import SearchResultsPage from "./pages/SearchResultsPage"; 
import MainLayout from "./layouts/MainLayout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import CheckEmail from "./pages/CheckEmail";
import VerifyEmail from "./pages/VerifyEmail";
import { AuthProvider } from "./context/AuthContext";
import UserProfilePage from "./pages/UserProfilePage";
import './index.css';

function App() {
  return (
    <div className="min-h-screen text-white 
      bg-gradient-to-b from-[#0a0f1c] via-[#0f0f1f] to-black">
         <AuthProvider>
          <Router>
            <Routes>
              <Route element={<MainLayout />}>
                <Route path="/" element={<AnimeListPage />} />
                <Route path="/search/:term" element={<SearchResultsPage />} />
                <Route path="/anime/:id" element={<AnimeInfoPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/check-email" element={<CheckEmail />} />
                <Route path="/verify-email" element={<VerifyEmail />} />
                <Route path="/profile" element={<UserProfilePage />} />
              </Route>
            </Routes>
          </Router>
         </AuthProvider>
      
    </div>
  );
}

export default App;
