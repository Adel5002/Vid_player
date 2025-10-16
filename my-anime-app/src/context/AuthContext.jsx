import React, { createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { api } from "../api/axios";

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
        // URLSearchParams формирует правильный формат
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const userInfo = await api.get(`/users/get-user-by-name/${username}`);
        const { data } = await api.post("/reg/refresh-token", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });

        setAuthTokens(data);
        setUser(jwtDecode(data.access_token));
        localStorage.setItem("authTokens", JSON.stringify(data));
        localStorage.setItem("user", JSON.stringify(userInfo["data"]));
        return true;
    } catch (error) {
        console.error("Login failed:", error.response?.data || error);
        return false;
    }
    };

  const logoutUser = () => {
    setAuthTokens(null);
    setUser(null);
    localStorage.removeItem("authTokens");
    localStorage.removeItem("user");
  };

  const updateToken = async () => {
    if (!authTokens?.refresh_token) return logoutUser();
    try {
      const { data } = await api.post("/reg/access-token", null, {params: {
        refresh_token: authTokens.refresh_token,
      }});

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
