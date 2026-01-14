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
  HStack,
} from '@chakra-ui/react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { format } from 'date-fns';

const GET_PERFORMANCE_TRENDS = gql`
  query GetPerformanceTrends($season: String!, $windowSize: Int) {
    performanceTrends(season: $season, windowSize: $windowSize) {
      matchDate
      opponent
      result
      goals
      xg
      shots
      shotsOnTarget
      bigChances
      rollingAvgXg
      rollingAvgGoals
    }
  }
`;

interface PerformanceTrendsProps {
  season: string;
}

export default function PerformanceTrends({ season }: PerformanceTrendsProps) {
  const [windowSize, setWindowSize] = useState(5);

  const { data, loading, error } = useQuery(GET_PERFORMANCE_TRENDS, {
    variables: { season: season || '2024-25', windowSize },
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
        <Text color="red.500">Error loading performance trends: {error.message}</Text>
      </Center>
    );
  }

  const trends = data?.performanceTrends || [];

  if (trends.length === 0) {
    return (
      <Center py={10}>
        <Text>No performance trend data available</Text>
      </Center>
    );
  }

  // Calculate current form (last 5 matches)
  const recentForm = trends.slice(-5);
  const formPoints = recentForm.reduce((sum: number, m: any) => 
    sum + (m.result === 'W' ? 3 : m.result === 'D' ? 1 : 0), 0);
  const avgXgRecent = recentForm.reduce((sum: number, m: any) => sum + m.xg, 0) / recentForm.length;
  const avgGoalsRecent = recentForm.reduce((sum: number, m: any) => sum + m.goals, 0) / recentForm.length;

  // Format data for charts
  const trendData = trends.map((t: any) => ({
    date: format(new Date(t.matchDate), 'MMM d'),
    fullDate: t.matchDate,
    goals: t.goals,
    xg: parseFloat(t.xg.toFixed(2)),
    rollingXg: t.rollingAvgXg ? parseFloat(t.rollingAvgXg.toFixed(2)) : null,
    rollingGoals: t.rollingAvgGoals ? parseFloat(t.rollingAvgGoals.toFixed(2)) : null,
    shots: t.shots,
    shotsOnTarget: t.shotsOnTarget,
    bigChances: t.bigChances,
    result: t.result,
  }));

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Performance Trends: {season}
      </Heading>

      <HStack mb={6} spacing={4}>
        <Text fontWeight="medium">Rolling Average Window:</Text>
        <Select
          value={windowSize}
          onChange={(e) => setWindowSize(parseInt(e.target.value))}
          width="150px"
          
        >
          <option value={3}>3 matches</option>
          <option value={5}>5 matches</option>
          <option value={10}>10 matches</option>
        </Select>
      </HStack>

      {/* Current Form Metrics */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={6}>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Form (Last 5)</StatLabel>
          <StatNumber>{formPoints}/15</StatNumber>
          <Text fontSize="sm" >
            {recentForm.filter((m: any) => m.result === 'W').length}W
            {' '}{recentForm.filter((m: any) => m.result === 'D').length}D
            {' '}{recentForm.filter((m: any) => m.result === 'L').length}L
          </Text>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Avg Goals (Last 5)</StatLabel>
          <StatNumber>{avgGoalsRecent.toFixed(2)}</StatNumber>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Avg xG (Last 5)</StatLabel>
          <StatNumber>{avgXgRecent.toFixed(2)}</StatNumber>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Total Matches</StatLabel>
          <StatNumber>{trends.length}</StatNumber>
        </Stat>
      </SimpleGrid>

      {/* Trend Charts */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={6}>
        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Goals vs xG Trend</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="goals" stackId="1" stroke="#10B981" fill="#10B981" fillOpacity={0.6} name="Goals" />
              <Area type="monotone" dataKey="xg" stackId="2" stroke="#EF0107" fill="#EF0107" fillOpacity={0.6} name="xG" />
              <Line type="monotone" dataKey="rollingGoals" stroke="#10B981" strokeWidth={2} strokeDasharray="5 5" name="Rolling Avg Goals" />
              <Line type="monotone" dataKey="rollingXg" stroke="#EF0107" strokeWidth={2} strokeDasharray="5 5" name="Rolling Avg xG" />
            </AreaChart>
          </ResponsiveContainer>
        </Box>

        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Shots & Big Chances Trend</Heading>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={100} />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="shots" stroke="#9CA3AF" strokeWidth={2} name="Total Shots" />
              <Line yAxisId="left" type="monotone" dataKey="shotsOnTarget" stroke="#F59E0B" strokeWidth={2} name="Shots on Target" />
              <Line yAxisId="right" type="monotone" dataKey="bigChances" stroke="#EF0107" strokeWidth={2} name="Big Chances" />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>

      {/* Rolling Averages */}
      <Box  p={6} borderRadius="xl" >
        <Heading size="md" mb={4}>Rolling Averages ({windowSize} matches)</Heading>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="rollingGoals" stroke="#10B981" strokeWidth={3} name="Rolling Avg Goals" />
            <Line type="monotone" dataKey="rollingXg" stroke="#EF0107" strokeWidth={3} name="Rolling Avg xG" />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
}
