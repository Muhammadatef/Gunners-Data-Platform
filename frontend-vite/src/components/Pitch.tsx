'use client';

import { Box } from '@chakra-ui/react';

interface Shot {
  x: number;
  y: number;
  xg: number;
  result: string;
  playerName?: string;
}

interface PitchProps {
  shots: Shot[];
  width?: number;
  height?: number;
}

export default function Pitch({ shots, width = 800, height = 500 }: PitchProps) {
  const goalWidth = 0.17; // Width of goal area (normalized)
  const goalHeight = 0.56; // Height of goal area (normalized)
  const centerY = 0.5;

  const getShotColor = (result: string) => {
    switch (result) {
      case 'Goal':
        return '#10B981';
      case 'SavedShot':
        return '#F59E0B';
      case 'BlockedShot':
        return '#EF4444';
      case 'MissedShots':
        return '#9CA3AF';
      default:
        return '#6B7280';
    }
  };

  const getShotSymbol = (result: string) => {
    switch (result) {
      case 'Goal':
        return '★';
      case 'SavedShot':
        return '●';
      case 'BlockedShot':
        return '✕';
      case 'MissedShots':
        return '○';
      default:
        return '●';
    }
  };

  return (
    <Box position="relative" width={`${width}px`} height={`${height}px`} mx="auto">
      <svg width={width} height={height} style={{ background: '#F0FDF4' }}>
        {/* Pitch outline */}
        <rect
          x={0}
          y={0}
          width={width}
          height={height}
          fill="#F0FDF4"
          stroke="#E5E7EB"
          strokeWidth={2}
        />

        {/* Center line */}
        <line
          x1={width / 2}
          y1={0}
          x2={width / 2}
          y2={height}
          stroke="#E5E7EB"
          strokeWidth={2}
        />

        {/* Center circle */}
        <circle
          cx={width / 2}
          cy={height / 2}
          r={width * 0.1}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={2}
        />

        {/* Left penalty box */}
        <rect
          x={0}
          y={height * (1 - goalHeight) / 2}
          width={width * goalWidth}
          height={height * goalHeight}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={2}
        />

        {/* Right penalty box */}
        <rect
          x={width * (1 - goalWidth)}
          y={height * (1 - goalHeight) / 2}
          width={width * goalWidth}
          height={height * goalHeight}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={2}
        />

        {/* Shots */}
        {shots.map((shot, idx) => {
          const x = shot.x * width;
          const y = shot.y * height;
          const size = Math.max(15, shot.xg * 100 + 10);
          const color = getShotColor(shot.result);

          return (
            <g key={idx}>
              <circle
                cx={x}
                cy={y}
                r={size / 2}
                fill={color}
                stroke="white"
                strokeWidth={2}
                opacity={0.8}
              />
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="white"
                fontSize={size * 0.4}
                fontWeight="bold"
              >
                {getShotSymbol(shot.result)}
              </text>
              {shot.playerName && (
                <title>{shot.playerName} - xG: {shot.xg.toFixed(2)}</title>
              )}
            </g>
          );
        })}
      </svg>
    </Box>
  );
}
