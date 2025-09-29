import { Link } from "react-router-dom";

const AnimeCard = ({ anime }) => {
  return (
    <Link
      to={`/anime/${anime.shikimori_id}`}   // 👉 теперь путь на фронте
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
        className="w-full h-[340px] object-cover transition-transform duration-300 group-hover:scale-105"
      />

      {/* Инфа при наведении */}
      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-black/90 to-black/50 p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <h3 className="text-white text-lg font-bold truncate">
          {anime.russian || anime.name}
        </h3>
        <p className="text-yellow-400 text-sm mb-1">⭐ {anime.score || "N/A"}</p>
        <div
          className="text-gray-300 text-xs line-clamp-4"
          dangerouslySetInnerHTML={{
            __html: anime.info?.description_html || "",
          }}
        />
        <p
          className={`mt-2 text-xs font-semibold ${
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
