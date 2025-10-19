import React, { useEffect, useState } from "react";
import AnimeList from "../components/AnimeList";
import { api } from "../api/axios";

const UserProfilePage = () => {
  const [animeList, setAnimeList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Безопасно получаем профиль из localStorage
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const profileId = user?.profile;

  useEffect(() => {
    if (!profileId) {
      setError("Не найден ID профиля пользователя");
      setLoading(false);
      return;
    }

    const fetchUserAnime = async () => {
      try {
        const res = await api.get(`/users/profile/${profileId}`);
        setAnimeList(
        res.data?.watch_anime
          ?.filter(anime => !anime.is_disabled)
          ?.map(anime => ({
            ...anime.anime, // сам объект аниме
            watchAnimeID: anime.id // ID записи в списке
          }))
      );
      } catch (err) {
        console.error(err);
        setError(err.response?.data?.message || "Ошибка загрузки данных пользователя");
      } finally {
        setLoading(false);
      }
    };

    fetchUserAnime();
  }, [profileId]);

  const animeWatchDisable = async (watchAnimeID) => {
    console.log(watchAnimeID)
    try {
      const request_data = {
        "is_disabled": true
      }
      await api.patch(`/watch-list/update-watch-anime/${watchAnimeID}`, request_data);
      setAnimeList(prev => prev.filter(a => a.watchAnimeID !== watchAnimeID));
    } catch (e) {
      console.log("Ошибка: ", e)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen text-gray-400">
        🔄 Загрузка профиля...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen text-red-500 text-lg">
        {error}
      </div>
    );
  }
  // TODO: Удалять аниме после просмотра
  // TODO: Рекомендации на основе просмотра
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-gray-900 text-white">
      <div className="container mx-auto px-6 py-10 space-y-10">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-pink-400 mb-2">Мой профиль</h1>
          <p className="text-gray-400">Список аниме, которые вы сейчас смотрите 👇</p>
        </div>

        {animeList.length === 0 ? (
          <p className="text-center text-gray-400 italic mt-20">
            😕 Пока нет аниме в списке
          </p>
        ) : (
          <AnimeList animeList={animeList} onRemove={animeWatchDisable}/>
        )}
      </div>
    </div>
  );
};

export default UserProfilePage;
