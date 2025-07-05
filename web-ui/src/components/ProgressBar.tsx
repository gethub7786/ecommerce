import React from 'react';

export default function ProgressBar({ percent }: { percent: number }) {
  return (
    <div className="w-40 h-3 bg-gray-200 rounded-full overflow-hidden">
      <div
        className="h-full bg-blue-500 transition-all duration-300"
        style={{ width: `${Math.max(0, Math.min(percent, 100))}%` }}
      />
    </div>
  );
}
