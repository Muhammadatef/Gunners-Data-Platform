import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Heading, Text, Button, VStack, Code } from '@chakra-ui/react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          minH="100vh"
          bg="gray.900"
          color="white"
          display="flex"
          alignItems="center"
          justifyContent="center"
          p={8}
        >
          <VStack spacing={6} maxW="800px" align="stretch">
            <Heading color="red.400" size="xl">
              ⚠️ Something Went Wrong
            </Heading>

            <Text fontSize="lg" color="gray.300">
              The Arsenal Analytics app encountered an error. This usually happens when:
            </Text>

            <VStack align="stretch" spacing={2} pl={4}>
              <Text color="gray.400">• The backend GraphQL API is not running</Text>
              <Text color="gray.400">• Database connection failed</Text>
              <Text color="gray.400">• Network connectivity issues</Text>
            </VStack>

            {this.state.error && (
              <Box>
                <Text fontWeight="bold" mb={2} color="red.300">
                  Error Details:
                </Text>
                <Code
                  display="block"
                  whiteSpace="pre-wrap"
                  p={4}
                  bg="gray.800"
                  borderRadius="md"
                  fontSize="sm"
                  color="red.200"
                >
                  {this.state.error.toString()}
                </Code>
              </Box>
            )}

            {this.state.errorInfo && (
              <Box>
                <Text fontWeight="bold" mb={2} color="orange.300">
                  Component Stack:
                </Text>
                <Code
                  display="block"
                  whiteSpace="pre-wrap"
                  p={4}
                  bg="gray.800"
                  borderRadius="md"
                  fontSize="xs"
                  maxH="200px"
                  overflowY="auto"
                  color="orange.200"
                >
                  {this.state.errorInfo.componentStack}
                </Code>
              </Box>
            )}

            <VStack spacing={3} pt={4}>
              <Button
                colorScheme="red"
                size="lg"
                onClick={this.handleReload}
                width="full"
              >
                🔄 Reload Page
              </Button>

              <Text fontSize="sm" color="gray.500">
                If the problem persists, check:
                <br />
                1. Backend is running: <Code>docker compose ps backend</Code>
                <br />
                2. PostgreSQL is healthy: <Code>docker compose ps postgres</Code>
                <br />
                3. Backend logs: <Code>docker compose logs backend</Code>
              </Text>
            </VStack>
          </VStack>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
