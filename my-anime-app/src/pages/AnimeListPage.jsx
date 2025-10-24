import React, { useState, useEffect, useRef, useCallback } from "react";
import { fetchAllAnime } from "../api/request_to_api";
import AnimeGrid from "../components/AnimeGrid";

const AnimeListPage = () => {
  const [animeList, setAnimeList] = useState([]);
  const [nextPage, setNextPage] = useState(null);
  const [prevPage, setPrevPage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [dbNotReady, setDbNotReady] = useState(false);

  const observer = useRef();

  const lastAnimeRef = useCallback(
    (node) => {
      if (loading || !hasMore) return;
      if (observer.current) observer.current.disconnect();
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          // 🚀 подгружаем следующую страницу по курсору
          loadMore();
        }
      });
      if (node) observer.current.observe(node);
    },
    [loading, hasMore, nextPage]
  );

  // ----------------------
  // 🔹 функция загрузки
  // ----------------------
  const loadMore = async () => {
    if (loading) return;
    setLoading(true);

    try {
      const response = await fetchAllAnime(30, nextPage);
      const data = response.data;

      if (data.status) {
        setDbNotReady(true);
        setHasMore(false);
        return;
      }

      setAnimeList((prev) => [...prev, ...data.items]);
      setNextPage(data.next_page);
      setPrevPage(data.prev_page);
      setHasMore(data.has_next);
    } catch (err) {
      console.error("Ошибка при загрузке:", err);
    } finally {
      setLoading(false);
    }
  };

  // ----------------------
  // 🔹 первая загрузка
  // ----------------------
  useEffect(() => {
    loadMore(); // первая страница
  }, []);

  // ----------------------
  // 🔹 группировка по статусу
  // ----------------------
  const statusOrder = ["ongoing", "released", "anons"];
  const groupedByStatus = statusOrder
    .map((status) => ({
      status,
      list: animeList.filter((a) => a.status === status),
    }))
    .filter((group) => group.list.length > 0);

  // ----------------------
  // 🔹 рендер
  // ----------------------
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-gray-900 text-white">
      <div className="container mx-auto px-3 sm:px-6 py-6 sm:py-10 space-y-6 sm:space-y-10">
        {dbNotReady && (
          <p className="text-center text-yellow-400 font-semibold bg-yellow-500/10 py-2 sm:py-3 px-3 rounded-lg shadow-md text-sm sm:text-base">
            ⏳ База данных наполняется, попробуйте позже...
          </p>
        )}

        <AnimeGrid groupedByStatus={groupedByStatus} lastAnimeRef={lastAnimeRef} />

        {loading && (
          <p className="text-center mt-6 sm:mt-8 text-gray-400 animate-pulse text-base sm:text-lg">
            🔄 Загрузка...
          </p>
        )}

        {!hasMore && !loading && !dbNotReady && (
          <p className="text-center mt-6 sm:mt-8 text-gray-500 italic text-sm sm:text-base">
            🎉 Все аниме загружены!
          </p>
        )}
      </div>
    </div>
  );
};

export default AnimeListPage;
