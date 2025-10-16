import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Star, Film, MoreHorizontal, X } from "lucide-react";
import { Link } from "react-router-dom";

const AnimeList = ({ animeList = [], onRemove }) => {
  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mt-10">
      {animeList.map((anime, i) => (
        <AnimeCard
          key={anime.id || i}
          anime={anime}
          onRemove={onRemove}
          delay={i * 0.08}
        />
      ))}
    </div>
  );
};

const AnimeCard = ({ anime, onRemove, delay }) => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="group relative bg-gradient-to-br from-[#1e293b]/70 to-[#0f172a]/90 
                 rounded-2xl overflow-hidden shadow-xl border border-white/10 
                 hover:border-blue-400/40 hover:shadow-blue-500/20 transition-all duration-300"
    >
      {/* === Иконка меню === */}
      <button
        onClick={() => setMenuOpen((prev) => !prev)}
        className="absolute top-3 left-3 z-20 p-2 bg-black/50 hover:bg-black/70 
                   rounded-xl text-white/80 hover:text-white transition"
      >
        {menuOpen ? <X size={18} /> : <MoreHorizontal size={18} />}
      </button>

      {/* === Оверлей меню === */}
      {/* // Реализовать механизм отключения аниме из списка а также сделать так чтобы аниме автоматом продолжалось с того момента где остановился юзер */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/70 backdrop-blur-md z-10 flex items-center justify-center"
          >
            
            <motion.button
              onClick={() => {
                setMenuOpen(false);
                onRemove?.(anime.watchAnimeID);
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-red-600/80 hover:bg-red-700 text-white font-semibold px-6 py-3 
                         rounded-xl shadow-lg shadow-red-600/30 transition-all"
            >
              Удалить из списка
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* === Постер + Кнопка === */}
      <div className="relative overflow-hidden">
        <motion.div
          className="relative w-full h-64"
          whileHover={{ scale: 1.05 }}
          transition={{ duration: 0.3 }}
        >
          <img
            src={
              anime.poster?.mainUrl ||
              anime.poster?.originalUrl ||
              anime.poster?.original ||
              "/placeholder.jpg"
            }
            alt={anime.russian || anime.name}
            className="absolute inset-0 w-full h-full object-cover rounded-t-2xl"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent 
                          transition-all duration-300 group-hover:from-black/70" />
        </motion.div>

        <motion.button
          whileHover={{ scale: 1.1 }}
          className="absolute bottom-4 right-4 flex items-center gap-2 px-4 py-2
                     bg-blue-600/80 hover:bg-blue-600 text-white rounded-xl 
                     shadow-lg shadow-blue-600/30 backdrop-blur-md transition"
        >
          <Play size={16} />
          <Link to={`/anime/${anime.shikimori_id}`}>Смотреть</Link>
        </motion.button>
      </div>

      {/* === Контент === */}
      <div className="p-5 space-y-2">
        <h3 className="text-xl font-bold text-blue-400 group-hover:text-blue-300 transition">
          {anime.russian || anime.name}
        </h3>

        <p className="text-gray-400 text-sm flex items-center gap-1">
          <Film size={14} />
          {anime.kind ? anime.kind.toUpperCase() : "Неизвестный тип"}
        </p>

        <p className="text-gray-400 text-sm flex items-center gap-1">
          <Star size={14} className="text-yellow-400" />
          {anime.score || "?"}
        </p>

        {anime.info?.description_html ? (
          <div
            className="text-gray-300 text-sm leading-relaxed line-clamp-4 mt-2"
            dangerouslySetInnerHTML={{
              __html: anime.info.description_html,
            }}
          />
        ) : (
          <p className="text-gray-500 italic mt-2">Описание отсутствует</p>
        )}
      </div>
    </motion.div>
  );
};

export default AnimeList;
