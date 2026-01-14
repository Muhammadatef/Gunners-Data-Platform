'use client';

import { useState } from 'react';
import { useQuery, gql } from '@apollo/client';
import {
  Box,
  Heading,
  Select,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
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
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Pitch from '@/components/Pitch';

const GET_MATCH_LIST = gql`
  query GetMatchList($season: String!) {
    matchList(season: $season) {
      matchId
      matchName
      matchDate
    }
  }
`;

const GET_MATCH_SHOTS = gql`
  query GetMatchShots($matchId: String!) {
    matchShots(matchId: $matchId) {
      x
      y
      xg
      result
      playerName
      minute
      situation
      shotType
    }
  }
`;

interface MatchDetailProps {
  season: string;
}

export default function MatchDetail({ season }: MatchDetailProps) {
  const { data: matchListData, loading: matchListLoading } = useQuery(GET_MATCH_LIST, {
    variables: { season: season || '2024-25' },
    skip: !season,
  });

  const [selectedMatch, setSelectedMatch] = useState<string>('');

  const { data: shotsData, loading: shotsLoading } = useQuery(GET_MATCH_SHOTS, {
    variables: { matchId: selectedMatch },
    skip: !selectedMatch,
  });

  if (matchListLoading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  const matches = matchListData?.matchList || [];
  const shots = shotsData?.matchShots || [];

  // Filter Arsenal shots (assuming team field or player names)
  const arsenalShots = shots.filter((shot: any) => shot.playerName);

  // Prepare xG timeline data
  const xgTimeline = shots.reduce((acc: any[], shot: any) => {
    const minute = Math.floor(shot.minute / 5) * 5; // Group by 5-minute intervals
    const existing = acc.find((item) => item.minute === minute);
    if (existing) {
      existing.xg += shot.xg;
      existing.shots += 1;
    } else {
      acc.push({ minute, xg: shot.xg, shots: 1 });
    }
    return acc;
  }, []).sort((a: any, b: any) => a.minute - b.minute);

  // Shot outcomes distribution
  const outcomeCounts = shots.reduce((acc: any, shot: any) => {
    acc[shot.result] = (acc[shot.result] || 0) + 1;
    return acc;
  }, {});

  const pieData = Object.entries(outcomeCounts).map(([name, value]) => ({
    name,
    value,
  }));

  const COLORS = {
    Goal: '#10B981',
    SavedShot: '#F59E0B',
    BlockedShot: '#EF4444',
    MissedShots: '#9CA3AF',
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Match Detail: {season}
      </Heading>

      {matches.length > 0 && (
        <Box mb={6}>
          <Select
            placeholder="Select Match"
            value={selectedMatch}
            onChange={(e) => setSelectedMatch(e.target.value)}
            
            mb={4}
          >
            {matches.map((match: any) => (
              <option key={match.matchId} value={match.matchId}>
                {match.matchName} - {new Date(match.matchDate).toLocaleDateString()}
              </option>
            ))}
          </Select>
        </Box>
      )}

      {shotsLoading ? (
        <Center py={10}>
          <Spinner size="xl" color="arsenal.500" />
        </Center>
      ) : selectedMatch && arsenalShots.length > 0 ? (
        <>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={6}>
            <Stat  p={4} borderRadius="xl" >
              <StatLabel>Total Shots</StatLabel>
              <StatNumber>{arsenalShots.length}</StatNumber>
            </Stat>
            <Stat  p={4} borderRadius="xl" >
              <StatLabel>Goals</StatLabel>
              <StatNumber>
                {arsenalShots.filter((s: any) => s.result === 'Goal').length}
              </StatNumber>
            </Stat>
            <Stat  p={4} borderRadius="xl" >
              <StatLabel>Total xG</StatLabel>
              <StatNumber>
                {arsenalShots.reduce((sum: number, s: any) => sum + s.xg, 0).toFixed(2)}
              </StatNumber>
            </Stat>
          </SimpleGrid>

          <Box  p={6} borderRadius="xl"  mb={6}>
            <Heading size="md" mb={4}>Shot Map</Heading>
            <Pitch shots={arsenalShots} />
          </Box>

          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
            <Box  p={6} borderRadius="xl" >
              <Heading size="md" mb={4}>xG Timeline</Heading>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={xgTimeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="minute" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="xg" stroke="#EF0107" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Box>

            <Box  p={6} borderRadius="xl" >
              <Heading size="md" mb={4}>Shot Outcomes</Heading>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#9CA3AF'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </SimpleGrid>

          <Box  p={6} borderRadius="xl" >
            <Heading size="md" mb={4}>Shot Details</Heading>
            <TableContainer>
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>Minute</Th>
                    <Th>Player</Th>
                    <Th>Result</Th>
                    <Th>xG</Th>
                    <Th>Situation</Th>
                    <Th>Type</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {arsenalShots.slice(0, 20).map((shot: any, idx: number) => (
                    <Tr key={idx}>
                      <Td>{shot.minute}</Td>
                      <Td>{shot.playerName}</Td>
                      <Td>{shot.result}</Td>
                      <Td>{shot.xg.toFixed(3)}</Td>
                      <Td>{shot.situation || 'N/A'}</Td>
                      <Td>{shot.shotType || 'N/A'}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          </Box>
        </>
      ) : selectedMatch ? (
        <Center py={10}>
          <Text>No shots data available for this match</Text>
        </Center>
      ) : (
        <Center py={10}>
          <Text>Please select a match to view details</Text>
        </Center>
      )}
    </Box>
  );
}
