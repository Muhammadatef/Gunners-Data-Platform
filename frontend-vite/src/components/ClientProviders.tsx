'use client';

import { ChakraProvider } from '@chakra-ui/react';
import { ApolloProvider } from '@apollo/client';
import { client } from '@/lib/apollo-client';
import { theme } from '@/theme';
import { SeasonProvider } from '@/contexts/SeasonContext';
import Header from './Header';
import Footer from './Footer';

export default function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <ApolloProvider client={client}>
      <ChakraProvider theme={theme}>
        <SeasonProvider>
          <Header />
          {children}
          <Footer />
        </SeasonProvider>
      </ChakraProvider>
    </ApolloProvider>
  );
}
