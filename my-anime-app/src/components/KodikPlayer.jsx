import React, { useEffect, useRef } from "react";
import { api } from "../api/axios";

const KodikPlayer = ({ src, anime_id }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    if (!src) return;

    const iframe = iframeRef.current;
    if (!iframe) return;

    const handleLoad = () => {
      iframe.contentWindow?.postMessage(
        {
          key: "kodik_player_api",
          value: { method: "seek"},
        },
        "*"
      );
    };

    let timelineUpdate = 0

    const kodikMessageListener = async (event) => {
      if (event.data.key === "kodik_player_current_episode") {
        console.log("▶️ Плеер запущен:", event.data);
        let requestBody = {
          "seek": timelineUpdate,
          "episode": event.data.value["episode"],
          "season": event.data.value["season"],
          "translation": event.data.value["translation"],
          "anime_id": anime_id,
          "profile_id": JSON.parse(localStorage.getItem("user"))["profile"]
        }

        const getAnimeWatch = await api.get(
          `/watch-list/get-watch-anime-by-profile-id/${JSON.parse(localStorage.getItem("user"))["profile"]}/${anime_id}`
        ).catch(() => null)

        try {
          await api.post("/watch-list/create-watch-anime/", requestBody)
        } catch (error) {
          if (getAnimeWatch) {
            await api.patch(`/watch-list/update-watch-anime/${getAnimeWatch.data.id}`, requestBody)
          }
        }
        
      }
      if (event.data.key === "kodik_player_time_update") {
        timelineUpdate = event.data.value
        console.log("⏱ Текущий тайм:", timelineUpdate);
      }

      // TODO: Сделать обновление seek при перемотке. СОМНИТЕЛЬНО!
      if (event.data.key === "kodik_player_pause") {
        console.log("⏱ Таймлайн во время паузы:", timelineUpdate);
        
        let requestBody = {
          "seek": timelineUpdate,
        }
        console.log(requestBody)

        const getAnimeWatch = await api.get(
          `/watch-list/get-watch-anime-by-profile-id/${JSON.parse(localStorage.getItem("user"))["profile"]}/${anime_id}`
        ).catch(() => null)

        
        try {
          await api.patch(`/watch-list/update-watch-anime/${getAnimeWatch.data.id}`, requestBody)
        } catch (error) {
          console.log(error)
        }
      }
      if (event.data.key === "kodik_player_video_ended") {
        console.log("⏱ Видео досмотрено");
      }
    };

    iframe.addEventListener("load", handleLoad);
    if (window.addEventListener) {
      window.addEventListener('message', kodikMessageListener);
    } else {
      window.attachEvent('onmessage', kodikMessageListener);
    }

    return () => {
      // фикс: iframeRef.current уже может быть null, поэтому снимаем с локальной переменной
      iframe.removeEventListener("load", handleLoad);
      window.removeEventListener("message", kodikMessageListener);
    };
  }, [src, anime_id]);

  return (
    <div className="relative w-full h-[480px] rounded-2xl overflow-hidden shadow-2xl">
      <iframe
        ref={iframeRef}
        src={src}
        className="w-full h-full border-0 rounded-2xl"
        allow="autoplay *; fullscreen *"
        title="Kodik Player"
      />
    </div>
  );
};

export default KodikPlayer;
