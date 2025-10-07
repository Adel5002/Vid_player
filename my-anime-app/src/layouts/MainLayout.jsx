import { Outlet, useNavigate } from "react-router-dom";
import AnimeSearchBar from "../components/AnimeSearchBar";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { motion } from "framer-motion";

const MainLayout = () => {
  const navigate = useNavigate();
  const { user, logoutUser } = useContext(AuthContext);

  const handleSearch = (term) => {
    if (term.trim()) navigate(`/search/${term}`);
  };

  return (
    <div className="min-h-screen text-white font-sans relative overflow-hidden">
      {/* 🔮 Фон с мягким свечением */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-b from-[#0a0f1f] via-[#121a2b] to-[#0a0f1f]" />
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.2),_transparent_70%)] blur-3xl" />

      {/* 🧭 HEADER */}
      <header className="sticky top-0 z-30 bg-black/30 backdrop-blur-md border-b border-white/10 shadow-[0_0_30px_-10px_rgba(59,130,246,0.4)]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between relative">
          
          {/* 🎬 ЛОГОТИП */}
          <motion.h1
            onClick={() => navigate("/")}
            whileHover={{ scale: 1.05, color: "#60a5fa" }}
            className="text-2xl font-extrabold cursor-pointer tracking-wide drop-shadow-[0_0_10px_rgba(96,165,250,0.6)]"
          >
            AnimeFinder
          </motion.h1>

          {/* 🧭 НАВИГАЦИЯ — по центру */}
          <nav className="absolute left-1/2 -translate-x-1/2 flex items-center space-x-10 text-gray-300 font-medium">
            <button
              onClick={() => navigate("/")}
              className="hover:text-blue-400 transition-all duration-300"
            >
              Главная
            </button>
            <button
              onClick={() => navigate("/trending")}
              className="hover:text-blue-400 transition-all duration-300"
            >
              Популярное
            </button>
            <button
              onClick={() => navigate("/genres")}
              className="hover:text-blue-400 transition-all duration-300"
            >
              Жанры
            </button>
          </nav>

          {/* 👤 ПРОФИЛЬ / ЛОГИН */}
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center gap-3 bg-white/10 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 shadow-lg">
                <span className="text-sm text-gray-200 font-semibold flex items-center gap-1">
                  👤 {user.sub}
                </span>
                <button
                  onClick={logoutUser}
                  className="px-3 py-1 bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white rounded-full text-xs font-semibold transition-all shadow-md hover:shadow-pink-500/30"
                >
                  Выйти
                </button>
              </div>
            ) : (
              <button
                onClick={() => navigate("/login")}
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white rounded-full text-sm font-semibold transition-all shadow-md hover:shadow-blue-400/30"
              >
                Войти
              </button>
            )}
          </div>
        </div>
      </header>

      {/* 🔍 ПОИСК */}
      <section className="py-10 bg-transparent">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-center text-2xl font-semibold mb-6 text-blue-400 drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]">
            Найди любимое аниме
          </h2>
          <AnimeSearchBar onSearch={handleSearch} />
        </div>
      </section>

      {/* 📜 КОНТЕНТ */}
      <main className="max-w-6xl mx-auto px-4 py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-black/30 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl p-6"
        >
          <Outlet />
        </motion.div>
      </main>

      {/* 🪞 FOOTER */}
      <footer className="mt-10 text-center text-gray-500 text-sm py-6 border-t border-white/10 bg-black/20">
        © {new Date().getFullYear()} AnimeFinder. Все права защищены.
      </footer>
    </div>
  );
};

export default MainLayout;
