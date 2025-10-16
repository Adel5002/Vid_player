import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";

const SearchResultsPage = () => {
  const { term } = useParams();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const apiUrl = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();

  useEffect(() => {
    if (!term) return;

    setLoading(true);

    // Дебаунс: подождать 500 мс перед запросом
    const timer = setTimeout(async () => {
      try {
        const response = await axios.get(`${apiUrl}/anime/get-anime-by-name/${term}`);
        setResults(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        console.error(err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 500); // <-- задержка 0.5 секунды

    // Очистка таймера при изменении term
    return () => clearTimeout(timer);
  }, [term, apiUrl]);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 sm:gap-8">
      {results.map((anime) => (
        <div
          key={anime.shikimori_id}
          onClick={() => navigate(`/anime/${anime.shikimori_id}`)}
          className="group flex flex-col sm:flex-row items-center sm:items-start gap-4 sm:gap-6 rounded-2xl p-4 bg-white/5 backdrop-blur-lg shadow-lg hover:shadow-blue-500/30 transition cursor-pointer"
        >
          <img
            src={anime.poster?.mainUrl || "/placeholder.jpg"}
            alt={anime.russian || anime.name}
            className="w-full sm:w-40 h-56 object-cover rounded-xl transition-transform duration-300 group-hover:scale-105"
          />

          <div className="flex flex-col justify-between text-center sm:text-left w-full">
            <h3 className="text-lg sm:text-2xl font-semibold text-white mb-1 truncate">
              {anime.russian || anime.name}
            </h3>
            <p className="text-gray-400 text-sm italic mb-3">{anime.name}</p>

            <div className="flex flex-wrap justify-center sm:justify-start gap-2 mb-3">
              {anime.info?.genres?.slice(0, 4).map((genre) => (
                <span
                  key={genre.id}
                  className="px-2 py-1 text-xs bg-blue-600/30 text-blue-300 rounded-md"
                >
                  {genre.name}
                </span>
              ))}
            </div>

            <p className="text-gray-300 text-sm line-clamp-3 hidden sm:block" dangerouslySetInnerHTML={{ __html: anime.info?.description_html || "Описание отсутствует" }} />

            <div className="flex justify-center sm:justify-start gap-3 mt-3 text-xs sm:text-sm text-gray-400">
              <span>⭐ {anime.score || "N/A"}</span>
              <span>📺 {anime.episodes || "?"} эп.</span>
              <span>📅 {anime.aired_on?.date || "—"}</span>
            </div>
          </div>
        </div>
      ))}
    </div>

  );
};

export default SearchResultsPage;
