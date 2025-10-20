import React, { useState } from 'react';

export default function YearRangeSlider({ minYear = 1970, maxYear = 2030, value, onChange }) {
  const [range, setRange] = useState(value || [2000, 2025]);

  const handleChange = (index, newValue) => {
    const newRange = [...range];
    newRange[index] = Number(newValue);
    if (index === 0 && newRange[0] >= newRange[1]) newRange[0] = newRange[1] - 1;
    if (index === 1 && newRange[1] <= newRange[0]) newRange[1] = newRange[0] + 1;
    setRange(newRange);
    onChange?.(newRange);
  };

  const trackLeft = ((range[0] - minYear) / (maxYear - minYear)) * 100;
  const trackRight = ((range[1] - minYear) / (maxYear - minYear)) * 100;

  return (
    <div style={{ width: '100%', fontSize: '14px', color: '#ccc' }}>
      <label style={{ display: 'block', marginBottom: '6px', fontWeight: '500' }}>Годы выпуска</label>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '12px', color: '#aaa' }}>
        <span>{range[0]}</span>
        <span>{range[1]}</span>
      </div>

      <div style={{ position: 'relative', height: '24px' }}>
        <input
          type="range"
          min={minYear}
          max={maxYear}
          value={range[0]}
          onChange={(e) => handleChange(0, e.target.value)}
          style={{
            position: 'absolute',
            width: '100%',
            pointerEvents: 'none',
            appearance: 'none',
            height: '6px',
            background: 'transparent',
            zIndex: 2,
          }}
        />
        <input
          type="range"
          min={minYear}
          max={maxYear}
          value={range[1]}
          onChange={(e) => handleChange(1, e.target.value)}
          style={{
            position: 'absolute',
            width: '100%',
            pointerEvents: 'none',
            appearance: 'none',
            height: '6px',
            background: 'transparent',
            zIndex: 3,
          }}
        />

        <div
          style={{
            position: 'absolute',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '100%',
            height: '6px',
            background: '#333',
            borderRadius: '3px',
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: '50%',
            transform: 'translateY(-50%)',
            left: `${trackLeft}%`,
            width: `${trackRight - trackLeft}%`,
            height: '6px',
            background: 'linear-gradient(90deg, #3b82f6, #a855f7)',
            borderRadius: '3px',
          }}
        />
      </div>

      <style>{`
        input[type=range]::-webkit-slider-thumb {
          pointer-events: all;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #fff;
          border: 2px solid #3b82f6;
          cursor: pointer;
          appearance: none;
          transition: background 0.2s, transform 0.1s;
        }
        input[type=range]::-webkit-slider-thumb:hover {
          background: #a855f7;
          transform: scale(1.1);
        }
        input[type=range]::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #fff;
          border: 2px solid #3b82f6;
          cursor: pointer;
          transition: background 0.2s, transform 0.1s;
        }
        input[type=range]::-moz-range-thumb:hover {
          background: #a855f7;
          transform: scale(1.1);
        }
      `}</style>
    </div>
  );
}