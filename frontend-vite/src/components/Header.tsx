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
    <Box
      bg="rgba(255, 255, 255, 0.05)"
      backdropFilter="blur(20px)"
      borderBottom="1px solid rgba(255, 255, 255, 0.1)"
      py={4}
      position="sticky"
      top={0}
      zIndex={1000}
      boxShadow="0 8px 32px rgba(0, 0, 0, 0.3)"
    >
      <Container maxW="container.xl">
        <Flex align="center" justify="space-between">
          <HStack spacing={4}>
            <Image
              src="/arsenal-cannon.svg"
              alt="Arsenal FC"
              height="50px"
              fallback={
                <Box
                  width="50px"
                  height="50px"
                  bg="linear-gradient(135deg, #EF0107 0%, #9C0D0F 100%)"
                  borderRadius="xl"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  color="white"
                  fontWeight="bold"
                  fontSize="2xl"
                  boxShadow="0 4px 12px rgba(239, 1, 7, 0.4)"
                >
                  AFC
                </Box>
              }
            />
            <Heading
              size="lg"
              bgGradient="linear(to-r, #EF0107, #F0AB00)"
              bgClip="text"
              fontWeight="extrabold"
            >
              Arsenal FC Analytics
            </Heading>
          </HStack>
          <HStack spacing={4}>
            {data?.seasons && data.seasons.length > 0 && (
              <Select
                value={season || data.seasons[0]}
                onChange={(e) => setSeason(e.target.value)}
                width="200px"
                bg="rgba(255, 255, 255, 0.05)"
                backdropFilter="blur(10px)"
                border="1px solid rgba(255, 255, 255, 0.1)"
                color="white"
                _hover={{
                  bg: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(239, 1, 7, 0.3)',
                }}
                _focus={{
                  border: '1px solid #EF0107',
                  boxShadow: '0 0 0 1px #EF0107',
                }}
                transition="all 0.3s ease"
              >
                {data.seasons.map((s: string) => (
                  <option key={s} value={s} style={{ background: '#001F3F', color: 'white' }}>
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
