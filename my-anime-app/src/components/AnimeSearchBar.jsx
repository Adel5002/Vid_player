import React, { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { animeByName } from "../api/request_to_api";
import { useNavigate } from "react-router-dom";

const AnimeSearchBar = () => {
  const [term, setTerm] = useState("");
  const [results, setResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (term.trim().length < 2) {
      setResults([]);
      return;
    }

    const fetchResults = async () => {
      try {
        const response = await animeByName(term)
        const data = Array.isArray(response.data) ? response.data : [];
        setResults(data);
        setShowDropdown(true);
      } catch (err) {
        console.error(err);
        setResults([]);
      }
    };

    const delay = setTimeout(fetchResults, 300);
    return () => clearTimeout(delay);
  }, [term]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (term.trim()) {
      navigate(`/search/${encodeURIComponent(term)}`);
      setShowDropdown(false);
    }
  };

  return (
    <div className="relative w-full max-w-xl mx-auto mb-6">
      {/* форма поиска */}
      <form
        onSubmit={handleSubmit}
        className="flex items-center bg-white rounded-xl shadow-lg overflow-hidden ring-1 ring-gray-300 focus-within:ring-2 focus-within:ring-blue-500 transition"
      >
        <Search className="w-5 h-5 text-gray-400 ml-3" />
        <input
          type="text"
          placeholder="Поиск аниме..."
          value={term}
          onChange={(e) => setTerm(e.target.value)}
          className="flex-1 px-3 py-2 outline-none text-gray-800"
          onFocus={() => term && setShowDropdown(true)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
        />
      </form>

      {/* дроп с результатами */}
      {showDropdown && (
        <div className="absolute z-20 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-2xl max-h-80 overflow-y-auto custom-scroll">
          {results.length > 0 ? (
            <ul className="divide-y divide-gray-100">
              {results.map((anime) => (
                <li
                  key={anime.shikimori_id}
                  className="flex items-center gap-4 px-4 py-3 hover:bg-gray-50 cursor-pointer transition group"
                  onClick={() => {
                    navigate(`/anime/${anime.shikimori_id}`);
                    setTerm("");
                    setResults([]);
                    setShowDropdown(false);
                  }}
                >
                  {/* постер */}
                  <div className="w-12 h-16 flex-shrink-0 overflow-hidden rounded-lg shadow-md group-hover:scale-105 transition-transform">
                    <img
                      src={anime.poster?.mainUrl || anime.poster?.originalUrl || "/placeholder.jpg"}
                      alt={anime.russian || anime.name}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  {/* текстовая часть */}
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">
                      {anime.russian || anime.name}
                    </p>
                    <p className="text-xs text-gray-500 italic">
                      {anime.info?.english || anime.name}
                    </p>

                    {/* жанры */}
                    <div className="flex flex-wrap gap-1 mt-1">
                      {anime.info?.genres?.slice(0, 3).map((g) => (
                        <span
                          key={g.id}
                          className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-600"
                        >
                          {g.name}
                        </span>
                      ))}
                    </div>

                    {/* статус + год */}
                    <p className="text-[11px] text-gray-400 mt-1">
                      {anime.status} • {anime.aired_on?.year || "—"}
                    </p>
                  </div>

                  {/* рейтинг */}
                  <div className="ml-auto">
                    <span className="px-2 py-1 text-xs rounded bg-yellow-100 text-yellow-700 font-medium">
                      ⭐ {anime.score !== "0.0" ? anime.score : "?"}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-4 text-gray-500 text-sm">Ничего не найдено</div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnimeSearchBar;
