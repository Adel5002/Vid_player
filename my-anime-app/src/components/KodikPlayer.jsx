import React, { useEffect, useRef } from "react";
import { api } from "../api/axios";

const KodikPlayer = ({ src, anime_id }) => {
  const iframeRef = useRef(null);
  const profile = JSON.parse(localStorage.getItem("user"))?.profile

  useEffect(() => {
    if (!src) return;
    const iframe = iframeRef.current;
    if (!iframe) return;

    let animeData = null;

    api.get(
        `/watch-list/get-watch-anime-by-profile-id/${
          profile
        }/${anime_id}`
      )
      .then((res) => {
        animeData = res.data;
      })
      .catch(() => null);

     const handleIframeLoad = () => {
      if (!animeData) return; // ещё не пришли данные
      const kodik = iframe.contentWindow;
      if (!kodik) return;

      // Немного подождать, чтобы плеер инициализировался
      setTimeout(() => {
        kodik.postMessage(
          {
            key: "kodik_player_api",
            value: {
              method: "change_episode",
              season: animeData.season,
              episode: animeData.episode,
            },
          },
          "*"
        );
      }, 500);
    };

    iframe.addEventListener("load", handleIframeLoad);

    let timelineUpdate = 0

    const kodikMessageListener = async (event) => {
      if (event.data.key === "kodik_player_current_episode") {
      
        let requestBody = {
          "seek": timelineUpdate,
          "episode": event.data.value["episode"],
          "season": event.data.value["season"],
          "translation": event.data.value["translation"],
          "anime_id": anime_id,
          "profile_id": profile,
          "is_disabled": false
        }

        const getAnimeWatch = await api.get(
          `/watch-list/get-watch-anime-by-profile-id/${profile}/${anime_id}`
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
        timelineUpdate = event.data.value;

        
        if (animeData && !animeData.seekApplied) {
          const kodik = iframeRef.current?.contentWindow;
          if (kodik) {
            kodik.postMessage(
              {
                key: "kodik_player_api",
                value: { method: "seek", seconds: animeData.seek },
              },
              "*"
            );
            animeData.seekApplied = true; // чтобы не делать повторно
          }
        }

        console.log("⏱ Текущий тайм:", timelineUpdate);
      }
      
      if (event.data.key === "kodik_player_pause") {
        console.log("⏱ Таймлайн во время паузы:", timelineUpdate);
        
        let requestBody = {
          "seek": timelineUpdate,
        }
        console.log(requestBody)

        const getAnimeWatch = await api.get(
          `/watch-list/get-watch-anime-by-profile-id/${profile}/${anime_id}`
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

    if (window.addEventListener) {
      window.addEventListener('message', kodikMessageListener);
    } else {
      window.attachEvent('onmessage', kodikMessageListener);
    }

    return () => {
      // фикс: iframeRef.current уже может быть null, поэтому снимаем с локальной переменной
      iframe.removeEventListener("load", handleIframeLoad);
      window.removeEventListener("message", kodikMessageListener);
    };
  }, []);

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
