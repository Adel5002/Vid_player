import React from "react";
import AnimeCard from "./AnimeCard";

const AnimeGrid = ({ groupedByStatus, lastAnimeRef }) => {
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
    <>
      {groupedByStatus.map((group, groupIndex) => (
        <section key={group.status} className="space-y-6">
          {/* Заголовок статуса */}
          <h2
            className={`text-2xl sm:text-3xl font-bold border-b pb-2 ${getStatusStyle(
              group.status
            )}`}
          >
            {group.status.toUpperCase()}
          </h2>

          {/* Сетка карточек */}
          <div
            className="
              grid gap-6 sm:gap-8
              grid-cols-1 
              sm:grid-cols-2 
              md:grid-cols-3 
              lg:grid-cols-4 
              xl:grid-cols-5
            "
          >
            {group.list.map((anime, index) => {
              const isLastGroup = groupIndex === groupedByStatus.length - 1;
              const isLastItem = index === group.list.length - 1;

              // ref только на последнюю карточку последнего блока
              const refProp =
                isLastGroup && isLastItem ? { ref: lastAnimeRef } : {};

              return (
                <div key={anime.id} {...refProp}>
                  <AnimeCard anime={anime} height="h-72" />
                </div>
              );
            })}
          </div>
        </section>
      ))}
    </>
  );
};

export default AnimeGrid;
