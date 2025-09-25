import AnimeCard from "../components/AnimeCard";
import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

const AnimeListPage = () => {
  const [animeList, setAnimeList] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

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
    const fetchAnime = async () => {
      setLoading(true);
      try {
        const response = await axios.get(
          `http://localhost:8000/anime/get-all-anime?page=${page}&limit=20`
        );
        const newAnime = response.data.results;
        setAnimeList((prev) => [...prev, ...newAnime]);
        setHasMore(newAnime.length > 0);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnime();
  }, [page]);

  const statusOrder = ["ongoing", "released", "anons"];
  const getStatusColor = (status) => {
    switch (status) {
      case "ongoing": return "text-red-600";
      case "released": return "text-green-600";
      case "anons": return "text-gray-600";
      default: return "text-gray-400";
    }
  };

  // сгруппировать по статусу
  const groupedByStatus = statusOrder.map((status) => ({
    status,
    list: animeList.filter((a) => a.status === status),
  })).filter((group) => group.list.length > 0);

  return (
    <div className="container mx-auto px-4 py-8 space-y-12">

      {groupedByStatus.map((group) => (
        <section key={group.status} className="space-y-4">
          <h2 className={`text-2xl font-bold mb-4 ${getStatusColor(group.status)}`}>
            {group.status.toUpperCase()}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {group.list.map((anime, index) => {
              const isLast = group.list.length === index + 1 && group.status === groupedByStatus[groupedByStatus.length-1].status;
              return (
                <div key={anime.id} ref={isLast ? lastAnimeRef : null}>
                  <AnimeCard anime={anime} height="h-64" />
                </div>
              );
            })}
          </div>
        </section>
      ))}

      {loading && (
        <p className="text-center mt-6 text-gray-500 animate-pulse">Loading...</p>
      )}

      {!hasMore && !loading && (
        <p className="text-center mt-6 text-gray-400">🎉 No more anime to load</p>
      )}
    </div>
  );
};

export default AnimeListPage;
