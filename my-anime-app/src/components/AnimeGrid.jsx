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
      {groupedByStatus.map((group) => (
        <section key={group.status} className="space-y-6">
          <h2
            className={`text-3xl font-bold border-b pb-2 ${getStatusStyle(
              group.status
            )}`}
          >
            {group.status.toUpperCase()}
          </h2>
          <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {group.list.map((anime, index) => {
              const isLast =
                group.list.length === index + 1 &&
                group.status === groupedByStatus[groupedByStatus.length - 1].status;
              return (
                <div key={anime.id} ref={isLast ? lastAnimeRef : null}>
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
