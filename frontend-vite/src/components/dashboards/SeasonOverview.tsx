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
  Flex,
} from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, Cell } from 'recharts';
import { format } from 'date-fns';
import ExportButton from '../ExportButton';
import { exportSeasonSummaryToPDF, exportDataToCSV } from '@/utils/exportUtils';

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

  // Define colors first before using them
  const formColors: Record<string, string> = {
    W: '#10B981',
    D: '#F59E0B',
    L: '#EF4444',
  };

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

  const handleExportPDF = () => {
    exportSeasonSummaryToPDF({
      season: summary.season,
      played: summary.matchesPlayed,
      wins: summary.wins,
      draws: summary.draws,
      losses: summary.losses,
      win_rate: parseFloat(winRate),
      points: summary.points,
      goals_for: summary.goalsFor,
      goals_against: summary.goalsAgainst,
      goal_difference: summary.goalDifference,
      xg_for: summary.totalXgFor,
      xg_against: summary.totalXgAgainst,
    });
  };

  const handleExportCSV = () => {
    exportDataToCSV(matches, `arsenal_matches_${season}`);
  };

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">
          Season Overview: {summary.season}
        </Heading>
        <ExportButton onExportPDF={handleExportPDF} onExportCSV={handleExportCSV} />
      </Flex>

      {/* Key Metrics */}
      <SimpleGrid columns={{ base: 2, md: 5 }} spacing={4} mb={8}>
        <Stat>
          <StatLabel>Matches</StatLabel>
          <StatNumber>{summary.matchesPlayed}</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>Wins</StatLabel>
          <StatNumber>{summary.wins}</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>Win Rate</StatLabel>
          <StatNumber>{winRate}%</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>Goals For</StatLabel>
          <StatNumber>{summary.goalsFor}</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>xG For</StatLabel>
          <StatNumber>{summary.totalXgFor.toFixed(1)}</StatNumber>
        </Stat>
      </SimpleGrid>

      {/* Charts */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={8}>
        <Box p={6} borderRadius="xl">
          <Heading size="md" mb={4}>Form (Last 10)</Heading>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={formData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.7)" />
              <YAxis domain={[0, 3]} stroke="rgba(255,255,255,0.7)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0, 31, 63, 0.95)',
                  border: '1px solid rgba(239, 1, 7, 0.3)',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Bar dataKey="points" fill="#8884d8">
                {formData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box p={6} borderRadius="xl">
          <Heading size="md" mb={4}>xG Performance</Heading>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={xgTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.7)" />
              <YAxis stroke="rgba(255,255,255,0.7)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0, 31, 63, 0.95)',
                  border: '1px solid rgba(239, 1, 7, 0.3)',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Legend wrapperStyle={{ color: 'white' }} />
              <Line type="monotone" dataKey="arsenalXg" stroke="#EF0107" strokeWidth={3} name="Arsenal xG" dot={{ fill: '#EF0107', r: 4 }} />
              <Line type="monotone" dataKey="opponentXg" stroke="#9CA3AF" strokeWidth={2} name="Opponent xG" dot={{ fill: '#9CA3AF', r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>

      {/* Recent Matches Table */}
      <Box p={6} borderRadius="xl">
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
                  <Td fontWeight="medium">{match.opponent}</Td>
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
                  <Td fontWeight="semibold">{match.arsenalGoals} - {match.opponentGoals}</Td>
                  <Td fontSize="sm">{match.arsenalXg.toFixed(2)} - {match.opponentXg.toFixed(2)}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
