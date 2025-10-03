import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";

const SearchResultsPage = () => {
  const { term } = useParams();
  const [results, setResults] = useState([]);
  const apiUrl = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get(`${apiUrl}/anime/get-anime-by-name/${term}`);
        setResults(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        console.error(err);
        setResults([]);
      }
    };
    fetchResults();
  }, [term, apiUrl]);

  return (
    <div className="container mx-auto px-4 py-10">
      <h2 className="text-4xl font-extrabold mb-10 text-center text-white drop-shadow-md">
        🔎 Результаты поиска:{" "}
        <span className="text-blue-400">{term}</span>
      </h2>

      {results.length > 0 ? (
        <div className="grid md:grid-cols-2 gap-8">
          {results.map((anime) => (
            <div
              key={anime.shikimori_id}
              className="group flex gap-6 rounded-2xl p-4
                bg-white/5 backdrop-blur-lg shadow-lg
                hover:shadow-blue-500/30 transition cursor-pointer"
              onClick={() => navigate(`/anime/${anime.shikimori_id}`)}
            >
              {/* Постер */}
              <div className="relative flex-shrink-0">
                <img
                  src={anime.poster?.mainUrl || anime.poster?.originalUrl || "/placeholder.jpg"}
                  alt={anime.russian || anime.name}
                  className="w-40 h-56 object-cover rounded-xl 
                    transition-transform duration-300 
                    group-hover:scale-105 group-hover:shadow-lg"
                />
              </div>

              {/* Контент */}
              <div className="flex flex-col justify-between flex-1">
                <div>
                  <h3 className="text-2xl font-semibold text-white mb-1">
                    {anime.russian || anime.name}
                  </h3>
                  <p className="text-gray-400 text-sm italic mb-3">
                    {anime.name}
                  </p>

                  {/* Жанры */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {anime.info?.genres?.map((genre) => (
                      <span
                        key={genre.id}
                        className="px-2 py-1 text-xs 
                          bg-blue-600/30 text-blue-300 
                          rounded-md"
                      >
                        {genre.name}
                      </span>
                    ))}
                  </div>

                  {/* Описание */}
                  {anime.info?.description ? (
                    <p
                      className="text-gray-300 text-sm line-clamp-3"
                      dangerouslySetInnerHTML={{
                        __html: anime.info.description_html,
                      }}
                    />
                  ) : (
                    <p className="text-gray-300 text-sm line-clamp-3">
                      Описание отсутствует
                    </p>
                  )}
                </div>

                {/* Метаданные */}
                <div className="flex gap-4 text-sm text-gray-400 mt-4">
                  <span>⭐ {anime.score !== "0.0" ? anime.score : "N/A"}</span>
                  <span>📺 {anime.episodes || "?"} эп.</span>
                  <span>📅 {anime.aired_on?.date || "—"}</span>
                  <span className="capitalize">📌 {anime.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-400 text-center mt-20 text-lg">
          ❌ Ничего не найдено по запросу:{" "}
          <span className="text-red-400">{term}</span>
        </p>
      )}
    </div>
  );
};

export default SearchResultsPage;
