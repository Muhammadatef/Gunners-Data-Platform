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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
} from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const GET_PLAYER_XT_STATS = gql`
  query GetPlayerXTStats($season: String!, $limit: Int) {
    playerXTStats(season: $season, limit: $limit) {
      playerName
      positionCategory
      season
      totalShots
      goals
      totalXt
      avgXtPerShot
      maxXtShot
      totalXg
      avgXgPerShot
      highThreatShots
      highThreatPct
      xtEfficiency
    }
  }
`;

interface ExpectedThreatProps {
  season: string;
}

export default function ExpectedThreat({ season }: ExpectedThreatProps) {
  const { data, loading } = useQuery(GET_PLAYER_XT_STATS, {
    variables: { season: season || '2024-25', limit: 20 },
    skip: !season,
  });

  if (loading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  const players = data?.playerXTStats || [];

  if (players.length === 0) {
    return (
      <Center py={10}>
        <Text>No xT data available for this season</Text>
      </Center>
    );
  }

  const top3 = players.slice(0, 3);
  const top10 = players.slice(0, 10);

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Expected Threat (xT): {season}
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={6}>
        {top3.map((player: any, idx: number) => (
          <Stat key={idx}  p={4} borderRadius="xl" >
            <StatLabel>
              {idx === 0 && '🥇 '}
              {idx === 1 && '🥈 '}
              {idx === 2 && '🥉 '}
              {player.playerName}
            </StatLabel>
            <StatNumber>{player.totalXt.toFixed(1)} xT</StatNumber>
            <Text fontSize="sm" >{player.totalShots} shots</Text>
          </Stat>
        ))}
      </SimpleGrid>

      <Box  p={6} borderRadius="xl"  mb={6}>
        <Heading size="md" mb={4}>xT Leaders</Heading>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={top10} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="playerName" type="category" width={120} />
            <Tooltip />
            <Bar dataKey="totalXt" fill="#EF0107" />
          </BarChart>
        </ResponsiveContainer>
      </Box>

      <Box  p={6} borderRadius="xl" >
        <Heading size="md" mb={4}>Player xT Statistics</Heading>
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Player</Th>
                <Th>Shots</Th>
                <Th>Goals</Th>
                <Th>Total xT</Th>
                <Th>Avg xT</Th>
                <Th>High Threat %</Th>
              </Tr>
            </Thead>
            <Tbody>
              {players.map((player: any, idx: number) => (
                <Tr key={idx}>
                  <Td fontWeight="medium">{player.playerName}</Td>
                  <Td>{player.totalShots}</Td>
                  <Td>{player.goals}</Td>
                  <Td>{player.totalXt.toFixed(2)}</Td>
                  <Td>{player.avgXtPerShot.toFixed(3)}</Td>
                  <Td>{player.highThreatPct.toFixed(1)}%</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
