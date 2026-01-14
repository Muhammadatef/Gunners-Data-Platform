'use client';

import { useQuery, gql } from '@apollo/client';
import {
  Box,
  Heading,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  Spinner,
  Center,
  Text,
} from '@chakra-ui/react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

const GET_TACTICAL_ANALYSIS = gql`
  query GetTacticalAnalysis($season: String!) {
    tacticalAnalysis(season: $season) {
      season
      arsenalShots0_15
      arsenalShots16_30
      arsenalShots31_45
      arsenalShots46_60
      arsenalShots61_75
      arsenalShots76_90
      arsenalGoals0_15
      arsenalGoals16_30
      arsenalGoals31_45
      arsenalGoals46_60
      arsenalGoals61_75
      arsenalGoals76_90
      shotsFromPass
      shotsFromDribble
      shotsFromRebound
      shotsFromChip
      shotsFromCross
      openPlayTotal
      openPlayGoals
      openPlayXg
      cornerTotal
      cornerGoals
      cornerXg
      setPieceTotal
      setPieceGoals
      setPieceXg
      penaltyTotal
      penaltyGoals
      bigChancesCreated
      bigChancesConverted
    }
  }
`;

const GET_MATCH_SHOTS = gql`
  query GetMatchShotsBySeason($season: String!, $team: String) {
    matchShotsBySeason(season: $season, team: $team) {
      x
      y
      xg
      result
    }
  }
`;

interface TacticalAnalysisProps {
  season: string;
}

export default function TacticalAnalysis({ season }: TacticalAnalysisProps) {
  const { data: tacticalData, loading: tacticalLoading } = useQuery(GET_TACTICAL_ANALYSIS, {
    variables: { season: season || '2024-25' },
    skip: !season,
  });

  const { data: shotsData, loading: shotsLoading } = useQuery(GET_MATCH_SHOTS, {
    variables: { season: season || '2024-25', team: 'Arsenal' },
    skip: !season,
  });

  if (tacticalLoading || shotsLoading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  const tactical = tacticalData?.tacticalAnalysis;
  const shots = shotsData?.matchShotsBySeason || [];

  if (!tactical) {
    return (
      <Center py={10}>
        <Text>No tactical data available for this season</Text>
      </Center>
    );
  }

  const totalShots = shots.length;
  const goals = shots.filter((s: any) => s.result === 'Goal').length;
  const conversion = totalShots > 0 ? (goals / totalShots * 100).toFixed(1) : '0.0';
  const avgXg = shots.length > 0
    ? (shots.reduce((sum: number, s: any) => sum + s.xg, 0) / shots.length).toFixed(3)
    : '0.000';

  // Shot timing data
  const timingData = [
    { period: '0-15', shots: tactical.arsenalShots0_15, goals: tactical.arsenalGoals0_15 },
    { period: '16-30', shots: tactical.arsenalShots16_30, goals: tactical.arsenalGoals16_30 },
    { period: '31-45', shots: tactical.arsenalShots31_45, goals: tactical.arsenalGoals31_45 },
    { period: '46-60', shots: tactical.arsenalShots46_60, goals: tactical.arsenalGoals46_60 },
    { period: '61-75', shots: tactical.arsenalShots61_75, goals: tactical.arsenalGoals61_75 },
    { period: '76-90', shots: tactical.arsenalShots76_90, goals: tactical.arsenalGoals76_90 },
  ];

  // Shot outcomes
  const outcomeCounts = shots.reduce((acc: any, shot: any) => {
    acc[shot.result] = (acc[shot.result] || 0) + 1;
    return acc;
  }, {});

  const outcomeData = Object.entries(outcomeCounts).map(([name, value]) => ({
    name,
    value,
  }));

  const COLORS = {
    Goal: '#10B981',
    SavedShot: '#F59E0B',
    BlockedShot: '#EF4444',
    MissedShots: '#9CA3AF',
  };

  // xG distribution
  const xgBins = Array.from({ length: 20 }, (_, i) => ({
    range: `${(i * 0.05).toFixed(2)}-${((i + 1) * 0.05).toFixed(2)}`,
    count: 0,
  }));

  shots.forEach((shot: any) => {
    const binIndex = Math.min(Math.floor(shot.xg / 0.05), 19);
    xgBins[binIndex].count++;
  });

  // Situation effectiveness
  const situationData = [
    {
      name: 'Open Play',
      total: tactical.openPlayTotal,
      goals: tactical.openPlayGoals,
      xg: tactical.openPlayXg,
    },
    {
      name: 'Corner',
      total: tactical.cornerTotal,
      goals: tactical.cornerGoals,
      xg: tactical.cornerXg,
    },
    {
      name: 'Set Piece',
      total: tactical.setPieceTotal,
      goals: tactical.setPieceGoals,
      xg: tactical.setPieceXg,
    },
    {
      name: 'Penalty',
      total: tactical.penaltyTotal,
      goals: tactical.penaltyGoals,
      xg: 0,
    },
  ];

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Tactical Analysis: {season}
      </Heading>

      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={6}>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Total Shots</StatLabel>
          <StatNumber>{totalShots}</StatNumber>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Goals</StatLabel>
          <StatNumber>{goals}</StatNumber>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Conversion %</StatLabel>
          <StatNumber>{conversion}%</StatNumber>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Avg xG/Shot</StatLabel>
          <StatNumber>{avgXg}</StatNumber>
        </Stat>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Shot Outcomes</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={outcomeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {outcomeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#9CA3AF'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Box>

        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Shot Timing by Period</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={timingData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="shots" fill="#EF0107" name="Shots" />
              <Bar dataKey="goals" fill="#10B981" name="Goals" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>xG Distribution</Heading>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={xgBins}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#EF0107" />
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Situation Effectiveness</Heading>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={situationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="total" fill="#9CA3AF" name="Total Shots" />
              <Bar dataKey="goals" fill="#10B981" name="Goals" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>
    </Box>
  );
}
