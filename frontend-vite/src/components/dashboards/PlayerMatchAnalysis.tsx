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
} from '@chakra-ui/react';
import Pitch from '@/components/Pitch';
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const GET_MATCH_LIST = gql`
  query GetMatchList($season: String!) {
    matchList(season: $season) {
      matchId
      matchName
      matchDate
    }
  }
`;

const GET_MATCH_PLAYERS = gql`
  query GetMatchPlayers($matchId: String!) {
    matchPlayers(matchId: $matchId)
  }
`;

const GET_MATCH_PLAYER_SHOTS = gql`
  query GetMatchPlayerShots($matchId: String!, $playerName: String!) {
    matchPlayerShots(matchId: $matchId, playerName: $playerName) {
      x
      y
      xg
      result
      playerName
      minute
      assistedBy
    }
  }
`;

const GET_MATCH_PLAYER_NETWORK = gql`
  query GetMatchPlayerNetwork($matchId: String!) {
    matchPlayerNetwork(matchId: $matchId) {
      assister
      shooter
      assistsCount
      goalsFromAssists
      totalXgAssisted
    }
  }
`;

interface PlayerMatchAnalysisProps {
  season: string;
}

export default function PlayerMatchAnalysis({ season }: PlayerMatchAnalysisProps) {
  const { data: matchListData, loading: matchListLoading } = useQuery(GET_MATCH_LIST, {
    variables: { season: season || '2024-25' },
    skip: !season,
  });

  const [selectedMatch, setSelectedMatch] = useState<string>('');
  const [selectedPlayer, setSelectedPlayer] = useState<string>('');

  const { data: playersData, loading: playersLoading } = useQuery(GET_MATCH_PLAYERS, {
    variables: { matchId: selectedMatch },
    skip: !selectedMatch,
  });

  const { data: shotsData, loading: shotsLoading } = useQuery(GET_MATCH_PLAYER_SHOTS, {
    variables: { matchId: selectedMatch, playerName: selectedPlayer },
    skip: !selectedMatch || !selectedPlayer,
  });

  const { data: networkData, loading: networkLoading } = useQuery(GET_MATCH_PLAYER_NETWORK, {
    variables: { matchId: selectedMatch },
    skip: !selectedMatch,
  });

  const networkRef = useRef<SVGSVGElement>(null);

  // Reset player selection when match changes
  useEffect(() => {
    if (selectedMatch) {
      setSelectedPlayer('');
    }
  }, [selectedMatch]);

  // Auto-select first player when players load
  useEffect(() => {
    if (playersData?.matchPlayers && playersData.matchPlayers.length > 0 && !selectedPlayer) {
      setSelectedPlayer(playersData.matchPlayers[0]);
    }
  }, [playersData, selectedPlayer]);

  // Render pass network
  useEffect(() => {
    if (!networkData?.matchPlayerNetwork || !networkRef.current || !selectedPlayer) return;

    const network = networkData.matchPlayerNetwork;
    const svg = d3.select(networkRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;
    svg.attr('width', width).attr('height', height);

    // Filter network to show connections involving selected player
    const filteredNetwork = network.filter(
      (edge: any) => edge.assister === selectedPlayer || edge.shooter === selectedPlayer
    );

    if (filteredNetwork.length === 0) {
      svg
        .append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .attr('fill', '#9CA3AF')
        .text('No pass network data for this player in this match');
      return;
    }

    // Create graph
    const nodes: any[] = [];
    const links: any[] = [];

    // Add selected player as central node
    if (!nodes.find((n) => n.id === selectedPlayer)) {
      nodes.push({ id: selectedPlayer, type: 'selected', isCentral: true });
    }

    filteredNetwork.forEach((edge: any) => {
      if (edge.assister === selectedPlayer) {
        // Player assisted someone
        if (!nodes.find((n) => n.id === edge.shooter)) {
          nodes.push({ id: edge.shooter, type: 'shooter' });
        }
        links.push({
          source: selectedPlayer,
          target: edge.shooter,
          value: edge.assistsCount,
          direction: 'out',
        });
      } else if (edge.shooter === selectedPlayer) {
        // Someone assisted the player
        if (!nodes.find((n) => n.id === edge.assister)) {
          nodes.push({ id: edge.assister, type: 'assister' });
        }
        links.push({
          source: edge.assister,
          target: selectedPlayer,
          value: edge.assistsCount,
          direction: 'in',
        });
      }
    });

    const simulation = d3
      .forceSimulation(nodes as any)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', (d: any) => (d.direction === 'out' ? '#10B981' : '#EF0107'))
      .attr('stroke-width', (d: any) => d.value * 3)
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', 'url(#arrowhead)');

    // Add arrow markers
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#6B7280');

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d: any) => (d.isCentral ? 30 : 20))
      .attr('fill', (d: any) => (d.isCentral ? '#EF0107' : '#9CA3AF'))
      .attr('stroke', 'white')
      .attr('stroke-width', 3);

    const label = svg
      .append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d: any) => d.id)
      .attr('font-size', (d: any) => (d.isCentral ? 12 : 10))
      .attr('font-weight', (d: any) => (d.isCentral ? 'bold' : 'normal'))
      .attr('dx', (d: any) => (d.isCentral ? 35 : 25))
      .attr('dy', 5)
      .attr('fill', '#1F2937');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
      label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y);
    });
  }, [networkData, selectedPlayer]);

  if (matchListLoading) {
    return (
      <Center py={10}>
        <Spinner size="xl" color="arsenal.500" />
      </Center>
    );
  }

  const matches = matchListData?.matchList || [];
  const players = playersData?.matchPlayers || [];
  const shots = shotsData?.matchPlayerShots || [];
  const network = networkData?.matchPlayerNetwork || [];

  const playerStats = {
    totalShots: shots.length,
    goals: shots.filter((s: any) => s.result === 'Goal').length,
    totalXg: shots.reduce((sum: number, s: any) => sum + s.xg, 0),
    assists: network.filter((e: any) => e.assister === selectedPlayer).length,
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Player Match Analysis: {season}
      </Heading>

      {/* Match Selector */}
      {matches.length > 0 && (
        <Box mb={6}>
          <Select
            placeholder="Select Match"
            value={selectedMatch}
            onChange={(e) => setSelectedMatch(e.target.value)}
            
            mb={4}
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

      {selectedMatch && (
        <>
          {/* Player Selector */}
          {playersLoading ? (
            <Center py={4}>
              <Spinner size="md" color="arsenal.500" />
            </Center>
          ) : players.length > 0 ? (
            <Box mb={6}>
              <Select
                placeholder="Select Player"
                value={selectedPlayer}
                onChange={(e) => setSelectedPlayer(e.target.value)}
                
                size="lg"
              >
                {players.map((player: string) => (
                  <option key={player} value={player}>
                    {player}
                  </option>
                ))}
              </Select>
            </Box>
          ) : (
            <Center py={4}>
              <Text >No players found for this match</Text>
            </Center>
          )}

          {selectedPlayer && (
            <>
              {/* Player Stats */}
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={6}>
                <Stat  p={4} borderRadius="xl" >
                  <StatLabel>Shots</StatLabel>
                  <StatNumber>{playerStats.totalShots}</StatNumber>
                </Stat>
                <Stat  p={4} borderRadius="xl" >
                  <StatLabel>Goals</StatLabel>
                  <StatNumber>{playerStats.goals}</StatNumber>
                </Stat>
                <Stat  p={4} borderRadius="xl" >
                  <StatLabel>Total xG</StatLabel>
                  <StatNumber>{playerStats.totalXg.toFixed(2)}</StatNumber>
                </Stat>
                <Stat  p={4} borderRadius="xl" >
                  <StatLabel>Assists</StatLabel>
                  <StatNumber>{playerStats.assists}</StatNumber>
                </Stat>
              </SimpleGrid>

              {/* Visualizations */}
              <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={6}>
                {/* Shot Heat Map */}
                <Box  p={6} borderRadius="xl" >
                  <Heading size="md" mb={4}>
                    {selectedPlayer} - Shot Heat Map
                  </Heading>
                  {shotsLoading ? (
                    <Center py={10}>
                      <Spinner size="xl" color="arsenal.500" />
                    </Center>
                  ) : shots.length > 0 ? (
                    <Pitch shots={shots} />
                  ) : (
                    <Center py={10}>
                      <Text >No shots data for this player in this match</Text>
                    </Center>
                  )}
                </Box>

                {/* Pass Network */}
                <Box  p={6} borderRadius="xl" >
                  <Heading size="md" mb={4}>
                    {selectedPlayer} - Pass Network
                  </Heading>
                  {networkLoading ? (
                    <Center py={10}>
                      <Spinner size="xl" color="arsenal.500" />
                    </Center>
                  ) : (
                    <Box width="100%" overflow="auto">
                      <svg ref={networkRef} style={{ display: 'block', margin: '0 auto' }} />
                    </Box>
                  )}
                  <Box mt={4} fontSize="sm" >
                    <Text>
                      <Box as="span" color="#EF0107" fontWeight="bold">
                        Red
                      </Box>{' '}
                      = Received assists |{' '}
                      <Box as="span" color="#10B981" fontWeight="bold">
                        Green
                      </Box>{' '}
                      = Given assists
                    </Text>
                  </Box>
                </Box>
              </SimpleGrid>

              {/* Shot Details */}
              {shots.length > 0 && (
                <Box  p={6} borderRadius="xl" >
                  <Heading size="md" mb={4}>Shot Details</Heading>
                  <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                    {shots.map((shot: any, idx: number) => (
                      <Box
                        key={idx}
                        p={3}
                        border="1px"
                        borderColor="gray.200"
                        borderRadius="xl"
                        bg={shot.result === 'Goal' ? '#F0FDF4' : 'white'}
                      >
                        <Text fontSize="sm" fontWeight="bold">
                          {shot.minute}'
                        </Text>
                        <Text fontSize="xs" >
                          {shot.result} - xG: {shot.xg.toFixed(3)}
                        </Text>
                        {shot.assistedBy && (
                          <Text fontSize="xs" color="arsenal.500">
                            Assisted by: {shot.assistedBy}
                          </Text>
                        )}
                      </Box>
                    ))}
                  </SimpleGrid>
                </Box>
              )}
            </>
          )}
        </>
      )}

      {!selectedMatch && (
        <Center py={10}>
          <Text >Please select a match to view player analysis</Text>
        </Center>
      )}
    </Box>
  );
}
