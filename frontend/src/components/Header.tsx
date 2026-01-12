'use client';

import {
  Box,
  Container,
  Flex,
  Heading,
  Image,
  Select,
  HStack,
} from '@chakra-ui/react';
import { useQuery, gql } from '@apollo/client';
import { useSeason } from '@/contexts/SeasonContext';
import { useEffect } from 'react';
import DataQualityIndicator from './DataQualityIndicator';

const GET_SEASONS = gql`
  query GetSeasons {
    seasons
  }
`;

export default function Header() {
  const { data } = useQuery(GET_SEASONS);
  const { season, setSeason } = useSeason();

  useEffect(() => {
    if (data?.seasons && data.seasons.length > 0 && !season) {
      setSeason(data.seasons[0]);
    }
  }, [data, season, setSeason]);

  return (
    <Box bg="white" borderBottom="1px" borderColor="gray.200" py={4}>
      <Container maxW="container.xl">
        <Flex align="center" justify="space-between">
          <HStack spacing={4}>
            <Image
              src="/arsenal-cannon.svg"
              alt="Arsenal FC"
              height="40px"
              fallback={
                <Box
                  width="40px"
                  height="40px"
                  bg="arsenal.500"
                  borderRadius="md"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  color="white"
                  fontWeight="bold"
                  fontSize="xl"
                >
                  AFC
                </Box>
              }
            />
            <Heading size="lg" color="arsenal.500">
              Arsenal FC Analytics
            </Heading>
          </HStack>
          <HStack spacing={4}>
            {data?.seasons && data.seasons.length > 0 && (
              <Select
                value={season || data.seasons[0]}
                onChange={(e) => setSeason(e.target.value)}
                width="200px"
                bg="white"
              >
                {data.seasons.map((s: string) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </Select>
            )}
            <DataQualityIndicator />
          </HStack>
        </Flex>
      </Container>
    </Box>
  );
}
