'use client';

import { useQuery, gql } from '@apollo/client';
import {
  Box,
  Heading,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
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
  Badge,
  HStack,
} from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const GET_OPPONENT_COMPARISON = gql`
  query GetOpponentComparison($season: String) {
    opponentComparison(season: $season) {
      opponent
      matchesPlayed
      wins
      draws
      losses
      winRatePct
      goalsFor
      goalsAgainst
      avgGoalsFor
      avgGoalsAgainst
      totalXgFor
      totalXgAgainst
      avgXgFor
      avgXgAgainst
      cleanSheets
      failedToScore
      lastPlayed
      lastResult
    }
  }
`;

interface OpponentAnalysisProps {
  season: string;
}

export default function OpponentAnalysis({ season }: OpponentAnalysisProps) {
  const { data, loading, error } = useQuery(GET_OPPONENT_COMPARISON, {
    variables: { season: season || undefined },
    skip: !season,
    errorPolicy: 'all',
  });

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
        <Text color="red.500">Error loading opponent data: {error.message}</Text>
      </Center>
    );
  }

  const opponents = data?.opponentComparison || [];

  if (opponents.length === 0) {
    return (
      <Center py={10}>
        <Text>No opponent data available</Text>
      </Center>
    );
  }

  // Top opponents by matches played
  const topOpponents = opponents.slice(0, 10);

  // Win rate analysis
  const winRateData = opponents
    .filter((o: any) => o.matchesPlayed >= 2)
    .map((o: any) => ({
      opponent: o.opponent.length > 15 ? o.opponent.substring(0, 15) + '...' : o.opponent,
      winRate: o.winRatePct,
      matches: o.matchesPlayed,
    }))
    .sort((a: any, b: any) => b.winRate - a.winRate)
    .slice(0, 10);

  // xG comparison
  const xgComparison = opponents
    .filter((o: any) => o.matchesPlayed >= 2)
    .map((o: any) => ({
      opponent: o.opponent.length > 12 ? o.opponent.substring(0, 12) + '...' : o.opponent,
      avgXgFor: o.avgXgFor,
      avgXgAgainst: o.avgXgAgainst,
    }))
    .slice(0, 10);

  // Best and worst records
  const bestRecord = opponents.reduce((best: any, current: any) => 
    current.winRatePct > (best?.winRatePct || 0) ? current : best, null);
  const worstRecord = opponents.reduce((worst: any, current: any) => 
    current.winRatePct < (worst?.winRatePct || 100) ? current : worst, null);

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Opponent Analysis: {season || 'All Seasons'}
      </Heading>

      {/* Key Metrics */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={6}>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Total Opponents</StatLabel>
          <StatNumber>{opponents.length}</StatNumber>
        </Stat>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Best Record</StatLabel>
          <StatNumber>{bestRecord?.winRatePct.toFixed(1)}%</StatNumber>
          <StatHelpText>{bestRecord?.opponent}</StatHelpText>
        </Stat>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Worst Record</StatLabel>
          <StatNumber>{worstRecord?.winRatePct.toFixed(1)}%</StatNumber>
          <StatHelpText>{worstRecord?.opponent}</StatHelpText>
        </Stat>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Avg Win Rate</StatLabel>
          <StatNumber>
            {(opponents.reduce((sum: number, o: any) => sum + o.winRatePct, 0) / opponents.length).toFixed(1)}%
          </StatNumber>
        </Stat>
      </SimpleGrid>

      {/* Charts */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={6}>
        <Box bg="white" p={6} borderRadius="md" boxShadow="sm">
          <Heading size="md" mb={4}>Win Rate by Opponent</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={winRateData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="opponent" angle={-45} textAnchor="end" height={100} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="winRate" fill="#EF0107" name="Win Rate %" />
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box bg="white" p={6} borderRadius="md" boxShadow="sm">
          <Heading size="md" mb={4}>xG Comparison</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={xgComparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="opponent" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="avgXgFor" fill="#10B981" name="Arsenal xG" />
              <Bar dataKey="avgXgAgainst" fill="#EF4444" name="Opponent xG" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>

      {/* Detailed Table */}
      <Box bg="white" p={6} borderRadius="md" boxShadow="sm">
        <Heading size="md" mb={4}>Head-to-Head Records</Heading>
        <TableContainer>
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Opponent</Th>
                <Th>Matches</Th>
                <Th>W-D-L</Th>
                <Th>Win Rate</Th>
                <Th>GF</Th>
                <Th>GA</Th>
                <Th>Avg xG For</Th>
                <Th>Avg xG Against</Th>
                <Th>Clean Sheets</Th>
                <Th>Last Result</Th>
              </Tr>
            </Thead>
            <Tbody>
              {opponents.map((opp: any, idx: number) => (
                <Tr key={idx}>
                  <Td fontWeight="medium">{opp.opponent}</Td>
                  <Td>{opp.matchesPlayed}</Td>
                  <Td>
                    <HStack spacing={1}>
                      <Badge colorScheme="green">{opp.wins}W</Badge>
                      <Badge colorScheme="yellow">{opp.draws}D</Badge>
                      <Badge colorScheme="red">{opp.losses}L</Badge>
                    </HStack>
                  </Td>
                  <Td fontWeight="bold">{opp.winRatePct.toFixed(1)}%</Td>
                  <Td>{opp.goalsFor}</Td>
                  <Td>{opp.goalsAgainst}</Td>
                  <Td>{opp.avgXgFor.toFixed(2)}</Td>
                  <Td>{opp.avgXgAgainst.toFixed(2)}</Td>
                  <Td>{opp.cleanSheets}</Td>
                  <Td>
                    <Badge
                      colorScheme={
                        opp.lastResult === 'W' ? 'green' :
                        opp.lastResult === 'D' ? 'yellow' : 'red'
                      }
                    >
                      {opp.lastResult}
                    </Badge>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
