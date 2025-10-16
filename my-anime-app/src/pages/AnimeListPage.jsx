import React, { useState, useEffect, useRef, useCallback } from "react";
import { fetchAllAnime, fetchAnimeByName } from "../api/anime";
import AnimeGrid from "../components/AnimeGrid";
import AnimeList from "../components/AnimeList";

const AnimeListPage = () => {
  const [animeList, setAnimeList] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [dbNotReady, setDbNotReady] = useState(false);
  

  const observer = useRef();

  const lastAnimeRef = useCallback(
    (node) => {
      if (loading) return;
      if (observer.current) observer.current.disconnect();
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          setPage((prevPage) => prevPage + 1);
        }
      });
      if (node) observer.current.observe(node);
    },
    [loading, hasMore]
  );

  useEffect(() => {
    
    const loadAnime = async () => {
      setLoading(true);
      try {
        const response = await fetchAllAnime(page);
        if (response.data?.status) {
          setDbNotReady(true);
          setHasMore(false);
          return;
        }
        const newAnime = response.data;
        setAnimeList((prev) => [...prev, ...newAnime]);
        setHasMore(newAnime.length > 0);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadAnime();
  }, [page, ]);

  

  const statusOrder = ["ongoing", "released", "anons"];
  const groupedByStatus = statusOrder
    .map((status) => ({
      status,
      list: animeList.filter((a) => a.status === status),
    }))
    .filter((group) => group.list.length > 0);

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
