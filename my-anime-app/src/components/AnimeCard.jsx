import React, { useEffect, useState } from "react";
import axios from "axios";

const AnimeCard = React.forwardRef(({ anime }, ref) => {
  const [poster, setPoster] = useState("/images/no-poster.png"); // базовый fallback

  useEffect(() => {
    const fetchPoster = async () => {
      try {
        const res = await axios.post(
          `${import.meta.env.VITE_API_URL}/anime/get-anime-poster`,
          {
            shikimori_id: anime.shikimori_id,

          }
        );

        if (res.data.poster && res.data.poster.length > 0) {
          setPoster(res.data.poster);
        }
      } catch (err) {
        console.error("Ошибка при загрузке постера:", err);
        setPoster(anime.screenshots?.[0] || "/images/no-poster.png");
      }
    };

    fetchPoster();
  }, [anime.shikimori_id, anime.screenshots]);

  return (
    <div
      ref={ref}
      className="border rounded overflow-hidden shadow hover:shadow-lg transition"
    >
      <img
        src={poster}
        alt={anime.title}
        className="w-full h-64 object-cover"
      />
      <div className="p-2">
        <h2 className="text-lg font-semibold">{anime.title}</h2>
        <p className="text-sm text-gray-500">{anime.year}</p>
        <p className="text-sm text-gray-400">{anime.translation?.title}</p>
      </div>
    </div>
  );
});

export default AnimeCard;
