'use client';

import { Box, Container, Text, Link, HStack } from '@chakra-ui/react';

export default function Footer() {
  return (
    <Box
      bg="rgba(255, 255, 255, 0.03)"
      backdropFilter="blur(10px)"
      borderTop="1px solid rgba(255, 255, 255, 0.1)"
      py={6}
      mt={12}
    >
      <Container maxW="container.xl">
        <HStack justify="center" spacing={4} flexWrap="wrap">
          <Text fontSize="sm" color="gray.300">
            Powered by{' '}
            <Link
              href="https://understat.com"
              isExternal
              color="arsenal.500"
              _hover={{
                color: 'gold.500',
                textDecoration: 'underline',
              }}
              transition="all 0.3s ease"
            >
              Understat
            </Link>{' '}
            &{' '}
            <Link
              href="https://fbref.com"
              isExternal
              color="arsenal.500"
              _hover={{
                color: 'gold.500',
                textDecoration: 'underline',
              }}
              transition="all 0.3s ease"
            >
              FBref
            </Link>
          </Text>
          <Text fontSize="sm" color="gray.400">
            •
          </Text>
          <Text fontSize="sm" color="gray.300">
            Built with ❤️ for Arsenal FC
          </Text>
        </HStack>
      </Container>
    </Box>
  );
}
