import { Outlet, useNavigate, Link } from "react-router-dom";
import AnimeSearchBar from "../components/AnimeSearchBar";
import { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";

const MainLayout = () => {
  const navigate = useNavigate();
  const { user, logoutUser } = useContext(AuthContext);
  const [menuOpen, setMenuOpen] = useState(false);

  const handleSearch = (term) => {
    if (term.trim()) navigate(`/search/${term}`);
  };

  // 💫 Анимация мобильного меню
  const menuVariants = {
    hidden: { opacity: 0, y: -20, transition: { duration: 0.25 } },
    visible: { opacity: 1, y: 0, transition: { duration: 0.35 } },
    exit: { opacity: 0, y: -15, transition: { duration: 0.25 } },
  };

  return (
    <div className="min-h-screen text-white font-sans relative overflow-x-hidden">
      {/* 🌌 Фон */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-b from-[#0a0f1f] via-[#121a2b] to-[#0a0f1f]" />
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.15),_transparent_70%)] blur-3xl" />

      {/* 🧭 HEADER */}
      <header className="sticky top-0 z-30 bg-black/30 backdrop-blur-md border-b border-white/10 shadow-[0_0_30px_-10px_rgba(59,130,246,0.4)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          {/* 🎬 ЛОГО */}
          <motion.h1
            onClick={() => navigate("/")}
            whileHover={{ scale: 1.05, color: "#60a5fa" }}
            className="text-xl sm:text-2xl font-extrabold cursor-pointer tracking-wide"
          >
            AnimeFinder
          </motion.h1>

          {/* 📱 Бургер */}
          <motion.button
            onClick={() => setMenuOpen(!menuOpen)}
            whileTap={{ scale: 0.9 }}
            className="sm:hidden text-gray-300 hover:text-blue-400 transition"
          >
            <motion.div
              initial={false}
              animate={{ rotate: menuOpen ? 180 : 0 }}
              transition={{ duration: 0.4, type: "spring" }}
            >
              {menuOpen ? <X size={26} /> : <Menu size={26} />}
            </motion.div>
          </motion.button>

          {/* 🧭 Навигация (Desktop) */}
          <nav className="hidden sm:flex items-center space-x-10 text-gray-300 font-medium">
            <button onClick={() => navigate("/")} className="hover:text-blue-400 transition">
              Главная
            </button>
            <button onClick={() => navigate("/trending")} className="hover:text-blue-400 transition">
              Популярное
            </button>
            <button onClick={() => navigate("/genres")} className="hover:text-blue-400 transition">
              Жанры
            </button>
          </nav>

          {/* 👤 ПРОФИЛЬ / ЛОГИН */}
          <div className="hidden sm:flex items-center space-x-4">
            {user ? (
              <div className="flex items-center gap-3 bg-white/10 backdrop-blur-lg px-4 py-2.5 rounded-full border border-white/10 shadow-md">
                <Link to="/profile" className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center font-bold text-sm">
                    {user.sub[0]?.toUpperCase() || "👤"}
                  </div>
                  <span className="text-sm">{user.sub}</span>
                </Link>
                <div className="w-px h-6 bg-white/20" />
                <button
                  onClick={logoutUser}
                  className="px-3 py-1.5 bg-gradient-to-r from-red-500 to-pink-600 rounded-full text-xs font-semibold"
                >
                  Выйти
                </button>
              </div>
            ) : (
              <button
                onClick={() => navigate("/login")}
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full text-sm font-semibold"
              >
                Войти
              </button>
            )}
          </div>
        </div>

        {/* 📱 Мобильное меню с плавной анимацией */}
        <AnimatePresence>
          {menuOpen && (
            <motion.div
              key="mobile-menu"
              variants={menuVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="sm:hidden flex flex-col items-center gap-4 bg-black/70 backdrop-blur-lg border-t border-white/10 py-6 shadow-lg"
            >
              <button
                onClick={() => {
                  navigate("/");
                  setMenuOpen(false);
                }}
                className="w-full text-center py-2 hover:text-blue-400 transition"
              >
                Главная
              </button>

              <button
                onClick={() => {
                  navigate("/trending");
                  setMenuOpen(false);
                }}
                className="w-full text-center py-2 hover:text-blue-400 transition"
              >
                Популярное
              </button>

              <button
                onClick={() => {
                  navigate("/genres");
                  setMenuOpen(false);
                }}
                className="w-full text-center py-2 hover:text-blue-400 transition"
              >
                Жанры
              </button>

              {user ? (
                <>
                  <Link
                    to="/profile"
                    className="w-full text-center py-2 text-blue-400 font-semibold"
                    onClick={() => setMenuOpen(false)}
                  >
                    {user.sub}
                  </Link>
                  <button
                    onClick={() => {
                      logoutUser();
                      setMenuOpen(false);
                    }}
                    className="w-full text-center py-2 text-red-400 font-semibold"
                  >
                    Выйти
                  </button>
                </>
              ) : (
                <button
                  onClick={() => {
                    navigate("/login");
                    setMenuOpen(false);
                  }}
                  className="w-full text-center py-2 text-blue-400 font-semibold"
                >
                  Войти
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* 🔍 Поиск */}
      <section className="py-8 px-4">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-center text-xl sm:text-2xl mb-6 text-blue-400 font-semibold">
            Найди любимое аниме
          </h2>
          <AnimeSearchBar onSearch={handleSearch} />
        </div>
      </section>

      {/* 📜 Контент */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-black/30 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl p-4 sm:p-6"
        >
          <Outlet />
        </motion.div>
      </main>

      {/* 🪞 Footer */}
      <footer className="text-center text-gray-500 text-sm py-6 border-t border-white/10 bg-black/20">
        © {new Date().getFullYear()} AnimeFinder
      </footer>
    </div>
  );
};

export default MainLayout;
