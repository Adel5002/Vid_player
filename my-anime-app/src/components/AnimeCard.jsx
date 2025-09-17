import React, { useState, useEffect, useRef, useCallback } from "react";

// Компонент карточки аниме
const AnimeCard = ({ anime }) => {
  return (
    <div className="anime-card border rounded p-4 shadow mb-4 flex">
      {anime.poster?.local_image_link || anime.poster?.shikimori_image_link ? (
        <img
          src={anime.poster.local_image_link || `https://shikimori.one${anime.poster.shikimori_image_link}`}
          alt={anime.name}
          className="w-24 h-36 object-cover mr-4"
        />
      ) : (
        <div className="w-24 h-36 bg-gray-200 mr-4 flex items-center justify-center">
          No Image
        </div>
      )}
      <div>
        <h3 className="text-lg font-bold">{anime.name}</h3>
        <p className="text-sm text-gray-600">Score: {anime.score || "N/A"}</p>
        <p className="text-sm text-gray-600">Status: {anime.status || "Unknown"}</p>
      </div>
    </div>
  );
};


export default AnimeCard;