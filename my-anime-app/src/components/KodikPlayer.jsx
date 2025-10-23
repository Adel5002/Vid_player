import React, { useEffect, useRef } from "react";
import Cookies from "js-cookie";
import {
  getWatchAnimeByProfile,
  createWatchAnime,
  updateWatchAnime,
} from "../api/request_to_api";

const KodikPlayer = ({ src, anime_id }) => {
  const iframeRef = useRef(null);

  const user = Cookies.get("user");
  const profile = user ? JSON.parse(user).profile : null;

  useEffect(() => {
    if (!src || !profile) return;
    const iframe = iframeRef.current;
    if (!iframe) return;

    let animeData = null;
    let timelineUpdate = 0;
    const kodik = iframe.contentWindow;

    const handleIframeLoad = async () => {
      try {
        const res = await getWatchAnimeByProfile(profile, anime_id);
        animeData = res.data;

        setTimeout(() => {
          if (!animeData) return;
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
          console.log("🎬 Перешёл на серию:", animeData.season, animeData.episode);
        }, 500);
      } catch (error) {
        console.warn("Не удалось получить данные о просмотре:", error);
      }
    };

    handleIframeLoad();

    const kodikMessageListener = async (event) => {
      if (event.data.key === "kodik_player_current_episode") {
        const requestBody = {
          seek: timelineUpdate,
          episode: event.data.value["episode"],
          season: event.data.value["season"],
          translation: event.data.value["translation"],
          anime_id: anime_id,
          profile_id: profile,
          is_disabled: false,
        };

        const getAnimeWatch = await getWatchAnimeByProfile(profile, anime_id).catch(() => null);

        try {
          await createWatchAnime(requestBody);
        } catch (error) {
          if (getAnimeWatch) {
            await updateWatchAnime(getAnimeWatch.data.id, requestBody);
          }
        }
      }

      if (event.data.key === "kodik_player_time_update") {
        timelineUpdate = event.data.value;

        if (animeData && !animeData.seekApplied) {
          kodik.postMessage(
            {
              key: "kodik_player_api",
              value: { method: "seek", seconds: animeData.seek },
            },
            "*"
          );
          animeData.seekApplied = true;
        }

        console.log("⏱ Текущее время:", timelineUpdate);
      }

      if (event.data.key === "kodik_player_pause") {
        console.log("⏸ Пауза на:", timelineUpdate);
        const requestBody = { seek: timelineUpdate };

        const getAnimeWatch = await getWatchAnimeByProfile(profile, anime_id).catch(() => null);

        try {
          await updateWatchAnime(getAnimeWatch.data.id, requestBody);
        } catch (error) {
          console.log(error);
        }
      }

      if (event.data.key === "kodik_player_video_ended") {
        console.log("✅ Видео досмотрено");
      }
    };

    window.addEventListener("message", kodikMessageListener);

    return () => {
      window.removeEventListener("message", kodikMessageListener);
    };
  }, [src, anime_id, profile]);

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
