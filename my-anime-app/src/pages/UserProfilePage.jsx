import React, { useEffect, useState } from "react";
import AnimeList from "../components/AnimeList";
import Cookies from "js-cookie";
import {
  fetchUserProfile,
  updateWatchAnime,
} from "../api/request_to_api"; // ✅ централизованный импорт

const UserProfilePage = () => {
  const [animeList, setAnimeList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 🧩 Безопасно получаем ID профиля
  const user = Cookies.get("user");
  const profileId = user ? JSON.parse(user).profile : null;

  useEffect(() => {
    if (!profileId) {
      setError("Не найден ID профиля пользователя");
      setLoading(false);
      return;
    }

    const fetchUserAnime = async () => {
      try {
        const { data } = await fetchUserProfile(profileId); // ✅ централизованный вызов
        const list =
          data?.watch_anime
            ?.filter((anime) => !anime.is_disabled)
            ?.map((anime) => ({
              ...anime.anime,
              watchAnimeID: anime.id,
            })) || [];
        setAnimeList(list);
      } catch (err) {
        console.error(err);
        setError(
          err.response?.data?.message || "Ошибка загрузки данных пользователя"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchUserAnime();
  }, [profileId]);

  // 🔻 Удаление аниме из списка (помечаем как disabled)
  const animeWatchDisable = async (watchAnimeID) => {
    try {
      await updateWatchAnime(watchAnimeID, { is_disabled: true }); // ✅ централизованный вызов
      setAnimeList((prev) =>
        prev.filter((a) => a.watchAnimeID !== watchAnimeID)
      );
    } catch (e) {
      console.error("Ошибка при обновлении статуса аниме:", e);
    }
  };

  // 💫 Состояния загрузки / ошибки
  if (loading)
    return (
      <div className="flex justify-center items-center h-screen text-gray-400">
        🔄 Загрузка профиля...
      </div>
    );

  if (error)
    return (
      <div className="flex justify-center items-center h-screen text-red-500 text-lg">
        {error}
      </div>
    );

  // 🎬 Основной контент
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-gray-900 text-white">
      <div className="container mx-auto px-6 py-10 space-y-10">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-pink-400 mb-2">Мой профиль</h1>
          <p className="text-gray-400">
            Список аниме, которые вы сейчас смотрите 👇
          </p>
        </div>

        {animeList.length === 0 ? (
          <p className="text-center text-gray-400 italic mt-20">
            😕 Пока нет аниме в списке
          </p>
        ) : (
          <AnimeList animeList={animeList} onRemove={animeWatchDisable} />
        )}
      </div>
    </div>
  );
};

export default UserProfilePage;
