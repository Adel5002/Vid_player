import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import AnimeListPage from './pages/AnimeList'
import AnimeInfoPage from "./pages/AnimeInfoPage";
import './index.css'


function App() {
  return (
    <div className="min-h-screen bg-[#272a36] text-white">
      <Router>
        <Routes>
          {/* Главная страница со списком */}
          <Route path="/" element={<AnimeListPage />} />

          {/* Страница информации про аниме */}
          <Route path="/anime/:id" element={<AnimeInfoPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
