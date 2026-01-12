'use client';

import { useQuery, gql } from '@apollo/client';
import {
  Box,
  Stat,
  StatLabel,
  StatNumber,
  SimpleGrid,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Spinner,
  Center,
  Text,
} from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, Cell } from 'recharts';
import { format } from 'date-fns';

const GET_SEASON_SUMMARY = gql`
  query GetSeasonSummary($season: String!) {
    seasonSummary(season: $season) {
      season
      matchesPlayed
      wins
      draws
      losses
      points
      goalsFor
      goalsAgainst
      goalDifference
      totalXgFor
      totalXgAgainst
      avgXgPerMatch
      totalXgOverperformance
      homeMatches
      awayMatches
      homeWins
      awayWins
    }
  }
`;

const GET_MATCHES = gql`
  query GetMatches($season: String!) {
    matches(season: $season, limit: 20) {
      matchDate
      opponent
      venue
      result
      arsenalGoals
      opponentGoals
      arsenalXg
      opponentXg
    }
  }
`;

interface SeasonOverviewProps {
  season: string;
}

export default function SeasonOverview({ season }: SeasonOverviewProps) {
  const { data: summaryData, loading: summaryLoading } = useQuery(GET_SEASON_SUMMARY, {
    variables: { season: season || '2024-25' },
    skip: !season,
  });

  const { data: matchesData, loading: matchesLoading } = useQuery(GET_MATCHES, {
    variables: { season: season || '2024-25' },
    skip: !season,
  });

  if (summaryLoading || matchesLoading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  const summary = summaryData?.seasonSummary;
  const matches = matchesData?.matches || [];

  if (!summary) {
    return (
      <Center py={10}>
        <Text>No data available for this season</Text>
      </Center>
    );
  }

  const winRate = summary.matchesPlayed > 0
    ? ((summary.wins / summary.matchesPlayed) * 100).toFixed(1)
    : '0.0';

  // Prepare form chart data (last 10 matches)
  const formData = matches.slice(0, 10).reverse().map((match: any) => ({
    date: format(new Date(match.matchDate), 'MMM d'),
    points: match.result === 'W' ? 3 : match.result === 'D' ? 1 : 0,
    result: match.result,
    color: formColors[match.result] || '#9CA3AF',
  }));

  // Prepare xG trend data
  const xgTrendData = matches.slice(0, 10).reverse().map((match: any) => ({
    date: format(new Date(match.matchDate), 'MMM d'),
    arsenalXg: parseFloat(match.arsenalXg.toFixed(2)),
    opponentXg: parseFloat(match.opponentXg.toFixed(2)),
  }));

  const formColors: Record<string, string> = {
    W: '#10B981',
    D: '#F59E0B',
    L: '#EF4444',
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Season Overview: {summary.season}
      </Heading>

      {/* Key Metrics */}
      <SimpleGrid columns={{ base: 2, md: 5 }} spacing={4} mb={8}>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Matches</StatLabel>
          <StatNumber>{summary.matchesPlayed}</StatNumber>
        </Stat>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Wins</StatLabel>
          <StatNumber>{summary.wins}</StatNumber>
        </Stat>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Win Rate</StatLabel>
          <StatNumber>{winRate}%</StatNumber>
        </Stat>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>Goals For</StatLabel>
          <StatNumber>{summary.goalsFor}</StatNumber>
        </Stat>
        <Stat bg="white" p={4} borderRadius="md" boxShadow="sm">
          <StatLabel>xG For</StatLabel>
          <StatNumber>{summary.totalXgFor.toFixed(1)}</StatNumber>
        </Stat>
      </SimpleGrid>

      {/* Charts */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={8}>
        <Box bg="white" p={6} borderRadius="md" boxShadow="sm">
          <Heading size="md" mb={4}>Form (Last 10)</Heading>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={formData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 3]} />
              <Tooltip />
              <Bar dataKey="points" fill="#8884d8">
                {formData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box bg="white" p={6} borderRadius="md" boxShadow="sm">
          <Heading size="md" mb={4}>xG Performance</Heading>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={xgTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="arsenalXg" stroke="#EF0107" strokeWidth={2} name="Arsenal xG" />
              <Line type="monotone" dataKey="opponentXg" stroke="#9CA3AF" strokeWidth={2} name="Opponent xG" />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>

      {/* Recent Matches Table */}
      <Box bg="white" p={6} borderRadius="md" boxShadow="sm">
        <Heading size="md" mb={4}>Recent Matches</Heading>
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Date</Th>
                <Th>Opponent</Th>
                <Th>Venue</Th>
                <Th>Result</Th>
                <Th>Score</Th>
                <Th>xG</Th>
              </Tr>
            </Thead>
            <Tbody>
              {matches.slice(0, 10).map((match: any, idx: number) => (
                <Tr key={idx}>
                  <Td>{format(new Date(match.matchDate), 'MMM d, yyyy')}</Td>
                  <Td>{match.opponent}</Td>
                  <Td>{match.venue}</Td>
                  <Td>
                    <Box
                      as="span"
                      px={2}
                      py={1}
                      borderRadius="md"
                      bg={formColors[match.result] || '#9CA3AF'}
                      color="white"
                      fontSize="sm"
                      fontWeight="bold"
                    >
                      {match.result}
                    </Box>
                  </Td>
                  <Td>{match.arsenalGoals} - {match.opponentGoals}</Td>
                  <Td>{match.arsenalXg.toFixed(2)} - {match.opponentXg.toFixed(2)}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
