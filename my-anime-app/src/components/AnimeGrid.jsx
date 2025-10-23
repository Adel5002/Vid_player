import React, { useState, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import AnimeCard from "./AnimeCard";
import { animeFilters, animeGenres } from "../api/request_to_api";
import YearRangeSlider from "./YearRangeSlider"

const DEFAULTS = {
  selectedGenre: "",
  selectedStatus: "",
  rating: 5,
  yearStart: 2000,
  yearEnd: 2025,
};

const PARAM_KEYS = ["genre", "status", "rating", "yearStart", "yearEnd"];

const AnimeGrid = ({ groupedByStatus, lastAnimeRef }) => {
  const [searchParams, setSearchParams] = useSearchParams();

  // UI/filters
  const [filters, setFilters] = useState({
    genre: [], // список жанров для селекта
    ...DEFAULTS,
    statusDict: {
      "Онгоинги": "ongoing",
      "Релизы": "released",
      "Анонсы": "anons",
    },
  });

  // data
  const [filteredList, setFilteredList] = useState([]);
  const [loading, setLoading] = useState(false);

  // режимы рендера
  const [initialized, setInitialized] = useState(false);     // когда можно рендерить страницу
  const [isFilteredMode, setIsFilteredMode] = useState(false); // показываем сетку результатов вместо главной

  // ---------- helpers ----------
  const readFiltersFromURL = () => {
    const fromURL = {
      selectedGenre: searchParams.get("genre") ?? DEFAULTS.selectedGenre,
      selectedStatus: searchParams.get("status") ?? DEFAULTS.selectedStatus,
      rating: Number(searchParams.get("rating") ?? DEFAULTS.rating) || DEFAULTS.rating,
      yearStart: parseInt(searchParams.get("yearStart") ?? DEFAULTS.yearStart, 10) || DEFAULTS.yearStart,
      yearEnd: parseInt(searchParams.get("yearEnd") ?? DEFAULTS.yearEnd, 10) || DEFAULTS.yearEnd,
    };
    return fromURL;
  };

  const urlHasAnyParams = useMemo(() => {
    // важно: смотрим именно наличие ключей в URL, а не сравнение со значениями по умолчанию
    return PARAM_KEYS.some((k) => searchParams.has(k));
  }, [searchParams]);

  const searchWith = async (payload) => {
    setLoading(true);
    const params = {
        params: {
          limit: 100,
          genre: payload.selectedGenre || undefined,
          status: payload.selectedStatus || undefined,
          score_min: payload.rating,
          year_start: payload.yearStart,
          year_end: payload.yearEnd,
        },
      }
    try {
      const res = await animeFilters(params)
      setFilteredList(res.data);
    } catch (e) {
      console.error("Ошибка фильтрации:", e);
    } finally {
      setLoading(false);
    }
  };

  const writeURLFromFilters = (state) => {
    const params = new URLSearchParams();
    if (state.selectedGenre) params.set("genre", state.selectedGenre);
    if (state.selectedStatus) params.set("status", state.selectedStatus);
    if (state.rating !== DEFAULTS.rating) params.set("rating", String(state.rating));
    if (state.yearStart !== DEFAULTS.yearStart) params.set("yearStart", String(state.yearStart));
    if (state.yearEnd !== DEFAULTS.yearEnd) params.set("yearEnd", String(state.yearEnd));
    setSearchParams(params);
  };

  // ---------- effects ----------
  // 1) тянем жанры один раз
  useEffect(() => {
    (async () => {
      try {
        const res = await animeGenres()
        const genres = res.data.map((g) => g.russian);
        setFilters((prev) => ({ ...prev, genre: genres }));
      } catch (e) {
        console.error("Ошибка при загрузке жанров:", e);
      }
    })();
  }, []);

  // 2) синхронизируемся с URL при маунте и каждом изменении searchParams.
  //    Важно: если URL содержит параметры -> заходим в filtered mode и делаем запрос ДО рендера главной.
  useEffect(() => {
    const fromURL = readFiltersFromURL();

    setFilters((prev) => ({ ...prev, ...fromURL }));

    if (urlHasAnyParams) {
      setIsFilteredMode(true);
      // делаем запрос и только потом отмечаем initialized=true, чтобы не было "флеша" главной
      (async () => {
        await searchWith(fromURL);
        setInitialized(true);
      })();
    } else {
      // URL без параметров: рендерим главную
      setIsFilteredMode(false);
      setFilteredList([]);
      setInitialized(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]); // намеренно завязаны только на URL

  // ---------- handlers ----------
  const handleFilterChange = (key, value) => {
    // важное изменение: НЕ трогаем URL здесь, только локальный стейт
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleSearch = async () => {
    // пользователь осознанно жмет "Искать" -> пишем URL и делаем запрос
    writeURLFromFilters(filters);
    setIsFilteredMode(true);
    await searchWith(filters);
  };

  const handleReset = () => {
    // сбрасываем локально и чистим URL, выходим из filtered mode
    setFilters((prev) => ({
      ...prev,
      ...DEFAULTS,
    }));
    setIsFilteredMode(false);
    setFilteredList([]);
    setSearchParams(new URLSearchParams()); // очистка URL
  };

  // ---------- render ----------
  if (!initialized) {
    return (
      <div className="flex items-center justify-center py-16 text-gray-300">
        Загрузка…
      </div>
    );
  }

  const getStatusStyle = (status) => {
    switch (status) {
      case "ongoing":
        return "text-pink-400 border-pink-400";
      case "released":
        return "text-green-400 border-green-400";
      case "anons":
        return "text-gray-400 border-gray-400";
      default:
        return "text-gray-500 border-gray-500";
    }
  };

  return (
    <div className="flex flex-col gap-10 text-white">
      {/* 🎛 Панель фильтров */}
<div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-gray-900/70 via-gray-800/60 to-gray-900/70 p-8 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
  <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_top_left,rgba(59,130,246,0.2),transparent_60%)]"></div>

  <h3 className="relative z-10 text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-pink-400 text-center mb-8">
    🌸 Фильтры поиска аниме
  </h3>

  <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
    {/* Жанр */}
    <div className="flex flex-col text-sm">
      <label className="text-gray-300 mb-2 font-medium flex items-center gap-2">
        <span>🎭</span> Жанр
      </label>
      <div className="relative group">
        <select
          className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2.5 text-white appearance-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400 transition-all duration-200 cursor-pointer hover:bg-white/20 backdrop-blur-md"
          value={filters.selectedGenre}
          onChange={(e) => handleFilterChange('selectedGenre', e.target.value)}
        >
          <option value="">Все</option>
          {filters.genre.map((g, idx) => (
            <option key={idx} value={g} className="bg-gray-900 text-white">
              {g}
            </option>
          ))}
        </select>
        <svg
          className="absolute right-3 top-3 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-pink-400 transition-colors"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    {/* Статус */}
    <div className="flex flex-col text-sm">
      <label className="text-gray-300 mb-2 font-medium flex items-center gap-2">
        <span>📺</span> Статус
      </label>
      <div className="relative group">
        <select
          className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2.5 text-white appearance-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400 transition-all duration-200 cursor-pointer hover:bg-white/20"
          value={filters.selectedStatus}
          onChange={(e) => handleFilterChange('selectedStatus', e.target.value)}
        >
          <option value="">Все</option>
          {Object.entries(filters.statusDict).map(([label, value]) => (
            <option key={value} value={value} className="bg-gray-900 text-white">
              {label}
            </option>
          ))}
        </select>
        <svg
          className="absolute right-3 top-3 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-pink-400 transition-colors"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    {/* ⭐ Минимальный рейтинг */}
    <div className="flex flex-col text-sm">
      <label className="text-gray-300 mb-2 font-medium flex items-center gap-2">
        <span>⭐</span> Минимальный рейтинг
      </label>
      <div className="relative w-full">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>0</span>
          <span className="text-pink-400 font-semibold">{filters.rating.toFixed(1)}</span>
          <span>10</span>
        </div>
        <input
          type="range"
          min="0"
          max="10"
          step="0.1"
          value={filters.rating}
          onChange={(e) => handleFilterChange('rating', parseFloat(e.target.value))}
          className="w-full h-2 bg-gradient-to-r from-blue-400/50 to-pink-400/50 rounded-lg appearance-none cursor-pointer hover:from-blue-400 hover:to-pink-400 transition-all"
        />
      </div>
    </div>

    {/* 🎚 Диапазон годов */}
    <YearRangeSlider
      value={[filters.yearStart, filters.yearEnd]}
      onChange={([start, end]) => {
        handleFilterChange('yearStart', start);
        handleFilterChange('yearEnd', end);
      }}
    />

    {/* 🔘 Кнопки */}
    <div className="flex flex-col items-end justify-end gap-3">
      <button
        onClick={handleReset}
        disabled={loading}
        className="w-full px-4 py-2 rounded-lg font-medium text-white/80 border border-white/20 hover:border-pink-400 hover:text-pink-400 transition-all text-sm"
      >
        Сбросить
      </button>
      <button
        onClick={handleSearch}
        disabled={loading}
        className="w-full px-6 py-2.5 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:opacity-90 transition-all shadow-[0_0_15px_rgba(147,51,234,0.5)]"
      >
        {loading ? 'Поиск...' : 'Искать 🔍'}
      </button>
    </div>
  </div>
</div>

      {/* 🧩 Контент */}
      {isFilteredMode ? (
        <div className="min-h-[200px]">
          {loading ? (
            <div className="flex items-center justify-center py-16 text-gray-300">Загрузка…</div>
          ) : filteredList.length > 0 ? (
            <div className="grid gap-6 sm:gap-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
              {filteredList.map((anime) => (
                <AnimeCard key={anime.id} anime={anime} height="h-72" />
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-300 py-12">Ничего не найдено</div>
          )}
        </div>
      ) : (
        groupedByStatus.map((group, groupIndex) => (
          <section key={group.status} className="space-y-6">
            <h2
              className={`text-2xl sm:text-3xl font-bold border-b pb-2 ${getStatusStyle(group.status)}`}
            >
              {group.status.toUpperCase()}
            </h2>

            <div className="grid gap-6 sm:gap-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
              {group.list.map((anime, index) => {
                const isLastGroup = groupIndex === groupedByStatus.length - 1;
                const isLastItem = index === group.list.length - 1;
                const refProp = isLastGroup && isLastItem ? { ref: lastAnimeRef } : {};
                return (
                  <div key={anime.id} {...refProp}>
                    <AnimeCard anime={anime} height="h-72" />
                  </div>
                );
              })}
            </div>
          </section>
        ))
      )}
    </div>
  );
};

export default AnimeGrid;
