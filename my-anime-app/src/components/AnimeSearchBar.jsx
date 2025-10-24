import React, { useState, useEffect, useRef } from "react";
import { Search, X } from "lucide-react";
import { animeByName } from "../api/request_to_api";
import { useNavigate, useLocation } from "react-router-dom";

const DEBOUNCE_DELAY = 600;

const AnimeSearchBar = () => {
  const [term, setTerm] = useState("");
  const [results, setResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [userInteracted, setUserInteracted] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const debounceRef = useRef(null);
  const inputRef = useRef(null);
  const containerRef = useRef(null);

  // 🔹 Запрос к API
  const fetchResults = async (searchTerm) => {
    const trimmed = searchTerm.trim();
    if (trimmed.length < 2) return;
    try {
      setIsLoading(true);
      const response = await animeByName(trimmed);
      const data = Array.isArray(response.data) ? response.data : [];
      setResults(data);
      setShowDropdown(true);
    } catch (err) {
      console.error("❌ Ошибка при поиске:", err);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 🔹 Debounce
  useEffect(() => {
    const trimmed = term.trim();
    if (trimmed.length < 2 || !userInteracted) {
      setResults([]);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchResults(trimmed), DEBOUNCE_DELAY);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [term, userInteracted]);

  // 🔹 При клике вне компонента — закрываем дроп
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // 🔹 При смене маршрута — просто скрываем дроп
  useEffect(() => {
    setShowDropdown(false);
  }, [location.pathname]);

  // 🔹 Сабмит
  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = term.trim();
    if (trimmed) {
      navigate(`/search/${encodeURIComponent(trimmed)}`);
      inputRef.current?.blur();
      setShowDropdown(false);
    }
  };

  // 🔹 Очистка
  const handleClear = () => {
    setTerm("");
    setResults([]);
    setShowDropdown(false);
    setUserInteracted(false);
    inputRef.current?.blur();
  };

  // 🔹 Фокус
  const handleFocus = async () => {
    setUserInteracted(true);
    const trimmed = term.trim();
    if (trimmed.length >= 2) {
      await fetchResults(trimmed);
    }
    setShowDropdown(true);
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-xl mx-auto mb-6">
      <form
        onSubmit={handleSubmit}
        className="flex items-center bg-white rounded-xl shadow-lg overflow-hidden ring-1 ring-gray-300 focus-within:ring-2 focus-within:ring-blue-500 transition relative"
      >
        <Search className="w-5 h-5 text-gray-400 ml-3" />
        <input
          ref={inputRef}
          type="text"
          placeholder="Поиск аниме..."
          value={term}
          onChange={(e) => {
            setTerm(e.target.value);
            setUserInteracted(true);
          }}
          className="flex-1 px-3 py-2 outline-none text-gray-800"
          onFocus={handleFocus}
        />

        {term && (
          <button
            type="button"
            onClick={handleClear}
            className="mr-3 text-gray-400 hover:text-gray-600 transition"
            aria-label="Очистить"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </form>

      {showDropdown && (
        <div className="absolute z-20 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-2xl max-h-80 overflow-y-auto custom-scroll">
          {term.trim().length < 2 ? (
            <div className="p-4 text-gray-500 text-sm">Ничего не найдено</div>
          ) : isLoading ? (
            <div className="p-4 text-gray-500 text-sm">Загрузка...</div>
          ) : results.length > 0 ? (
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
                    inputRef.current?.blur();
                  }}
                >
                  <div className="w-12 h-16 flex-shrink-0 overflow-hidden rounded-lg shadow-md group-hover:scale-105 transition-transform">
                    <img
                      src={
                        anime.poster?.mainUrl ||
                        anime.poster?.originalUrl ||
                        "/placeholder.jpg"
                      }
                      alt={anime.russian || anime.name}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">
                      {anime.russian || anime.name}
                    </p>
                    <p className="text-xs text-gray-500 italic">
                      {anime.info?.english || anime.name}
                    </p>

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

                    <p className="text-[11px] text-gray-400 mt-1">
                      {anime.status} • {anime.aired_on?.year || "—"}
                    </p>
                  </div>

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
