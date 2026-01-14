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
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const GET_ASSIST_NETWORK = gql`
  query GetAssistNetwork($season: String!, $limit: Int) {
    assistNetwork(season: $season, limit: $limit) {
      assister
      shooter
      season
      assistsCount
      goalsFromAssists
      totalXgAssisted
    }
  }
`;

interface ShotNetworksProps {
  season: string;
}

export default function ShotNetworks({ season }: ShotNetworksProps) {
  const { data, loading } = useQuery(GET_ASSIST_NETWORK, {
    variables: { season: season || '2024-25', limit: 50 },
    skip: !season,
  });

  const networkRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data?.assistNetwork || !networkRef.current) return;

    const network = data.assistNetwork;
    const svg = d3.select(networkRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;
    svg.attr('width', width).attr('height', height);

    // Create graph
    const nodes: any[] = [];
    const links: any[] = [];

    network.forEach((edge: any) => {
      if (!nodes.find((n) => n.id === edge.assister)) {
        nodes.push({ id: edge.assister, type: 'assister' });
      }
      if (!nodes.find((n) => n.id === edge.shooter)) {
        nodes.push({ id: edge.shooter, type: 'shooter' });
      }
      links.push({
        source: edge.assister,
        target: edge.shooter,
        value: edge.assistsCount,
      });
    });

    const simulation = d3
      .forceSimulation(nodes as any)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#E5E7EB')
      .attr('stroke-width', (d: any) => d.value * 2);

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', 20)
      .attr('fill', '#EF0107')
      .attr('stroke', 'white')
      .attr('stroke-width', 2);

    const label = svg
      .append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d: any) => d.id)
      .attr('font-size', 11)
      .attr('dx', 25)
      .attr('dy', 5);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
      label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y);
    });
  }, [data]);

  if (loading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  const network = data?.assistNetwork || [];

  if (network.length === 0) {
    return (
      <Center py={10}>
        <Text>No assist network data available for this season</Text>
      </Center>
    );
  }

  const totalAssists = network.reduce((sum: number, edge: any) => sum + edge.assistsCount, 0);
  const goalsFromAssists = network.reduce((sum: number, edge: any) => sum + edge.goalsFromAssists, 0);
  const uniqueAssisters = new Set(network.map((edge: any) => edge.assister)).size;

  // Top assisters
  const assisterStats = network.reduce((acc: any, edge: any) => {
    if (!acc[edge.assister]) {
      acc[edge.assister] = { assists: 0, goals: 0 };
    }
    acc[edge.assister].assists += edge.assistsCount;
    acc[edge.assister].goals += edge.goalsFromAssists;
    return acc;
  }, {});

  const topAssisters = Object.entries(assisterStats)
    .map(([name, stats]: [string, any]) => ({
      name,
      assists: stats.assists,
      goals: stats.goals,
    }))
    .sort((a: any, b: any) => b.assists - a.assists)
    .slice(0, 10);

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Shot Networks: {season}
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={6}>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Total Assists</StatLabel>
          <StatNumber>{totalAssists}</StatNumber>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Goals from Assists</StatLabel>
          <StatNumber>{goalsFromAssists}</StatNumber>
        </Stat>
        <Stat  p={4} borderRadius="xl" >
          <StatLabel>Active Assisters</StatLabel>
          <StatNumber>{uniqueAssisters}</StatNumber>
        </Stat>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Assist Network Graph</Heading>
          <Box width="100%" overflow="auto">
            <svg ref={networkRef} style={{ display: 'block', margin: '0 auto' }} />
          </Box>
        </Box>

        <Box  p={6} borderRadius="xl" >
          <Heading size="md" mb={4}>Top Assisters</Heading>
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={topAssisters} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={120} />
              <Tooltip />
              <Bar dataKey="assists" fill="#EF0107" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </SimpleGrid>

      <Box  p={6} borderRadius="xl" >
        <Heading size="md" mb={4}>Assist Partnerships Detail</Heading>
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Assister</Th>
                <Th>Shooter</Th>
                <Th>Assists</Th>
                <Th>Goals</Th>
                <Th>xG</Th>
              </Tr>
            </Thead>
            <Tbody>
              {network.slice(0, 15).map((edge: any, idx: number) => (
                <Tr key={idx}>
                  <Td fontWeight="medium">{edge.assister}</Td>
                  <Td>{edge.shooter}</Td>
                  <Td>{edge.assistsCount}</Td>
                  <Td>{edge.goalsFromAssists}</Td>
                  <Td>{edge.totalXgAssisted.toFixed(2)}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
