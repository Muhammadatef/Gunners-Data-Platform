'use client';

import { useState } from 'react';
import { useQuery, gql } from '@apollo/client';
import {
  Box,
  Heading,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  Select,
  Spinner,
  Center,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
} from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, Cell } from 'recharts';
import Pitch from '@/components/Pitch';

const GET_PLAYER_STATS = gql`
  query GetPlayerStats($season: String!, $limit: Int) {
    playerStats(season: $season, limit: $limit) {
      playerName
      season
      matchesPlayed
      totalShots
      goals
      totalXg
      avgXgPerShot
      conversionPct
      shotsOnTarget
      shotAccuracyPct
      assists
      xgOverperformance
    }
  }
`;

const GET_PLAYER_SHOTS = gql`
  query GetPlayerShots($season: String!, $playerName: String!) {
    playerShots(season: $season, playerName: $playerName) {
      x
      y
      xg
      result
      playerName
    }
  }
`;

interface PlayerStatsProps {
  season: string;
}

export default function PlayerStats({ season }: PlayerStatsProps) {
  const { data, loading } = useQuery(GET_PLAYER_STATS, {
    variables: { season: season || '2024-25', limit: 20 },
    skip: !season,
  });

  const [selectedPlayer, setSelectedPlayer] = useState<string>('');

  const { data: shotsData, loading: shotsLoading } = useQuery(GET_PLAYER_SHOTS, {
    variables: { season: season || '2024-25', playerName: selectedPlayer },
    skip: !selectedPlayer || !season,
  });

  if (loading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  const players = data?.playerStats || [];
  const shots = shotsData?.playerShots || [];

  if (players.length === 0) {
    return (
      <Center py={10}>
        <Text>No player data available for this season</Text>
      </Center>
    );
  }

  const topScorer = players[0];
  const top10 = players.slice(0, 10);

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Player Statistics: {season}
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={6}>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Top Scorer</StatLabel>
          <StatNumber>{topScorer.playerName}</StatNumber>
          <Text fontSize="sm" >{topScorer.goals} goals</Text>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Highest xG</StatLabel>
          <StatNumber>{topScorer.totalXg.toFixed(1)}</StatNumber>
          <Text fontSize="sm" >{topScorer.playerName}</Text>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Most Shots</StatLabel>
          <StatNumber>{topScorer.totalShots}</StatNumber>
          <Text fontSize="sm" >{topScorer.playerName}</Text>
        </Stat>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Top Scorers</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={top10} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="playerName" type="category" width={120} />
              <Tooltip />
              <Bar dataKey="goals" fill="#EF0107" />
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>xG vs Goals</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={top10}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="playerName" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="goals" fill="#10B981" name="Goals" />
              <Bar dataKey="totalXg" fill="#9CA3AF" name="xG" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>

      <Box  p={6} borderRadius="xl"  mb={6}>
        <Heading size="md" mb={4}>Player Shot Heatmap</Heading>
        <Select
          placeholder="Select Player"
          value={selectedPlayer}
          onChange={(e) => setSelectedPlayer(e.target.value)}
          
          mb={4}
        >
          {players.map((player: any) => (
            <option key={player.playerName} value={player.playerName}>
              {player.playerName} ({player.goals} goals, {player.totalXg.toFixed(1)} xG)
            </option>
          ))}
        </Select>

        {shotsLoading ? (
          <Center py={10}>
            <Spinner size="xl" color="arsenal.500" />
          </Center>
        ) : shots.length > 0 ? (
          <Pitch shots={shots} />
        ) : selectedPlayer ? (
          <Center py={10}>
            <Text>No shots data available for this player</Text>
          </Center>
        ) : null}
      </Box>

      <Box  p={6} borderRadius="xl" >
        <Heading size="md" mb={4}>Player Performance Table</Heading>
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Player</Th>
                <Th>Shots</Th>
                <Th>Goals</Th>
                <Th>Total xG</Th>
                <Th>Avg xG</Th>
                <Th>Conversion %</Th>
                <Th>Assists</Th>
              </Tr>
            </Thead>
            <Tbody>
              {players.slice(0, 15).map((player: any, idx: number) => (
                <Tr key={idx}>
                  <Td fontWeight="medium">{player.playerName}</Td>
                  <Td>{player.totalShots}</Td>
                  <Td fontWeight="bold">{player.goals}</Td>
                  <Td>{player.totalXg.toFixed(2)}</Td>
                  <Td>{player.avgXgPerShot.toFixed(3)}</Td>
                  <Td>{player.conversionPct.toFixed(1)}%</Td>
                  <Td>{player.assists || 0}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
