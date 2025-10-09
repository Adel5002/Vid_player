import React, { useEffect, useRef } from "react";

const KodikPlayer = ({ src, startTime = 0 }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    if (!src) return;

    const iframe = iframeRef.current;
    if (!iframe) return;

    const handleLoad = () => {
      iframe.contentWindow?.postMessage(
        {
          key: "kodik_player_api",
          value: { method: "seek", seconds: startTime },
        },
        "*"
      );
    };

    const kodikMessageListener = (event) => {
      if (event.data.key === "kodik_player_play") {
        console.log("▶️ Плеер запущен:", event.data.value);
      }
      if (event.data.key === "kodik_player_pause") {
        console.log("⏸ Плеер на паузе:", event.data.value);
      }
      if (event.data.key === "kodik_player_time_update") {
        console.log("⏱ Текущий тайм:", event.data.value);
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
  }, [src, startTime]);

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
