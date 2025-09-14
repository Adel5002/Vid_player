import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true, // если куки
  headers: { "Content-Type": "application/json" },
});

console.log(import.meta.env.VITE_API_URL)

export default API;