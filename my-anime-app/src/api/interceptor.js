import { api } from "./axios";
import * as jwtDecode from "jwt-decode";

export const setupAxiosInterceptors = (authTokens, updateToken, logoutUser) => {
  api.interceptors.request.use(
    (config) => {
      if (authTokens?.access_token) {
        config.headers.Authorization = `Bearer ${authTokens.access_token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // Если токен просрочен и запрос ещё не повторяли
      if (
        error.response?.status === 401 &&
        !originalRequest._retry &&
        authTokens?.refresh_token
      ) {
        originalRequest._retry = true;
        try {
          await updateToken(); // обновляем токен
          originalRequest.headers.Authorization = `Bearer ${authTokens.access_token}`;
          return api(originalRequest); // повторяем запрос
        } catch (err) {
          logoutUser();
          return Promise.reject(err);
        }
      }

      return Promise.reject(error);
    }
  );
};
