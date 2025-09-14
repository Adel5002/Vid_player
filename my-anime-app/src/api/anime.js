// src/api/anime.js
import API from "./client";

export async function fetchAnime(next = null) {
  const url = next ? `/anime/get-all-anime?next_page=${next}` : `/anime/get-all-anime`;
  const res = await API.get(url);
  return res.data;
}
