import React, { useEffect, useState, useRef, forwardRef } from "react";
import { useParams } from "react-router-dom";
import { animeById } from "../api/request_to_api"; // ✅ импорт централизованной функции
import RecommendationsBlock from "../components/Recommendations";
import KodikPlayer from "../components/KodikPlayer";

// Swiper
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, FreeMode } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/free-mode";

// Icons
import { ChevronLeft, ChevronRight } from "lucide-react";

// 🔘 Универсальная кнопка
const ArrowButton = forwardRef(({ side = "left" }, ref) => (
  <button
    ref={ref}
    className={`absolute top-1/2 -translate-y-1/2 z-10 hidden sm:flex
      bg-gradient-to-r from-purple-600 to-pink-500 opacity-80 hover:opacity-100
      p-3 rounded-full shadow-xl transition duration-300
      ${side === "left" ? "left-3" : "right-3"}`}
    aria-label={side === "left" ? "Previous" : "Next"}
  >
    {side === "left" ? (
      <ChevronLeft className="w-6 h-6 text-white drop-shadow" />
    ) : (
      <ChevronRight className="w-6 h-6 text-white drop-shadow" />
    )}
  </button>
));
ArrowButton.displayName = "ArrowButton";

const AnimeInfoPage = () => {
  const { id } = useParams();
  const [anime, setAnime] = useState(null);
  const [loading, setLoading] = useState(true);

  const prevRefVideos = useRef(null);
  const nextRefVideos = useRef(null);
  const prevRefScreens = useRef(null);
  const nextRefScreens = useRef(null);

  useEffect(() => {
    const fetchAnime = async () => {
      try {
        const { data } = await animeById(id); // ✅ централизованный вызов
        setAnime(data);
      } catch (e) {
        console.error("Ошибка загрузки аниме:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchAnime();
  }, [id]);

  if (loading)
    return <p className="text-center text-gray-400 py-20 text-lg">⏳ Загрузка...</p>;
  if (!anime)
    return <p className="text-center text-red-500 py-20 text-lg">❌ Аниме не найдено</p>;

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0a0f1c] via-[#0f0f1f] to-black text-white">
      <div className="mx-auto px-2 sm:px-6 py-10 space-y-12 max-w-6xl">
        {/* 🏮 Верхний блок */}
        <div className="flex flex-col md:flex-row gap-8 bg-white/5 rounded-2xl p-3 sm:p-8 shadow-2xl backdrop-blur-lg -mx-2 sm:mx-0">
          {/* Постер */}
          <img
            src={anime.poster?.mainUrl || anime.poster?.originalUrl || "/placeholder.jpg"}
            alt={anime.russian || anime.name || "Anime Poster"}
            className="w-full sm:w-72 h-auto mx-auto md:mx-0 rounded-2xl shadow-2xl object-cover transform hover:scale-105 transition duration-500"
          />

          {/* Информация */}
          <div className="flex-1 space-y-6 w-full">
            <h1 className="text-2xl sm:text-5xl font-extrabold bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent drop-shadow-lg text-center md:text-left">
              {anime.russian || "Без названия"}
            </h1>

            <p className="text-gray-400 italic text-center md:text-left text-sm sm:text-lg">
              {anime.name || "Нет английского названия"}
            </p>

            {/* Теги */}
            <div className="flex flex-wrap justify-center md:justify-start gap-2 text-sm">
              <span className="px-3 py-1.5 rounded-full bg-gradient-to-r from-green-500 to-emerald-700 shadow">
                {anime.status || "Статус неизвестен"}
              </span>
              <span className="px-3 py-1.5 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 shadow">
                ⭐ {anime.score || "N/A"}
              </span>
              <span className="px-3 py-1.5 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 shadow">
                {anime.kind || "Тип неизвестен"}
              </span>
              <span className="px-3 py-1.5 rounded-full bg-gradient-to-r from-fuchsia-500 to-purple-700 shadow">
                {anime.info?.duration ? `${anime.info.duration} мин/эп` : "—"}
              </span>
            </div>

            {/* 🎭 Жанры */}
            {anime.info?.genres?.length > 0 && (
              <div className="mt-6">
                <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                  {anime.info.genres.map((genre) => (
                    <span
                      key={genre.id}
                      className="px-3 py-1 text-sm font-medium rounded-full border border-purple-500/40 
                                bg-purple-900/20 backdrop-blur-sm text-purple-200 
                                hover:bg-purple-600/20 hover:text-pink-300 hover:border-pink-400/60 
                                shadow-[0_0_10px_rgba(168,85,247,0.3)] 
                                transition-all duration-300"
                    >
                      {genre.russian}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 📜 Описание */}
            <div
              className="prose prose-invert max-w-none bg-black/40 p-3 sm:p-6 rounded-2xl border border-white/10 shadow-lg leading-relaxed text-gray-200 text-sm sm:text-base"
              dangerouslySetInnerHTML={{
                __html:
                  anime.info?.description?.replace(/<[^>]+>/g, "").trim()
                    ? anime.info.description_html
                    : "<p>Описание отсутствует</p>",
              }}
            />
          </div>
        </div>

        {/* 🎥 Плеер Kodik */}
        <div className="-mx-2 sm:mx-0">
          <h2 className="text-xl sm:text-3xl font-bold mb-6 border-l-4 border-rose-500 pl-3">
            🎥 Смотреть аниме
          </h2>
          {anime.info.kodik_player_url !== "none" ? (
            <div className="w-full rounded-2xl overflow-hidden shadow-xl">
              <KodikPlayer src={anime.info.kodik_player_url} anime_id={anime.id} />
            </div>
          ) : (
            <h2 className="text-gray-500 italic">🎞 Видеофайл отсутствует</h2>
          )}
        </div>

        {/* 🎬 Трейлеры */}
        <div className="-mx-2 sm:mx-0">
          <h2 className="text-xl sm:text-3xl font-bold mb-6 border-l-4 border-pink-500 pl-3">
            🎬 Трейлеры
          </h2>
          {anime.info?.videos?.length > 0 ? (
            <div className="relative">
              <ArrowButton ref={prevRefVideos} side="left" />
              <ArrowButton ref={nextRefVideos} side="right" />
              <Swiper
                modules={[Navigation, FreeMode]}
                spaceBetween={10}
                slidesPerView={1.2}
                freeMode={{ enabled: true, momentum: true, momentumBounce: false }}
                breakpoints={{
                  480: { slidesPerView: 1.5 },
                  640: { slidesPerView: 2 },
                  1024: { slidesPerView: 3 },
                }}
                onBeforeInit={(swiper) => {
                  swiper.params.navigation.prevEl = prevRefVideos.current;
                  swiper.params.navigation.nextEl = nextRefVideos.current;
                }}
                onInit={(swiper) => {
                  swiper.navigation.init();
                  swiper.navigation.update();
                }}
                className="!pb-12"
              >
                {anime.info.videos.map((v) => (
                  <SwiperSlide key={v.id}>
                    <div className="overflow-hidden rounded-2xl shadow-xl bg-black/40">
                      <iframe
                        src={v.playerUrl || v.player_url}
                        title={v.name}
                        className="w-full h-40 sm:h-64 rounded-2xl transition-transform duration-500"
                        allowFullScreen
                      />
                      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-black/80 to-transparent px-3 py-2 text-sm text-gray-200">
                        {v.name}
                      </div>
                    </div>
                  </SwiperSlide>
                ))}
              </Swiper>
            </div>
          ) : (
            <p className="text-gray-500 italic">Нет трейлеров</p>
          )}
        </div>

        {/* 🖼 Скриншоты */}
        <div className="-mx-2 sm:mx-0">
          <h2 className="text-xl sm:text-3xl font-bold mb-6 border-l-4 border-purple-500 pl-3">
            🖼 Скриншоты
          </h2>
          {anime.info?.screenshots?.length > 0 ? (
            <div className="relative">
              <ArrowButton ref={prevRefScreens} side="left" />
              <ArrowButton ref={nextRefScreens} side="right" />
              <Swiper
                modules={[Navigation, FreeMode]}
                spaceBetween={8}
                slidesPerView={1.3}
                freeMode={{ enabled: true, momentum: true, momentumBounce: false }}
                breakpoints={{
                  480: { slidesPerView: 2 },
                  640: { slidesPerView: 3 },
                  1024: { slidesPerView: 4 },
                }}
                onBeforeInit={(swiper) => {
                  swiper.params.navigation.prevEl = prevRefScreens.current;
                  swiper.params.navigation.nextEl = nextRefScreens.current;
                }}
                onInit={(swiper) => {
                  swiper.navigation.init();
                  swiper.navigation.update();
                }}
                className="!pb-12"
              >
                {anime.info.screenshots.map((s, i) => (
                  <SwiperSlide key={i}>
                    <img
                      src={s.originalUrl || s.preview}
                      alt={`screenshot-${i}`}
                      className="rounded-2xl shadow-xl w-full h-36 sm:h-56 object-cover transition-transform duration-500 hover:scale-105"
                    />
                  </SwiperSlide>
                ))}
              </Swiper>
            </div>
          ) : (
            <p className="text-gray-500 italic">Нет скриншотов</p>
          )}
        </div>

        {/* 💡 Рекомендации */}
        <div className="-mx-2 sm:mx-0">
          <h2 className="text-xl sm:text-3xl font-bold mb-6 border-l-4 border-emerald-500 pl-3">
            💡 Рекомендации
          </h2>
          <RecommendationsBlock animeId={anime.shikimori_id} />
        </div>
      </div>
    </div>
  );
};

export default AnimeInfoPage;
