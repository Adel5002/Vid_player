import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Star, Tv, Calendar } from "lucide-react";

const AnimeCard = ({ anime }) => {
  const title = anime.russian || anime.name;
  const poster =
    anime.poster?.mainUrl ||
    anime.poster?.originalUrl ||
    anime.poster?.original ||
    "/placeholder.jpg";

  const statusColor =
    anime.status === "ongoing"
      ? "text-rose-400"
      : anime.status === "released"
      ? "text-emerald-400"
      : "text-gray-400";

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="relative group rounded-xl overflow-hidden shadow-lg bg-gray-900 border border-white/10"
    >
      <Link to={`/anime/${anime.shikimori_id}`} className="block relative">
        {/* 🎬 Постер */}
        <img
          src={poster}
          alt={title}
          className="w-full h-[260px] sm:h-[340px] object-cover transition-transform duration-300 group-hover:scale-105"
        />

        {/* 💻 Оверлей — появляется только при наведении */}
        <div className="hidden sm:block absolute inset-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* 📱 Мобильная панель */}
        <div className="absolute bottom-0 left-0 w-full p-4 sm:hidden flex flex-col gap-2 backdrop-blur-md bg-black/40 rounded-t-2xl border-t border-white/10">
          <h3 className="text-white text-lg font-bold leading-tight drop-shadow-lg">
            {title}
          </h3>

          <div className="flex justify-between items-center text-xs text-gray-300 font-medium">
            <div className="flex items-center gap-1">
              <Star size={14} className="text-yellow-400" />
              <span>{anime.score || "N/A"}</span>
            </div>
            <div className="flex items-center gap-1">
              <Tv size={14} className="text-blue-400" />
              <span>{anime.episodes || "?"} эп.</span>
            </div>
            <div className="flex items-center gap-1">
              <Calendar size={14} className="text-purple-400" />
              <span>{anime.aired_on?.date || "—"}</span>
            </div>
          </div>

          <p className={`text-xs font-semibold ${statusColor} tracking-wider`}>
            {anime.status?.toUpperCase()}
          </p>
        </div>

        {/* 💻 Десктопная информация */}
        <div className="hidden sm:flex absolute bottom-0 left-0 w-full bg-gradient-to-t from-black/85 to-black/30 p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex-col gap-2">
          <h3 className="text-white text-lg font-semibold truncate">
            {title}
          </h3>
          <p className="text-yellow-400 text-sm mb-1">
            ⭐ {anime.score || "N/A"}
          </p>

          <p
            className={`mt-2 text-xs font-semibold ${statusColor}`}
          >
            {anime.status?.toUpperCase()}
          </p>
        </div>
      </Link>
    </motion.div>
  );
};

export default AnimeCard;
