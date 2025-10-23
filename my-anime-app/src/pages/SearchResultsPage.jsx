import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { animeByName } from "../api/request_to_api"; // ✅ используем централизованный API

const SearchResultsPage = () => {
  const { term } = useParams();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!term) return;
    setLoading(true);

    const timer = setTimeout(async () => {
      try {
        const { data } = await animeByName(term); // ✅ заменили api.get на централизованный вызов
        setResults(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Ошибка при поиске:", err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [term]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {loading && (
        <div className="text-center text-white text-lg">Загрузка...</div>
      )}

      {!loading && results.length === 0 && term && (
        <div className="text-center text-gray-400 text-lg">
          По запросу "{term}" ничего не найдено
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {results.map((anime) => (
          <div
            key={anime.shikimori_id}
            onClick={() => navigate(`/anime/${anime.shikimori_id}`)}
            className="group flex flex-col rounded-2xl p-6 bg-white/5 backdrop-blur-lg shadow-lg hover:shadow-blue-500/30 transition-all duration-300 cursor-pointer border border-white/10 hover:border-blue-500/30"
          >
            {/* Изображение */}
            <div className="flex-shrink-0 mb-4">
              <img
                src={anime.poster?.mainUrl || "/placeholder.jpg"}
                alt={anime.russian || anime.name}
                className="w-full h-80 object-cover rounded-xl transition-transform duration-300 group-hover:scale-105"
                onError={(e) => {
                  e.target.src = "/placeholder.jpg";
                }}
              />
            </div>

            {/* Контент */}
            <div className="flex flex-col flex-grow">
              {/* Заголовки */}
              <div className="mb-3">
                <h3 className="text-xl font-bold text-white mb-2 line-clamp-2 leading-tight">
                  {anime.russian || anime.name}
                </h3>
                <p className="text-gray-400 text-sm italic line-clamp-1">
                  {anime.name}
                </p>
              </div>

              {/* Жанры */}
              <div className="flex flex-wrap gap-2 mb-4">
                {anime.info?.genres?.slice(0, 3).map((genre) => (
                  <span
                    key={genre.id}
                    className="px-3 py-1 text-xs bg-blue-600/30 text-blue-300 rounded-full border border-blue-500/20"
                  >
                    {genre.name}
                  </span>
                ))}
              </div>

              {/* Описание */}
              <div className="mb-4 flex-grow">
                <p
                  className="text-gray-300 text-sm line-clamp-3 leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html:
                      anime.info?.description_html ||
                      "Описание отсутствует",
                  }}
                />
              </div>

              {/* Статистика */}
              <div className="flex justify-between items-center pt-4 border-t border-white/10">
                <div className="flex items-center gap-1 text-sm text-yellow-400">
                  <span>⭐</span>
                  <span>{anime.score || "N/A"}</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-400">
                  <span>📺</span>
                  <span>{anime.episodes || "?"} эп.</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-400">
                  <span>📅</span>
                  <span>
                    {anime.aired_on?.date
                      ? new Date(anime.aired_on.date).getFullYear()
                      : "—"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResultsPage;
