import AnimeCard from '../components/AnimeCard'
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

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Anime List</h1>
      <div className="flex flex-col">
        {animeList.map((anime, index) => {
            console.log(anime)
          if (animeList.length === index + 1) {
            return (
              <div ref={lastAnimeRef} key={`${anime.id}-${index}`}>
                <AnimeCard anime={anime} />
              </div>
            );
          } else {
            return <AnimeCard key={`${anime.id}-${index}`} anime={anime} />;
          }
        })}
      </div>
      {loading && <p className="text-center mt-4">Loading...</p>}
      {!hasMore && <p className="text-center mt-4">No more anime to load</p>}
    </div>
  );
};

export default AnimeListPage;