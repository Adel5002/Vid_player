import { Link } from "react-router-dom";

const AnimeCard = ({ anime }) => {
  return (
    <Link
      to={`/anime/${anime.shikimori_id}`}
      className="relative group rounded-xl overflow-hidden shadow-lg bg-gray-900 block"
    >
      {/* Постер */}
      <img
        src={
          anime.poster?.mainUrl ||
          anime.poster?.originalUrl ||
          anime.poster?.original ||
          "/placeholder.jpg"
        }
        alt={anime.russian || anime.name}
        className="
          w-full 
          h-[280px] sm:h-[340px] 
          object-cover 
          transition-transform 
          duration-300 
          group-hover:scale-105
        "
      />

      {/* Инфа */}
      <div
        className="
          absolute bottom-0 left-0 w-full 
          bg-gradient-to-t from-black/90 to-black/40 
          p-3 sm:p-4 
          opacity-100 sm:opacity-0 
          sm:group-hover:opacity-100 
          transition-opacity 
          duration-300
        "
      >
        <h3 className="text-white text-base sm:text-lg font-bold truncate">
          {anime.russian || anime.name}
        </h3>

        <p className="text-yellow-400 text-xs sm:text-sm mb-1">
          ⭐ {anime.score || "N/A"}
        </p>

        {/* Описание только на больших экранах */}
        <div
          className="hidden sm:block text-gray-300 text-xs line-clamp-4"
          dangerouslySetInnerHTML={{
            __html: anime.info?.description_html || "",
          }}
        />

        <p
          className={`mt-2 text-xs sm:text-sm font-semibold ${
            anime.status === "ongoing"
              ? "text-red-400"
              : anime.status === "released"
              ? "text-green-400"
              : "text-gray-400"
          }`}
        >
          {anime.status?.toUpperCase()}
        </p>
      </div>
    </Link>
  );
};

export default AnimeCard;
