import React, { useState } from "react";

export default function YearRangeSlider({
  minYear = 1970,
  maxYear = 2030,
  value,
  onChange,
}) {
  const [range, setRange] = useState(value || [2000, 2025]);
  const [isDragging, setIsDragging] = useState(false);

  const handleChange = (index, newValue) => {
    const newRange = [...range];
    newRange[index] = Number(newValue);
    if (index === 0 && newRange[0] >= newRange[1]) newRange[0] = newRange[1] - 1;
    if (index === 1 && newRange[1] <= newRange[0]) newRange[1] = newRange[0] + 1;
    setRange(newRange);
    onChange?.(newRange);
  };

  const handleStart = () => setIsDragging(true);
  const handleEnd = () => setIsDragging(false);

  const trackLeft = ((range[0] - minYear) / (maxYear - minYear)) * 100;
  const trackRight = ((range[1] - minYear) / (maxYear - minYear)) * 100;

  return (
    <div className="flex flex-col text-sm justify-end w-full">
      <label className="text-gray-300 mb-2 font-medium flex items-center gap-2">
        <span>📅</span> Годы выпуска
      </label>

      {/* Значения лет */}
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{range[0]}</span>
        <span>{range[1]}</span>
      </div>

      {/* Слайдер */}
      <div className="relative flex items-center h-[28px]">
        <input
          type="range"
          min={minYear}
          max={maxYear}
          value={range[0]}
          onChange={(e) => handleChange(0, e.target.value)}
          onMouseDown={handleStart}
          onMouseUp={handleEnd}
          onTouchStart={handleStart}
          onTouchEnd={handleEnd}
          className="absolute w-full z-[3] bg-transparent pointer-events-none appearance-none"
        />
        <input
          type="range"
          min={minYear}
          max={maxYear}
          value={range[1]}
          onChange={(e) => handleChange(1, e.target.value)}
          onMouseDown={handleStart}
          onMouseUp={handleEnd}
          onTouchStart={handleStart}
          onTouchEnd={handleEnd}
          className="absolute w-full z-[4] bg-transparent pointer-events-none appearance-none"
        />

        {/* Трек */}
        <div className="absolute top-1/2 -translate-y-1/2 w-full h-[6px] rounded-full bg-white/10" />
        <div
          className={`absolute top-1/2 -translate-y-1/2 h-[6px] rounded-full ${
            !isDragging ? "transition-all duration-200" : ""
          }`}
          style={{
            left: `${trackLeft}%`,
            width: `${trackRight - trackLeft}%`,
            background: "linear-gradient(90deg, #3b82f6, #a855f7)",
            boxShadow: "0 0 8px rgba(168,85,247,0.6)",
          }}
        />
      </div>

      {/* CSS для ползунков */}
      <style>{`
        input[type=range]::-webkit-slider-thumb {
          pointer-events: all;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #fff;
          border: 2px solid #a855f7;
          cursor: pointer;
          appearance: none;
          box-shadow: 0 0 6px rgba(168, 85, 247, 0.5);
          transition: transform 0.15s ease, background 0.2s ease;
        }
        input[type=range]::-webkit-slider-thumb:hover {
          background: #a855f7;
          transform: scale(1.15);
        }

        input[type=range]::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #fff;
          border: 2px solid #a855f7;
          cursor: pointer;
          box-shadow: 0 0 6px rgba(168, 85, 247, 0.5);
          transition: transform 0.15s ease, background 0.2s ease;
        }
        input[type=range]::-moz-range-thumb:hover {
          background: #a855f7;
          transform: scale(1.15);
        }

        input[type=range]::-moz-range-track {
          background: transparent;
        }

        input[type=range]:focus::-webkit-slider-thumb {
          box-shadow: 0 0 10px rgba(59, 130, 246, 0.7);
        }
      `}</style>
    </div>
  );
}
