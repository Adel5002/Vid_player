import React, { createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { login, logout, refresh, userByName } from "../api/request_to_api";
import Cookies from "js-cookie";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authTokens, setAuthTokens] = useState(() =>
    localStorage.getItem("authTokens")
      ? JSON.parse(localStorage.getItem("authTokens"))
      : null
  );
  const [user, setUser] = useState(() =>
    authTokens ? jwtDecode(authTokens.access_token) : null
  );

  const loginUser = async (username, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);
      const headers = {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }

      console.log()

      const userInfo = await userByName(username)
      const { data } = await login(formData, headers)
      
      setAuthTokens(data);
      setUser(jwtDecode(data.access_token));
      localStorage.setItem("authTokens", JSON.stringify(data));
      Cookies.set("user", JSON.stringify(userInfo["data"]), { path: "/" });
      return { success: true };
    } catch (error) {
      console.error("Login failed:", error.response?.data || error);
      const status = error.response?.status;
      const message =
        status === 429
          ? "Слишком много попыток входа. Попробуйте позже."
          : error.response?.data?.detail || "Неверный логин или пароль";
      return { success: false, message };
    }
  };

  const logoutUser = async () => {
    try {
      await logout()
    } catch (e) {
      console.warn("Logout API failed:", e);
    } finally {
      setAuthTokens(null);
      setUser(null);
      localStorage.removeItem("authTokens");
       window.location.href = "/";
    }
  };

  const updateToken = async () => {
    if (!authTokens?.refresh_token) return await logoutUser();
    const params = {params: {
        refresh_token: authTokens.refresh_token,
      }}
    try {
      const { data } = await refresh(params)

      const newTokens = {
        ...authTokens,
        access_token: data.access_token,
        refresh_token: data.refresh_token,
      };

      setAuthTokens(newTokens);
      setUser(jwtDecode(data.access_token));
      localStorage.setItem("authTokens", JSON.stringify(newTokens));
    } catch (err) {
      console.warn("Token refresh failed:", err.response?.data || err);
      logoutUser();
    }
  };
  // TODO: разобраться с перелогированием пользователя
  // ⏱ Автообновление токена каждые 10 минут
  useEffect(() => {
    if (!authTokens) return;

    const interval = setInterval(() => {
      updateToken();
    }, 15 * 60 * 1000);

    return () => clearInterval(interval);
  }, [authTokens]);

  return (
    <AuthContext.Provider
      value={{
        user,
        authTokens,
        loginUser,
        logoutUser,
        updateToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
