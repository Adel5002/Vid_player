import React from "react";

const AnimeList = ({ animeList = [] }) => {
  return (
    <div className="space-y-6">
      {animeList.map((anime) => (
        <div
          key={anime.id}
          className="flex gap-6 bg-white/5 hover:bg-white/10 transition rounded-xl p-4 shadow-lg backdrop-blur-lg"
        >
          <img
            src={
              anime.poster?.mainUrl ||
              anime.poster?.originalUrl ||
              anime.poster?.original ||
              "/placeholder.jpg"
            }
            alt={anime.russian || anime.name}
            className="w-32 h-48 object-cover rounded-lg shadow-lg"
          />
          <div className="flex-1 space-y-3">
            <h3 className="text-2xl font-bold text-pink-400 drop-shadow">
              {anime.russian || anime.name}
            </h3>
            <p className="text-gray-400 text-sm">
              📌 Статус: {anime.status || "Неизвестно"}
            </p>

            {anime.info?.description ? (
              <div
                className="text-gray-300 text-sm leading-relaxed bg-black/40 p-3 rounded-lg overflow-hidden"
                dangerouslySetInnerHTML={{
                  __html: anime.info.description_html,
                }}
              />
            ) : (
              <p className="text-gray-500 italic">Описание отсутствует</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default AnimeList;
