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
  StatHelpText,
  Spinner,
  Center,
  Text,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  VStack,
  HStack,
  Badge,
  Divider,
} from '@chakra-ui/react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { format } from 'date-fns';

const GET_MATCH_LIST = gql`
  query GetMatchList($season: String!) {
    matchList(season: $season) {
      matchId
      matchName
      matchDate
    }
  }
`;

const GET_MATCH_ADVANCED_STATS = gql`
  query GetMatchAdvancedStats($matchId: String!) {
    matchAdvancedStats(matchId: $matchId) {
      matchUrl
      matchDate
      opponent
      venue
      result
      arsenalGoals
      opponentGoals
      arsenalXg
      opponentXg
      arsenalShots
      opponentShots
      arsenalShotsOnTarget
      opponentShotsOnTarget
      arsenalShotAccuracyPct
      arsenalBigChances
      arsenalBigChancesScored
      arsenalBoxShots
      arsenalOutsideBoxShots
      arsenalFirstHalfShots
      arsenalFirstHalfXg
      arsenalSecondHalfShots
      arsenalSecondHalfXg
      arsenalAvgShotXg
      opponentAvgShotXg
    }
  }
`;

const GET_MATCH_SHOTS = gql`
  query GetMatchShots($matchId: String!) {
    matchShots(matchId: $matchId) {
      minute
      result
      xg
      playerName
      situation
    }
  }
`;

interface MatchInsightsProps {
  season: string;
}

export default function MatchInsights({ season }: MatchInsightsProps) {
  const { data: matchListData, loading: matchListLoading, error: matchListError } = useQuery(GET_MATCH_LIST, {
    variables: { season: season || '2024-25' },
    skip: !season,
    errorPolicy: 'all',
  });

  const [selectedMatch, setSelectedMatch] = useState<string>('');

  const { data: statsData, loading: statsLoading, error: statsError } = useQuery(GET_MATCH_ADVANCED_STATS, {
    variables: { matchId: selectedMatch },
    skip: !selectedMatch,
    errorPolicy: 'all',
  });

  const { data: shotsData, loading: shotsLoading, error: shotsError } = useQuery(GET_MATCH_SHOTS, {
    variables: { matchId: selectedMatch },
    skip: !selectedMatch,
    errorPolicy: 'all',
  });

  if (matchListLoading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  if (matchListError) {
    return (
      <Center py={10}>
        <Text color="red.500">Error loading matches: {matchListError.message}</Text>
      </Center>
    );
  }

  const matches = matchListData?.matchList || [];
  const stats = statsData?.matchAdvancedStats;
  const shots = shotsData?.matchShots || [];

  // Generate insights
  const insights = [];
  if (stats) {
    // xG performance insight
    const xgDiff = stats.arsenalGoals - stats.arsenalXg;
    if (xgDiff > 0.5) {
      insights.push({
        type: 'success',
        title: 'Clinical Finishing',
        description: `Scored ${stats.arsenalGoals} goals from ${stats.arsenalXg.toFixed(2)} xG (+${xgDiff.toFixed(2)}). Excellent finishing performance.`,
      });
    } else if (xgDiff < -0.5) {
      insights.push({
        type: 'warning',
        title: 'Underperformed xG',
        description: `Scored ${stats.arsenalGoals} goals from ${stats.arsenalXg.toFixed(2)} xG (${xgDiff.toFixed(2)}). Created chances but didn't convert.`,
      });
    }

    // Shot accuracy insight
    if (stats.arsenalShotAccuracyPct > 50) {
      insights.push({
        type: 'success',
        title: 'High Shot Accuracy',
        description: `${stats.arsenalShotAccuracyPct.toFixed(1)}% of shots were on target. Good shot selection.`,
      });
    } else if (stats.arsenalShotAccuracyPct < 30) {
      insights.push({
        type: 'warning',
        title: 'Low Shot Accuracy',
        description: `Only ${stats.arsenalShotAccuracyPct.toFixed(1)}% of shots were on target. Need better shot selection.`,
      });
    }

    // Big chances insight
    if (stats.arsenalBigChances > 0) {
      const bigChanceConversion = (stats.arsenalBigChancesScored / stats.arsenalBigChances) * 100;
      if (bigChanceConversion >= 50) {
        insights.push({
          type: 'success',
          title: 'Excellent Big Chance Conversion',
          description: `Converted ${stats.arsenalBigChancesScored} of ${stats.arsenalBigChances} big chances (${bigChanceConversion.toFixed(0)}%).`,
        });
      } else if (bigChanceConversion < 30) {
        insights.push({
          type: 'warning',
          title: 'Poor Big Chance Conversion',
          description: `Only converted ${stats.arsenalBigChancesScored} of ${stats.arsenalBigChances} big chances (${bigChanceConversion.toFixed(0)}%).`,
        });
      }
    }

    // Half performance insight
    if (stats.arsenalSecondHalfXg > stats.arsenalFirstHalfXg * 1.5) {
      insights.push({
        type: 'info',
        title: 'Strong Second Half',
        description: `Generated ${stats.arsenalSecondHalfXg.toFixed(2)} xG in second half vs ${stats.arsenalFirstHalfXg.toFixed(2)} in first half.`,
      });
    }
  }

  // Key moments (goals and big chances)
  const keyMoments = shots
    .filter((s: any) => s.result === 'Goal' || s.xg > 0.3)
    .sort((a: any, b: any) => a.minute - b.minute)
    .slice(0, 10);

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Match Insights: {season}
      </Heading>

      {matches.length > 0 && (
        <Box mb={6}>
          <Select
            placeholder="Select Match"
            value={selectedMatch}
            onChange={(e) => setSelectedMatch(e.target.value)}
            
            size="lg"
          >
            {matches.map((match: any) => (
              <option key={match.matchId} value={match.matchId}>
                {match.matchName} - {new Date(match.matchDate).toLocaleDateString()}
              </option>
            ))}
          </Select>
        </Box>
      )}

      {statsLoading || shotsLoading ? (
        <Center py={10}>
          <Spinner size="xl" color="arsenal.500" />
        </Center>
      ) : statsError || shotsError ? (
        <Center py={10}>
          <Text color="red.500">
            Error loading match data: {statsError?.message || shotsError?.message}
          </Text>
        </Center>
      ) : stats ? (
        <>
          {/* Match Summary */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={6}>
            <Stat  p={4} borderRadius="xl" >
              <StatLabel>Result</StatLabel>
              <StatNumber>
                <Badge
                  colorScheme={stats.result === 'W' ? 'green' : stats.result === 'D' ? 'yellow' : 'red'}
                  fontSize="lg"
                  p={2}
                >
                  {stats.arsenalGoals} - {stats.opponentGoals}
                </Badge>
              </StatNumber>
              <StatHelpText>{stats.opponent} ({stats.venue})</StatHelpText>
            </Stat>
            <Stat  p={4} borderRadius="xl" >
              <StatLabel>xG Performance</StatLabel>
              <StatNumber>
                {(stats.arsenalGoals - stats.arsenalXg).toFixed(2)}
              </StatNumber>
              <StatHelpText>
                {stats.arsenalGoals} goals from {stats.arsenalXg.toFixed(2)} xG
              </StatHelpText>
            </Stat>
            <Stat  p={4} borderRadius="xl" >
              <StatLabel>Shot Accuracy</StatLabel>
              <StatNumber>{stats.arsenalShotAccuracyPct.toFixed(1)}%</StatNumber>
              <StatHelpText>
                {stats.arsenalShotsOnTarget} on target / {stats.arsenalShots} total
              </StatHelpText>
            </Stat>
            <Stat  p={4} borderRadius="xl" >
              <StatLabel>Big Chances</StatLabel>
              <StatNumber>
                {stats.arsenalBigChancesScored}/{stats.arsenalBigChances}
              </StatNumber>
              <StatHelpText>
                {stats.arsenalBigChances > 0
                  ? ((stats.arsenalBigChancesScored / stats.arsenalBigChances) * 100).toFixed(0)
                  : 0}% conversion
              </StatHelpText>
            </Stat>
          </SimpleGrid>

          {/* Insights */}
          {insights.length > 0 && (
            <Box mb={6}>
              <Heading size="md" mb={4}>Key Insights</Heading>
              <VStack spacing={3}>
                {insights.map((insight: any, idx: number) => (
                  <Alert
                    key={idx}
                    status={insight.type}
                    borderRadius="xl"
                  >
                    <AlertIcon />
                    <Box>
                      <AlertTitle>{insight.title}</AlertTitle>
                      <AlertDescription>{insight.description}</AlertDescription>
                    </Box>
                  </Alert>
                ))}
              </VStack>
            </Box>
          )}

          {/* Half Comparison */}
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
            <Box  p={6} borderRadius="xl" >
              <Heading size="md" mb={4}>First Half Performance</Heading>
              <SimpleGrid columns={2} spacing={4}>
                <Stat>
                  <StatLabel>Shots</StatLabel>
                  <StatNumber>{stats.arsenalFirstHalfShots}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>xG</StatLabel>
                  <StatNumber>{stats.arsenalFirstHalfXg.toFixed(2)}</StatNumber>
                </Stat>
              </SimpleGrid>
            </Box>
            <Box  p={6} borderRadius="xl" >
              <Heading size="md" mb={4}>Second Half Performance</Heading>
              <SimpleGrid columns={2} spacing={4}>
                <Stat>
                  <StatLabel>Shots</StatLabel>
                  <StatNumber>{stats.arsenalSecondHalfShots}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>xG</StatLabel>
                  <StatNumber>{stats.arsenalSecondHalfXg.toFixed(2)}</StatNumber>
                </Stat>
              </SimpleGrid>
            </Box>
          </SimpleGrid>

          {/* Key Moments */}
          {keyMoments.length > 0 && (
            <Box  p={6} borderRadius="xl" >
              <Heading size="md" mb={4}>Key Moments</Heading>
              <VStack spacing={2} align="stretch">
                {keyMoments.map((moment: any, idx: number) => (
                  <Box
                    key={idx}
                    p={3}
                    border="1px"
                    borderColor="gray.200"
                    borderRadius="xl"
                    bg={moment.result === 'Goal' ? '#F0FDF4' : '#FEF3C7'}
                  >
                    <HStack justify="space-between">
                      <HStack>
                        <Badge colorScheme={moment.result === 'Goal' ? 'green' : 'yellow'}>
                          {moment.minute}'
                        </Badge>
                        <Text fontWeight="medium">{moment.playerName}</Text>
                      </HStack>
                      <HStack>
                        {moment.result === 'Goal' && (
                          <Badge colorScheme="green">GOAL</Badge>
                        )}
                        {moment.xg > 0.3 && (
                          <Badge colorScheme="orange">Big Chance (xG: {moment.xg.toFixed(2)})</Badge>
                        )}
                      </HStack>
                    </HStack>
                  </Box>
                ))}
              </VStack>
            </Box>
          )}

          {/* Shot Quality Comparison */}
          <Box  p={6} borderRadius="xl"  mt={6}>
            <Heading size="md" mb={4}>Shot Quality Analysis</Heading>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              <Box>
                <Text fontWeight="medium" mb={2}>Arsenal</Text>
                <Text>Avg Shot xG: <strong>{stats.arsenalAvgShotXg.toFixed(3)}</strong></Text>
                <Text>Box Shots: {stats.arsenalBoxShots}</Text>
                <Text>Outside Box: {stats.arsenalOutsideBoxShots}</Text>
              </Box>
              <Box>
                <Text fontWeight="medium" mb={2}>Opponent</Text>
                <Text>Avg Shot xG: <strong>{stats.opponentAvgShotXg.toFixed(3)}</strong></Text>
                <Text>Total Shots: {stats.opponentShots}</Text>
                <Text>Shots on Target: {stats.opponentShotsOnTarget}</Text>
              </Box>
            </SimpleGrid>
          </Box>
        </>
      ) : selectedMatch ? (
        <Center py={10}>
          <Text>No advanced stats available for this match</Text>
        </Center>
      ) : (
        <Center py={10}>
          <Text>Please select a match to view insights</Text>
        </Center>
      )}
    </Box>
  );
}
