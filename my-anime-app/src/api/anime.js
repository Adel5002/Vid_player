// src/api/anime.js
import API from "./client";
import axios from "axios";

const apiUrl = import.meta.env.VITE_API_URL;


export const fetchAllAnime = (page, limit = 20) =>
  axios.get(`${apiUrl}/anime/get-all-anime?page=${page}&limit=${limit}`);

export const fetchAnimeByName = (name) =>
  axios.get(`${apiUrl}/anime/get-anime-by_name/${encodeURIComponent(name)}`); 