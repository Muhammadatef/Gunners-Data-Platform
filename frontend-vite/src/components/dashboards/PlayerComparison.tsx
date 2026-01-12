'use client';

import { useState, useEffect } from 'react';
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
  HStack,
  Badge,
} from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const GET_PLAYER_STATS = gql`
  query GetPlayerStats($season: String!, $limit: Int) {
    playerStats(season: $season, limit: $limit) {
      playerName
      goals
      totalXg
      assists
      totalShots
      conversionPct
      shotAccuracyPct
      bigChances
      bigChanceConversionPct
      xgOverperformance
      goalsPerMatch
      xgPerMatch
    }
  }
`;

interface PlayerComparisonProps {
  season: string;
}

export default function PlayerComparison({ season }: PlayerComparisonProps) {
  const { data, loading, error } = useQuery(GET_PLAYER_STATS, {
    variables: { season: season || '2024-25', limit: 50 },
    skip: !season,
    errorPolicy: 'all',
  });

  const [player1, setPlayer1] = useState<string>('');
  const [player2, setPlayer2] = useState<string>('');

  const players = data?.playerStats || [];

  // Auto-select top 2 players if none selected
  useEffect(() => {
    if (players.length > 0 && !player1) {
      setPlayer1(players[0].playerName);
    }
    if (players.length > 1 && !player2) {
      setPlayer2(players[1].playerName);
    }
  }, [players, player1, player2]);

  if (loading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  if (error) {
    return (
      <Center py={10}>
        <Text color="red.500">Error loading player data: {error.message}</Text>
      </Center>
    );
  }

  if (players.length === 0) {
    return (
      <Center py={10}>
        <Text>No player data available</Text>
      </Center>
    );
  }

  const p1 = players.find((p: any) => p.playerName === player1);
  const p2 = players.find((p: any) => p.playerName === player2);

  // Radar chart data
  const radarData = p1 && p2 ? [
    {
      metric: 'Goals',
      [player1]: Math.min((p1.goals / Math.max(p1.goals, p2.goals, 1)) * 100, 100),
      [player2]: Math.min((p2.goals / Math.max(p1.goals, p2.goals, 1)) * 100, 100),
    },
    {
      metric: 'xG',
      [player1]: Math.min((p1.totalXg / Math.max(p1.totalXg, p2.totalXg, 1)) * 100, 100),
      [player2]: Math.min((p2.totalXg / Math.max(p1.totalXg, p2.totalXg, 1)) * 100, 100),
    },
    {
      metric: 'Assists',
      [player1]: Math.min((p1.assists / Math.max(p1.assists, p2.assists, 1)) * 100, 100),
      [player2]: Math.min((p2.assists / Math.max(p1.assists, p2.assists, 1)) * 100, 100),
    },
    {
      metric: 'Conversion %',
      [player1]: Math.min(p1.conversionPct, 100),
      [player2]: Math.min(p2.conversionPct, 100),
    },
    {
      metric: 'Accuracy %',
      [player1]: Math.min(p1.shotAccuracyPct, 100),
      [player2]: Math.min(p2.shotAccuracyPct, 100),
    },
    {
      metric: 'Big Chance %',
      [player1]: Math.min(p1.bigChanceConversionPct, 100),
      [player2]: Math.min(p2.bigChanceConversionPct, 100),
    },
  ] : [];

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Player Comparison: {season}
      </Heading>

      {/* Player Selectors */}
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mb={6}>
        <Box>
          <Text mb={2} fontWeight="medium">Player 1</Text>
          <Select
            value={player1}
            onChange={(e) => setPlayer1(e.target.value)}
            bg="white"
          >
            {players.map((p: any) => (
              <option key={p.playerName} value={p.playerName}>
                {p.playerName}
              </option>
            ))}
          </Select>
        </Box>
        <Box>
          <Text mb={2} fontWeight="medium">Player 2</Text>
          <Select
            value={player2}
            onChange={(e) => setPlayer2(e.target.value)}
            bg="white"
          >
            {players.map((p: any) => (
              <option key={p.playerName} value={p.playerName}>
                {p.playerName}
              </option>
            ))}
          </Select>
        </Box>
      </SimpleGrid>

      {p1 && p2 && (
        <>
          {/* Comparison Stats */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={6}>
            <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
              <StatLabel>Goals</StatLabel>
              <StatNumber>
                <HStack>
                  <Text color={p1.goals > p2.goals ? 'arsenal.500' : 'gray.600'}>
                    {p1.goals}
                  </Text>
                  <Text color="gray.400">vs</Text>
                  <Text color={p2.goals > p1.goals ? 'arsenal.500' : 'gray.600'}>
                    {p2.goals}
                  </Text>
                </HStack>
              </StatNumber>
            </Stat>
            <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
              <StatLabel>Total xG</StatLabel>
              <StatNumber>
                <HStack>
                  <Text color={p1.totalXg > p2.totalXg ? 'arsenal.500' : 'gray.600'}>
                    {p1.totalXg.toFixed(1)}
                  </Text>
                  <Text color="gray.400">vs</Text>
                  <Text color={p2.totalXg > p1.totalXg ? 'arsenal.500' : 'gray.600'}>
                    {p2.totalXg.toFixed(1)}
                  </Text>
                </HStack>
              </StatNumber>
            </Stat>
            <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
              <StatLabel>Assists</StatLabel>
              <StatNumber>
                <HStack>
                  <Text color={p1.assists > p2.assists ? 'arsenal.500' : 'gray.600'}>
                    {p1.assists}
                  </Text>
                  <Text color="gray.400">vs</Text>
                  <Text color={p2.assists > p1.assists ? 'arsenal.500' : 'gray.600'}>
                    {p2.assists}
                  </Text>
                </HStack>
              </StatNumber>
            </Stat>
            <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
              <StatLabel>Conversion %</StatLabel>
              <StatNumber>
                <HStack>
                  <Text color={p1.conversionPct > p2.conversionPct ? 'arsenal.500' : 'gray.600'}>
                    {p1.conversionPct.toFixed(1)}%
                  </Text>
                  <Text color="gray.400">vs</Text>
                  <Text color={p2.conversionPct > p1.conversionPct ? 'arsenal.500' : 'gray.600'}>
                    {p2.conversionPct.toFixed(1)}%
                  </Text>
                </HStack>
              </StatNumber>
            </Stat>
          </SimpleGrid>

          {/* Radar Chart */}
          <Box bg="white" p={6} borderRadius="md" boxShadow="sm" mb={6}>
            <Heading size="md" mb={4}>Performance Radar</Heading>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name={player1} dataKey={player1} stroke="#EF0107" fill="#EF0107" fillOpacity={0.6} />
                <Radar name={player2} dataKey={player2} stroke="#9CA3AF" fill="#9CA3AF" fillOpacity={0.6} />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </Box>

          {/* Side-by-Side Comparison Table */}
          <Box bg="white" p={6} borderRadius="md" boxShadow="sm">
            <Heading size="md" mb={4}>Detailed Comparison</Heading>
            <TableContainer>
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Metric</Th>
                    <Th textAlign="center">{player1}</Th>
                    <Th textAlign="center">{player2}</Th>
                    <Th textAlign="center">Winner</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td fontWeight="medium">Goals</Td>
                    <Td textAlign="center">{p1.goals}</Td>
                    <Td textAlign="center">{p2.goals}</Td>
                    <Td textAlign="center">
                      {p1.goals > p2.goals ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.goals > p1.goals ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Total xG</Td>
                    <Td textAlign="center">{p1.totalXg.toFixed(2)}</Td>
                    <Td textAlign="center">{p2.totalXg.toFixed(2)}</Td>
                    <Td textAlign="center">
                      {p1.totalXg > p2.totalXg ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.totalXg > p1.totalXg ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Goals vs xG</Td>
                    <Td textAlign="center">{p1.xgOverperformance > 0 ? '+' : ''}{p1.xgOverperformance.toFixed(2)}</Td>
                    <Td textAlign="center">{p2.xgOverperformance > 0 ? '+' : ''}{p2.xgOverperformance.toFixed(2)}</Td>
                    <Td textAlign="center">
                      {p1.xgOverperformance > p2.xgOverperformance ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.xgOverperformance > p1.xgOverperformance ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Assists</Td>
                    <Td textAlign="center">{p1.assists}</Td>
                    <Td textAlign="center">{p2.assists}</Td>
                    <Td textAlign="center">
                      {p1.assists > p2.assists ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.assists > p1.assists ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Total Shots</Td>
                    <Td textAlign="center">{p1.totalShots}</Td>
                    <Td textAlign="center">{p2.totalShots}</Td>
                    <Td textAlign="center">
                      {p1.totalShots > p2.totalShots ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.totalShots > p1.totalShots ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Conversion %</Td>
                    <Td textAlign="center">{p1.conversionPct.toFixed(1)}%</Td>
                    <Td textAlign="center">{p2.conversionPct.toFixed(1)}%</Td>
                    <Td textAlign="center">
                      {p1.conversionPct > p2.conversionPct ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.conversionPct > p1.conversionPct ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Shot Accuracy %</Td>
                    <Td textAlign="center">{p1.shotAccuracyPct.toFixed(1)}%</Td>
                    <Td textAlign="center">{p2.shotAccuracyPct.toFixed(1)}%</Td>
                    <Td textAlign="center">
                      {p1.shotAccuracyPct > p2.shotAccuracyPct ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.shotAccuracyPct > p1.shotAccuracyPct ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Big Chances</Td>
                    <Td textAlign="center">{p1.bigChances}</Td>
                    <Td textAlign="center">{p2.bigChances}</Td>
                    <Td textAlign="center">
                      {p1.bigChances > p2.bigChances ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.bigChances > p1.bigChances ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Big Chance Conversion %</Td>
                    <Td textAlign="center">{p1.bigChanceConversionPct.toFixed(1)}%</Td>
                    <Td textAlign="center">{p2.bigChanceConversionPct.toFixed(1)}%</Td>
                    <Td textAlign="center">
                      {p1.bigChanceConversionPct > p2.bigChanceConversionPct ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.bigChanceConversionPct > p1.bigChanceConversionPct ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">Goals per Match</Td>
                    <Td textAlign="center">{p1.goalsPerMatch.toFixed(2)}</Td>
                    <Td textAlign="center">{p2.goalsPerMatch.toFixed(2)}</Td>
                    <Td textAlign="center">
                      {p1.goalsPerMatch > p2.goalsPerMatch ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.goalsPerMatch > p1.goalsPerMatch ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="medium">xG per Match</Td>
                    <Td textAlign="center">{p1.xgPerMatch.toFixed(2)}</Td>
                    <Td textAlign="center">{p2.xgPerMatch.toFixed(2)}</Td>
                    <Td textAlign="center">
                      {p1.xgPerMatch > p2.xgPerMatch ? <Badge colorScheme="green">{player1}</Badge> :
                       p2.xgPerMatch > p1.xgPerMatch ? <Badge colorScheme="green">{player2}</Badge> :
                       <Badge colorScheme="gray">Tie</Badge>}
                    </Td>
                  </Tr>
                </Tbody>
              </Table>
            </TableContainer>
          </Box>
        </>
      )}
    </Box>
  );
}
