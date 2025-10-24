import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL;

export const ENDPOINTS = {
  anime: {
    // 🔹 Аниме
    all: (limit = 30, next_page = null, prev_page = null) =>
      `${BASE_URL}/anime/all?limit=${limit}${
        next_page ? `&next_page=${encodeURIComponent(next_page)}` : ""
      }${prev_page ? `&prev_page=${encodeURIComponent(prev_page)}` : ""}`,

    byId: (id) => `${BASE_URL}/anime/${id}`,
    byName: (name) => `${BASE_URL}/anime/by-name/${name}`,
    filters: `${BASE_URL}/anime/filters`,
    genres: `${BASE_URL}/anime/genres`,
    recommendations: (id) => `${BASE_URL}/anime/${id}/recommendations`,

    // 🔹 Популярные аниме (тоже на курсорах)
    popular: (limit = 20, next_page = null, prev_page = null) =>
      `${BASE_URL}/anime/popular?limit=${limit}${
        next_page ? `&next_page=${encodeURIComponent(next_page)}` : ""
      }${prev_page ? `&prev_page=${encodeURIComponent(prev_page)}` : ""}`,
  },

  authentication: {
    register: `${BASE_URL}/reg/register`,
    login: `${BASE_URL}/reg/refresh-token`,
    logout: `${BASE_URL}/reg/logout`,
    refresh: `${BASE_URL}/reg/access-token`,
  },

  user: {
    byName: (username) => `${BASE_URL}/users/get-user-by-name/${username}`,
    profile: (id) => `${BASE_URL}/users/profile/${id}`,
  },

  watchList: {
    byProfileAndAnime: (profileId, animeId) =>
      `${BASE_URL}/watch-list/get-watch-anime-by-profile-id/${profileId}/${animeId}`,
    create: `${BASE_URL}/watch-list/create-watch-anime/`,
    update: (id) => `${BASE_URL}/watch-list/update-watch-anime/${id}`,
  },
};

// =========================
// 🟢 Anime Requests
// =========================

// 📦 Все аниме (теперь с курсорами)
export const fetchAllAnime = (limit = 30, next_page = null, prev_page = null) => {
  const params = { limit };
  if (next_page) params.next_page = next_page;
  if (prev_page) params.prev_page = prev_page;
  return axios.get(`${BASE_URL}/anime/all`, { params });
};

// 📦 Популярные аниме (с курсорами)
export const fetchPopularAnime = (limit = 20, next_page = null, prev_page = null) => {
  const params = { limit };
  if (next_page) params.next_page = next_page;
  if (prev_page) params.prev_page = prev_page;
  return axios.get(`${BASE_URL}/anime/popular`, { params });
};

export const animeById = (id) => axios.get(ENDPOINTS.anime.byId(id));
export const animeByName = (name) => axios.get(ENDPOINTS.anime.byName(name));
export const animeFilters = (params) => axios.get(ENDPOINTS.anime.filters, params);
export const animeGenres = () => axios.get(ENDPOINTS.anime.genres);
export const animeRecommendations = (id) =>
  axios.get(ENDPOINTS.anime.recommendations(id));

// =========================
// 🟢 Auth Requests
// =========================

export const register = async (username, email, password, navigate) => {
  await axios.post(ENDPOINTS.authentication.register, { username, email, password });
  navigate("/check-email");
};

export const login = (formData, headers) =>
  axios.post(ENDPOINTS.authentication.login, formData, headers);

export const logout = () => axios.post(ENDPOINTS.authentication.logout);

export const refresh = (params) =>
  axios.post(ENDPOINTS.authentication.refresh, null, params);

// =========================
// 🟢 User Requests
// =========================

export const userByName = (username) => axios.get(ENDPOINTS.user.byName(username));
export const fetchUserProfile = (id) => axios.get(ENDPOINTS.user.profile(id));

// =========================
// 🟢 Watch List Requests
// =========================

export const getWatchAnimeByProfile = (profileId, animeId) =>
  axios.get(ENDPOINTS.watchList.byProfileAndAnime(profileId, animeId));

export const createWatchAnime = (body) =>
  axios.post(ENDPOINTS.watchList.create, body);

export const updateWatchAnime = (id, body) =>
  axios.patch(ENDPOINTS.watchList.update(id), body);
