import axios from "axios";

const apiUrl = import.meta.env.VITE_API_URL;


export const fetchAllAnime = (page, limit = 30) =>
  axios.get(`${apiUrl}/anime/all?page=${page}&limit=${limit}`);
