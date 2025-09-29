import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

// Swiper
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation } from "swiper/modules";

// Swiper стили
import "swiper/css";
import "swiper/css/navigation";

const AnimeInfoPage = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const { id } = useParams();
  const [anime, setAnime] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnime = async () => {
      try {
        const response = await axios.get(`${apiUrl}/anime/anime-watch/${id}`);
        setAnime(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnime();
  }, [id]);

  if (loading) return <p className="text-center text-gray-400">Loading...</p>;
  if (!anime) return <p className="text-center text-red-500">Anime not found</p>;

  return (
    <div className="bg-[#0a0f1c] min-h-screen text-white">
      <div className="container mx-auto px-6 py-10">
        {/* Верхний блок */}
        <div className="flex flex-col md:flex-row gap-6">
          <img
            src={anime.poster?.mainUrl || anime.poster?.originalUrl || "/placeholder.jpg"}
            alt={anime.russian || anime.name || "Anime Poster"}
            className="w-72 h-auto rounded-xl shadow-lg object-cover"
          />
          <div className="flex-1 space-y-4">
            <h1 className="text-4xl font-bold">{anime.russian || "Без названия"}</h1>
            <p className="text-gray-400 italic">{anime.name || "Нет английского названия"}</p>
            <div className="flex gap-4 text-sm flex-wrap">
              <span className="px-3 py-1 rounded bg-green-700">{anime.status || "Статус неизвестен"}</span>
              <span className="px-3 py-1 rounded bg-blue-700">⭐ {anime.score || "N/A"}</span>
              <span className="px-3 py-1 rounded bg-gray-700">{anime.kind || "Неизвестный тип"}</span>
              <span className="px-3 py-1 rounded bg-purple-700">
                {anime.info?.duration ? `${anime.info.duration} мин/эп` : "Длительность неизвестна"}
              </span>
            </div>
            <div
              className="prose prose-invert max-w-none bg-black/40 p-4 rounded-lg"
              dangerouslySetInnerHTML={{
                __html:
                  anime.info?.description_html?.replace(/<[^>]+>/g, "").trim()
                    ? anime.info.description_html
                    : "<p>Описание отсутствует</p>",
              }}
            />
          </div>
        </div>

        {/* Студии / жанры */}
        <div className="mt-10 grid md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-2xl font-semibold mb-2">Студии</h2>
            {anime.info?.studios?.length > 0 ? (
              <ul className="list-disc list-inside text-gray-300">
                {anime.info.studios.map((s) => <li key={s.id}>{s.name}</li>)}
              </ul>
            ) : (
              <p className="text-gray-500">Студии отсутствуют</p>
            )}
          </div>
          <div>
            <h2 className="text-2xl font-semibold mb-2">Жанры</h2>
            {anime.genres?.length > 0 ? (
              <ul className="list-disc list-inside text-gray-300">
                {anime.genres.map((g, i) => <li key={i}>{g}</li>)}
              </ul>
            ) : (
              <p className="text-gray-500">Жанры не указаны</p>
            )}
          </div>
        </div>

        {/* Озвучка / субтитры */}
        <div className="mt-10 grid md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-2xl font-semibold mb-2">Озвучка</h2>
            {anime.info?.fandubbers?.length > 0 ? (
              <ul className="grid grid-cols-2 gap-1 text-gray-300 text-sm">
                {anime.info.fandubbers.map((f, i) => <li key={i}>🎤 {f}</li>)}
              </ul>
            ) : (
              <p className="text-gray-500">Нет информации об озвучке</p>
            )}
          </div>
          <div>
            <h2 className="text-2xl font-semibold mb-2">Субтитры</h2>
            {anime.info?.fansubbers?.length > 0 ? (
              <ul className="grid grid-cols-2 gap-1 text-gray-300 text-sm">
                {anime.info.fansubbers.map((f, i) => <li key={i}>📝 {f}</li>)}
              </ul>
            ) : (
              <p className="text-gray-500">Нет информации о субтитрах</p>
            )}
          </div>
        </div>

        {/* Видео трейлеры */}
        <div className="mt-10">
          <h2 className="text-2xl font-semibold mb-4">Трейлеры</h2>
          {anime.info?.videos?.length > 0 ? (
            <Swiper spaceBetween={20} slidesPerView={3} navigation modules={[Navigation]}>
              {anime.info.videos.map((v) => (
                <SwiperSlide key={v.id}>
                  <iframe
                    src={v.playerUrl}
                    title={v.name}
                    className="w-full h-64 rounded-lg shadow-lg"
                    allowFullScreen
                  />
                </SwiperSlide>
              ))}
            </Swiper>
          ) : (
            <p className="text-gray-500">Нет трейлеров</p>
          )}
        </div>

        {/* Скриншоты */}
        <div className="mt-10">
          <h2 className="text-2xl font-semibold mb-4">Скриншоты</h2>
          {anime.info?.screenshots?.length > 0 ? (
            <Swiper spaceBetween={10} slidesPerView={3} navigation modules={[Navigation]}>
              {anime.info.screenshots.map((s, i) => (
                <SwiperSlide key={i}>
                  <img
                    src={s.originalUrl || s.preview}
                    alt={`screenshot-${i}`}
                    className="rounded-lg shadow-md w-full h-48 object-cover"
                  />
                </SwiperSlide>
              ))}
            </Swiper>
          ) : (
            <p className="text-gray-500">Нет скриншотов</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnimeInfoPage;
