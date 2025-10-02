import React, { useEffect, useState, useRef, forwardRef } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

// Swiper
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";

// Icons
import { ChevronLeft, ChevronRight } from "lucide-react";

const ArrowButton = forwardRef(({ side = "left" }, ref) => (
  <button
    ref={ref}
    className={`absolute top-1/2 -translate-y-1/2 z-10 
      bg-black/40 hover:bg-black/70 p-2 rounded-full transition-colors
      ${side === "left" ? "left-2" : "right-2"}`}
    aria-label={side === "left" ? "Previous" : "Next"}
  >
    {side === "left" ? (
      <ChevronLeft className="w-6 h-6 text-white" />
    ) : (
      <ChevronRight className="w-6 h-6 text-white" />
    )}
  </button>
));
ArrowButton.displayName = "ArrowButton";

const AnimeInfoPage = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const { id } = useParams();
  const [anime, setAnime] = useState(null);
  const [loading, setLoading] = useState(true);

  // refs для трейлеров
  const prevRefVideos = useRef(null);
  const nextRefVideos = useRef(null);

  // refs для скриншотов
  const prevRefScreens = useRef(null);
  const nextRefScreens = useRef(null);

  useEffect(() => {
    const fetchAnime = async () => {
      try {
        const res = await axios.get(`${apiUrl}/anime/anime-watch/${id}`);
        setAnime(res.data);
      } catch (e) {
        console.error(e);
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

        {/* Трейлеры */}
        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">🎬 Трейлеры</h2>
          {anime.info?.videos?.length > 0 ? (
            <div className="relative">
              <ArrowButton ref={prevRefVideos} side="left" />
              <ArrowButton ref={nextRefVideos} side="right" />

              <Swiper
                modules={[Navigation]}
                spaceBetween={20}
                slidesPerView={1}
                breakpoints={{
                  640: { slidesPerView: 1 },
                  768: { slidesPerView: 2 },
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
                    <div className="overflow-hidden rounded-2xl shadow-xl group relative">
                      <iframe
                        src={v.playerUrl || v.player_url}
                        title={v.name}
                        className="w-full h-64 transition-transform duration-300 group-hover:scale-105"
                        allowFullScreen
                      />
                      <div className="absolute bottom-0 left-0 w-full bg-black/60 text-sm px-3 py-2">
                        {v.name}
                      </div>
                    </div>
                  </SwiperSlide>
                ))}
              </Swiper>
            </div>
          ) : (
            <p className="text-gray-500">Нет трейлеров</p>
          )}
        </div>

        {/* Скриншоты */}
        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">🖼 Скриншоты</h2>
          {anime.info?.screenshots?.length > 0 ? (
            <div className="relative">
              <ArrowButton ref={prevRefScreens} side="left" />
              <ArrowButton ref={nextRefScreens} side="right" />

              <Swiper
                modules={[Navigation]}
                spaceBetween={15}
                slidesPerView={1.2}
                breakpoints={{
                  640: { slidesPerView: 2 },
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
                      className="rounded-xl shadow-lg w-full h-52 object-cover transition-transform duration-300 hover:scale-105"
                    />
                  </SwiperSlide>
                ))}
              </Swiper>
            </div>
          ) : (
            <p className="text-gray-500">Нет скриншотов</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnimeInfoPage;
