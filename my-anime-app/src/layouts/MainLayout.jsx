import { Outlet, useNavigate } from "react-router-dom";
import AnimeSearchBar from "../components/AnimeSearchBar";

const MainLayout = () => {
  const navigate = useNavigate();

  const handleSearch = (term) => {
    if (term.trim()) {
      navigate(`/search/${term}`);
    }
  };

  return (
    <div className="min-h-screen text-white font-sans">
      {/* Глобальный градиентный фон */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#0f172a]" />

      {/* Хедер / Навбар */}
      <header className="sticky top-0 z-20 bg-black/30 backdrop-blur-md border-b border-white/10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1
            onClick={() => navigate("/")}
            className="text-2xl font-bold cursor-pointer hover:text-blue-400 transition"
          >
            🎬 AnimeFinder
          </h1>
          <div className="w-1/2">
            <AnimeSearchBar onSearch={handleSearch} />
          </div>
        </div>
      </header>

      {/* Основной контент */}
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
