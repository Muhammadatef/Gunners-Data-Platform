'use client';

import { Box, Container, Text, Link, HStack } from '@chakra-ui/react';

export default function Footer() {
  return (
    <Box bg="white" borderTop="1px" borderColor="gray.200" py={6} mt={12}>
      <Container maxW="container.xl">
        <HStack justify="center" spacing={4}>
          <Text fontSize="sm" color="gray.600">
            Powered by{' '}
            <Link href="https://understat.com" isExternal color="arsenal.500">
              Understat
            </Link>{' '}
            &{' '}
            <Link href="https://fbref.com" isExternal color="arsenal.500">
              FBref
            </Link>
          </Text>
          <Text fontSize="sm" color="gray.600">
            •
          </Text>
          <Text fontSize="sm" color="gray.600">
            Built with ❤️ for Arsenal FC
          </Text>
        </HStack>
      </Container>
    </Box>
  );
}
