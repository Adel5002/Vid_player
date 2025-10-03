import React, { useState, useEffect, useRef, useCallback } from "react";
import { fetchAllAnime, fetchAnimeByName } from "../api/anime";
import AnimeGrid from "../components/AnimeGrid";
import AnimeList from "../components/AnimeList";
import AnimeSearchBar from "../components/AnimeSearchBar";

const AnimeListPage = () => {
  const [animeList, setAnimeList] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [dbNotReady, setDbNotReady] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

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
    if (searchResults.length) return;
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
  }, [page, searchResults]);

  const handleSearch = async (term) => {
    setLoading(true);
    try {
      const response = await fetchAnimeByName(term);
      setSearchResults(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error(err);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const statusOrder = ["ongoing", "released", "anons"];
  const groupedByStatus = statusOrder
    .map((status) => ({
      status,
      list: animeList.filter((a) => a.status === status),
    }))
    .filter((group) => group.list.length > 0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-gray-900 text-white">
      <div className="container mx-auto px-6 py-10 space-y-10">
        

        {dbNotReady && (
          <p className="text-center text-yellow-400 font-semibold bg-yellow-500/10 py-3 rounded-lg shadow-md">
            ⏳ База данных наполняется, попробуйте позже...
          </p>
        )}

        {searchResults.length > 0 ? (
          <AnimeList animeList={searchResults} />
        ) : (
          <AnimeGrid groupedByStatus={groupedByStatus} lastAnimeRef={lastAnimeRef} />
        )}

        {loading && (
          <p className="text-center mt-8 text-gray-400 animate-pulse text-lg">
            🔄 Loading anime...
          </p>
        )}

        {!hasMore && !loading && !dbNotReady && searchResults.length === 0 && (
          <p className="text-center mt-8 text-gray-500 italic">
            🎉 Все аниме загружены!
          </p>
        )}
      </div>
    </div>
  );
};

export default AnimeListPage;
