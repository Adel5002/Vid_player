import React, { useEffect, useState, useRef, forwardRef } from "react";
import { api } from "../api/axios";

// Swiper
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, FreeMode } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/free-mode";

// Icons
import { ChevronLeft, ChevronRight } from "lucide-react";

// 🎯 Универсальная кнопка со стрелкой
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

/**
 * 💡 RecommendationsBlock
 * Отображает похожие аниме с постерами, оценками и плавной прокруткой.
 *
 * @param {number} animeId - ID текущего аниме (shikimori_id)
 */
const RecommendationsBlock = ({ animeId }) => {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const prevRefRecs = useRef(null);
  const nextRefRecs = useRef(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const { data } = await api.get(`/anime/${animeId}/recommendations`);
        const ids = data.recommendations || [];
        const detailed = [];

        for (const id of ids) {
          try {
            const res = await api.get(`/anime/${id}`);
            detailed.push(res.data);
          } catch (err) {
            console.warn("⚠️ Ошибка загрузки аниме:", id, err);
          }
        }

        setRecs(detailed);
      } catch (err) {
        console.error("❌ Ошибка загрузки рекомендаций:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [animeId]);

  if (loading)
    return (
      <p className="text-gray-400 italic">⏳ Загрузка рекомендаций...</p>
    );

  if (!recs.length)
    return (
      <p className="text-gray-500 italic">😔 Рекомендации отсутствуют</p>
    );

  return (
    <div className="relative">
      <ArrowButton ref={prevRefRecs} side="left" />
      <ArrowButton ref={nextRefRecs} side="right" />

      <Swiper
        modules={[Navigation, FreeMode]}
        spaceBetween={12}
        slidesPerView={1.3}
        freeMode={{ enabled: true, momentum: true, momentumBounce: false }}
        breakpoints={{
          480: { slidesPerView: 2 },
          640: { slidesPerView: 3 },
          1024: { slidesPerView: 4 },
        }}
        onBeforeInit={(swiper) => {
          swiper.params.navigation.prevEl = prevRefRecs.current;
          swiper.params.navigation.nextEl = nextRefRecs.current;
        }}
        onInit={(swiper) => {
          swiper.navigation.init();
          swiper.navigation.update();
        }}
        className="!pb-12"
      >
        {recs.map((item) => (
          <SwiperSlide key={item.shikimori_id}>
            <a
              href={`/anime/${item.shikimori_id}`}
              className="block rounded-2xl overflow-hidden bg-white/5 hover:bg-white/10 
                         transition-all duration-300 shadow-lg hover:shadow-pink-500/20"
            >
              <div className="relative">
                <img
                  src={
                    item.poster?.mainUrl ||
                    item.poster?.originalUrl ||
                    "/placeholder.jpg"
                  }
                  alt={item.russian || item.name}
                  className="w-full h-52 object-cover transition-transform duration-500 hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-70" />
                <div className="absolute bottom-0 p-3">
                  <h3 className="text-sm sm:text-base font-semibold text-white line-clamp-2 drop-shadow-lg">
                    {item.russian || item.name}
                  </h3>
                  <p className="text-xs text-gray-300">
                    ⭐ {item.score || "N/A"} | {item.kind || "?"}
                  </p>
                </div>
              </div>
            </a>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};

export default RecommendationsBlock;
