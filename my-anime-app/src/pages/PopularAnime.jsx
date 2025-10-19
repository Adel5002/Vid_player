import React, { useEffect, useState, useRef, useCallback } from "react";
import { api } from "../api/axios";
import AnimeCard from "../components/AnimeCard";
import { motion } from "framer-motion";

const PopularAnime = () => {
  const [animeList, setAnimeList] = useState([]);
  const [nextPage, setNextPage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchingMore, setFetchingMore] = useState(false);
  const observerRef = useRef(null);

  const LIMIT = 20;

  // 🧠 Функция для загрузки данных
  const fetchAnime = async (page = null, append = false) => {
    try {
      if (append) setFetchingMore(true);
      else setLoading(true);

      const res = await api.get("/anime/get-popular-anime", {
        params: {
          limit: LIMIT,
          next_page: page || undefined,
        },
      });

      const data = res.data;
      if (!data) return;

      setAnimeList((prev) =>
        append ? [...prev, ...data.items] : data.items || []
      );

      setNextPage(data.next_page || null);
    } catch (err) {
      console.error("Ошибка при загрузке популярных аниме:", err);
    } finally {
      setLoading(false);
      setFetchingMore(false);
    }
  };

  // 🪄 При первом рендере — загрузить первую страницу
  useEffect(() => {
    fetchAnime();
  }, []);

  // 📜 IntersectionObserver для бесконечного скролла
  const lastElementRef = useCallback(
    (node) => {
      if (fetchingMore || loading) return;
      if (observerRef.current) observerRef.current.disconnect();

      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && nextPage) {
          fetchAnime(nextPage, true);
        }
      });

      if (node) observerRef.current.observe(node);
    },
    [fetchingMore, loading, nextPage]
  );

  return (
    <div className="min-h-screen text-white px-3 sm:px-6 md:px-10 py-8">
      {/* 🧭 Заголовок */}
      <motion.div
        className="text-center mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl sm:text-4xl font-extrabold text-blue-400 mb-2">
          Популярное аниме 🔥
        </h1>
        <p className="text-gray-400 text-sm sm:text-base">
          Самые рейтинговые и обсуждаемые тайтлы прямо сейчас
        </p>
      </motion.div>

      {/* ⏳ Загрузка первой страницы */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 sm:gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="w-full h-[260px] sm:h-[320px] bg-gray-800/60 rounded-xl animate-pulse"
            />
          ))}
        </div>
      ) : (
        <>
          {/* 🎴 Сетка карточек */}
          <motion.div
            className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 sm:gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
          >
            {animeList.map((anime, i) => {
              if (i === animeList.length - 1) {
                return (
                  <div ref={lastElementRef} key={anime.shikimori_id}>
                    <AnimeCard anime={anime} />
                  </div>
                );
              } else {
                return <AnimeCard key={anime.shikimori_id} anime={anime} />;
              }
            })}
          </motion.div>

          {/* ⚙️ Идёт подгрузка */}
          {fetchingMore && (
            <div className="flex justify-center py-8 text-gray-400 animate-pulse">
              Загрузка следующей страницы...
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PopularAnime;
