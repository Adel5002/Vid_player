import { useEffect, useState, useRef, useCallback } from "react";
import { fetchAnime } from "../api/anime";
import AnimeCard from "../components/AnimeCard";

export default function AnimeList() {
  const [anime, setAnime] = useState([]);
  const [pagesCache, setPagesCache] = useState({});
  const [nextPage, setNextPage] = useState(null);
  const [loading, setLoading] = useState(false);

  const observer = useRef();

  const loadAnime = async (pageId = null) => {
    if (loading) return;

    if (pageId && pagesCache[pageId]) {
      mergeAnime(pagesCache[pageId]);
      return;
    }

    setLoading(true);
    try {
      const data = await fetchAnime(pageId);
      if (data?.results) {
        mergeAnime(data.results);

        if (data.next_page) setNextPage(data.next_page);

        const key = pageId || "first";
        setPagesCache((prev) => ({ ...prev, [key]: data.results }));
      }
    } catch (err) {
      console.error("Ошибка при загрузке аниме:", err);
    } finally {
      setLoading(false);
    }
  };

  const mergeAnime = (newItems) => {
    setAnime((prev) => {
      const combined = [...prev, ...newItems];
      const map = new Map();

      combined.forEach((item) => {
        const key = `${item.title}_${item.year}`;
        if (!map.has(key)) {
          map.set(key, { ...item, translations: [item.translation] });
        } else {
          map.get(key).translations.push(item.translation);
        }
      });

      return Array.from(map.values());
    });
  };

  useEffect(() => {
    loadAnime();
  }, []);

  const lastElementRef = useCallback(
    (node) => {
      if (loading) return;
      if (observer.current) observer.current.disconnect();

      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && nextPage) {
          loadAnime(nextPage);
        }
      });

      if (node) observer.current.observe(node);
    },
    [loading, nextPage]
  );

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Каталог аниме</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {anime.map((item, i) => {
          if (i === anime.length - 1) {
            return <AnimeCard ref={lastElementRef} key={item.id} anime={item} />;
          }
          return <AnimeCard key={item.id} anime={item} />;
        })}
      </div>

      {loading && <p className="mt-4 text-center">Загрузка...</p>}
      {!nextPage && !loading && anime.length > 0 && (
        <p className="mt-4 text-center text-gray-500">Больше нет аниме для подгрузки</p>
      )}
    </div>
  );
}
