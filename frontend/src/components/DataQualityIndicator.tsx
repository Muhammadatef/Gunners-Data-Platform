'use client';

import { useQuery, gql } from '@apollo/client';
import {
  Box,
  HStack,
  Text,
  Badge,
  Spinner,
  Tooltip,
} from '@chakra-ui/react';

const GET_DATA_QUALITY = gql`
  query GetDataQuality {
    dataQuality {
      totalMatches
      totalShots
      dataCompleteness
      lastUpdate
      seasonsAvailable
      validationErrors
      dataFreshness
    }
  }
`;

export default function DataQualityIndicator() {
  const { data, loading, error } = useQuery(GET_DATA_QUALITY, {
    errorPolicy: 'all',
  });

  if (loading) {
    return <Spinner size="sm" />;
  }

  if (error) {
    return null; // Silently fail for data quality indicator
  }

  const quality = data?.dataQuality;

  if (!quality) {
    return null;
  }

  const getQualityColor = (completeness: number) => {
    if (completeness >= 90) return 'green';
    if (completeness >= 70) return 'yellow';
    return 'red';
  };

  return (
    <Tooltip
      label={
        <Box>
          <Text><strong>Data Quality:</strong> {quality.dataCompleteness.toFixed(1)}%</Text>
          <Text><strong>Matches:</strong> {quality.totalMatches}</Text>
          <Text><strong>Shots:</strong> {quality.totalShots}</Text>
          <Text><strong>Last Update:</strong> {quality.dataFreshness}</Text>
          <Text><strong>Seasons:</strong> {quality.seasonsAvailable.length}</Text>
        </Box>
      }
    >
      <HStack spacing={2} cursor="pointer">
        <Badge colorScheme={getQualityColor(quality.dataCompleteness)}>
          {quality.dataCompleteness.toFixed(0)}% Complete
        </Badge>
        <Text fontSize="xs" color="gray.600">
          {quality.totalMatches} matches • Updated {quality.dataFreshness}
        </Text>
      </HStack>
    </Tooltip>
  );
}
