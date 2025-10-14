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

// 🎥 Kodik Player
import KodikPlayer from "../components/KodikPlayer";

const ArrowButton = forwardRef(({ side = "left" }, ref) => (
  <button
    ref={ref}
    className={`absolute top-1/2 -translate-y-1/2 z-10 
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
  const apiUrl = import.meta.env.VITE_API_URL;
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
        const res = await axios.get(`${apiUrl}/anime/watch-anime/${id}`);
        setAnime(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchAnime();
  }, [id]);

  if (loading) return <p className="text-center text-gray-400">⏳ Loading...</p>;
  if (!anime) return <p className="text-center text-red-500">❌ Anime not found</p>;

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0a0f1c] via-[#0f0f1f] to-black text-white">
      <div className="container mx-auto px-6 py-12 space-y-16">
        {/* Верхний блок */}
        <div className="flex flex-col md:flex-row gap-8 bg-white/5 rounded-2xl p-6 shadow-2xl backdrop-blur-lg">
          <img
            src={anime.poster?.mainUrl || anime.poster?.originalUrl || "/placeholder.jpg"}
            alt={anime.russian || anime.name || "Anime Poster"}
            className="w-72 h-auto rounded-2xl shadow-2xl object-cover transform hover:scale-105 transition duration-500"
          />
          <div className="flex-1 space-y-6">
            <h1 className="text-5xl font-extrabold bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent drop-shadow-lg">
              {anime.russian || "Без названия"}
            </h1>
            <p className="text-gray-400 italic text-lg">{anime.name || "Нет английского названия"}</p>

           {/* Теги */}
            <div className="flex gap-3 text-sm flex-wrap">
              <span className="px-4 py-1.5 rounded-full bg-gradient-to-r from-green-500 to-emerald-700 shadow">
                {anime.status || "Статус неизвестен"}
              </span>
              <span className="px-4 py-1.5 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 shadow">
                ⭐ {anime.score || "N/A"}
              </span>
              <span className="px-4 py-1.5 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 shadow">
                {anime.kind || "Неизвестный тип"}
              </span>
              <span className="px-4 py-1.5 rounded-full bg-gradient-to-r from-fuchsia-500 to-purple-700 shadow">
                {anime.info?.duration ? `${anime.info.duration} мин/эп` : "Длительность неизвестна"}
              </span>
            </div>

            {/* 🎭 Жанры */}
            {anime.info.genres?.length > 0 && (
            <div className="mt-6">
              <div className="flex flex-wrap gap-2">
                {anime.info.genres.map((genre) => (
                  <span
                    key={genre.id}
                    className="px-4 py-1.5 text-sm font-medium rounded-full border border-purple-500/40 
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

            {/* Описание */}
            <div
              className="prose prose-invert max-w-none bg-black/40 p-5 rounded-2xl border border-white/10 shadow-lg leading-relaxed text-gray-200"
              dangerouslySetInnerHTML={{
                __html:
                  anime.info?.description?.replace(/<[^>]+>/g, "").trim()
                    ? anime.info.description_html
                    : "<p>Описание отсутствует</p>",
              }}
            />
          </div>
        </div>

        {/* 🎥 Смотреть аниме */}
        <div>
          <h2 className="text-3xl font-bold mb-6 border-l-4 border-rose-500 pl-3">
            🎥 Смотреть аниме
          </h2>
          {anime.info.kodik_player_url != 'none' ? (
            <KodikPlayer src={anime.info.kodik_player_url} anime_id={anime.id} />
          ) : (
            <h2 className="text-gray-500 italic">🎞 Видеофайл отсутствует</h2>
          )}

        </div>

        {/* 🎬 Трейлеры */}
        <div>
          <h2 className="text-3xl font-bold mb-6 border-l-4 border-pink-500 pl-3">
            🎬 Трейлеры
          </h2>
          {anime.info?.videos?.length > 0 ? (
            <div className="relative">
              <ArrowButton ref={prevRefVideos} side="left" />
              <ArrowButton ref={nextRefVideos} side="right" />
              <Swiper
                modules={[Navigation]}
                spaceBetween={25}
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
                    <div className="overflow-hidden rounded-2xl shadow-xl group relative bg-black/40">
                      <iframe
                        src={v.playerUrl || v.player_url}
                        title={v.name}
                        className="w-full h-64 transition-transform duration-500 group-hover:scale-105"
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
        <div>
          <h2 className="text-3xl font-bold mb-6 border-l-4 border-purple-500 pl-3">
            🖼 Скриншоты
          </h2>
          {anime.info?.screenshots?.length > 0 ? (
            <div className="relative">
              <ArrowButton ref={prevRefScreens} side="left" />
              <ArrowButton ref={nextRefScreens} side="right" />
              <Swiper
                modules={[Navigation]}
                spaceBetween={20}
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
                      className="rounded-2xl shadow-xl w-full h-56 object-cover transition-transform duration-500 hover:scale-105"
                    />
                  </SwiperSlide>
                ))}
              </Swiper>
            </div>
          ) : (
            <p className="text-gray-500 italic">Нет скриншотов</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnimeInfoPage;
