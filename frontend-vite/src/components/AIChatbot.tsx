import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Input,
  Text,
  IconButton,
  Heading,
  Flex,
  Spinner,
  Badge,
  useDisclosure,
  Slide,
  CloseButton,
  Tooltip,
} from '@chakra-ui/react';
import { FiMessageCircle, FiSend, FiX } from 'react-icons/fi';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    match_date: string;
    opponent: string;
    result: string;
    season: string;
  }>;
  confidence?: number;
}

export default function AIChatbot() {
  const { isOpen, onToggle, onClose } = useDisclosure();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "👋 Hello! I'm your Arsenal FC data analyst. Ask me anything about Arsenal's performance, player stats, tactical analysis, or match results!"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          conversation_history: messages.slice(1) // Exclude welcome message
        })
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Sorry, I encountered an error. Please make sure the chatbot service is running.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <Tooltip label="Ask Arsenal AI Analyst" placement="left">
          <IconButton
            icon={<FiMessageCircle size={24} />}
            aria-label="Open chat"
            onClick={onToggle}
            position="fixed"
            bottom="30px"
            right="30px"
            size="lg"
            borderRadius="full"
            bg="linear-gradient(135deg, #EF0107 0%, #9C0D0F 100%)"
            color="white"
            boxShadow="0 8px 24px rgba(239, 1, 7, 0.4)"
            _hover={{
              transform: 'scale(1.1)',
              boxShadow: '0 12px 32px rgba(239, 1, 7, 0.6)',
            }}
            _active={{
              transform: 'scale(0.95)',
            }}
            transition="all 0.3s ease"
            zIndex={1000}
            width="60px"
            height="60px"
          />
        </Tooltip>
      )}

      {/* Chat Window */}
      <Slide direction="bottom" in={isOpen} style={{ zIndex: 999 }}>
        <Box
          position="fixed"
          bottom="30px"
          right="30px"
          width={{ base: '90vw', md: '400px' }}
          height="600px"
          bg="rgba(0, 31, 63, 0.95)"
          backdropFilter="blur(20px)"
          borderRadius="xl"
          border="1px solid rgba(239, 1, 7, 0.3)"
          boxShadow="0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(239, 1, 7, 0.2)"
          display="flex"
          flexDirection="column"
          overflow="hidden"
        >
          {/* Header */}
          <Flex
            bg="linear-gradient(135deg, #EF0107 0%, #9C0D0F 100%)"
            p={4}
            align="center"
            justify="space-between"
          >
            <HStack spacing={3}>
              <Box
                width="10px"
                height="10px"
                borderRadius="full"
                bg="#10B981"
                boxShadow="0 0 10px #10B981"
              />
              <VStack align="start" spacing={0}>
                <Heading size="sm" color="white">
                  Arsenal FC Analyst
                </Heading>
                <Text fontSize="xs" color="whiteAlpha.800">
                  🎯 AI-Powered Data Analysis
                </Text>
              </VStack>
            </HStack>
            <CloseButton onClick={onClose} color="white" />
          </Flex>

          {/* Messages */}
          <VStack
            flex={1}
            overflowY="auto"
            p={4}
            spacing={3}
            align="stretch"
            css={{
              '&::-webkit-scrollbar': { width: '4px' },
              '&::-webkit-scrollbar-track': { background: 'transparent' },
              '&::-webkit-scrollbar-thumb': {
                background: 'rgba(239, 1, 7, 0.5)',
                borderRadius: '2px',
              },
            }}
          >
            {messages.map((message, idx) => (
              <Box
                key={idx}
                alignSelf={message.role === 'user' ? 'flex-end' : 'flex-start'}
                maxW="80%"
              >
                <Box
                  bg={
                    message.role === 'user'
                      ? 'rgba(255, 255, 255, 0.1)'
                      : 'rgba(239, 1, 7, 0.1)'
                  }
                  border={
                    message.role === 'user'
                      ? '1px solid rgba(255, 255, 255, 0.2)'
                      : '1px solid rgba(239, 1, 7, 0.3)'
                  }
                  borderRadius="lg"
                  p={3}
                  backdropFilter="blur(10px)"
                >
                  <Text
                    color="white"
                    fontSize="sm"
                    whiteSpace="pre-wrap"
                    lineHeight="1.6"
                  >
                    {message.content}
                  </Text>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <VStack align="start" mt={3} spacing={1}>
                      <Text fontSize="xs" color="whiteAlpha.700" fontWeight="bold">
                        📊 Sources:
                      </Text>
                      {message.sources.slice(0, 3).map((source, i) => (
                        <Text key={i} fontSize="xs" color="whiteAlpha.600">
                          • {source.match_date}: Arsenal vs {source.opponent} ({source.result})
                        </Text>
                      ))}
                    </VStack>
                  )}

                  {/* Confidence */}
                  {message.confidence !== undefined && (
                    <Badge
                      mt={2}
                      size="sm"
                      colorScheme={message.confidence > 0.7 ? 'green' : 'yellow'}
                    >
                      {(message.confidence * 100).toFixed(0)}% confidence
                    </Badge>
                  )}
                </Box>
              </Box>
            ))}

            {isLoading && (
              <HStack spacing={2} alignSelf="flex-start">
                <Spinner size="sm" color="arsenal.500" />
                <Text fontSize="sm" color="whiteAlpha.600">
                  Analyzing data...
                </Text>
              </HStack>
            )}

            <div ref={messagesEndRef} />
          </VStack>

          {/* Input */}
          <Box
            p={4}
            borderTop="1px solid rgba(255, 255, 255, 0.1)"
            bg="rgba(0, 15, 31, 0.5)"
          >
            <HStack spacing={2}>
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about Arsenal's performance..."
                size="sm"
                bg="rgba(255, 255, 255, 0.05)"
                border="1px solid rgba(255, 255, 255, 0.1)"
                color="white"
                _placeholder={{ color: 'whiteAlpha.500' }}
                _focus={{
                  border: '1px solid rgba(239, 1, 7, 0.5)',
                  boxShadow: '0 0 0 1px rgba(239, 1, 7, 0.3)',
                }}
              />
              <IconButton
                icon={<FiSend />}
                aria-label="Send message"
                onClick={handleSend}
                isDisabled={!input.trim() || isLoading}
                size="sm"
                bg="linear-gradient(135deg, #EF0107 0%, #9C0D0F 100%)"
                color="white"
                _hover={{
                  transform: 'scale(1.05)',
                  boxShadow: '0 4px 12px rgba(239, 1, 7, 0.4)',
                }}
                _active={{ transform: 'scale(0.95)' }}
              />
            </HStack>

            {/* Quick Questions */}
            <HStack mt={2} spacing={2} flexWrap="wrap">
              {['vs Liverpool?', 'Top scorer?', 'xG trend?'].map((q) => (
                <Button
                  key={q}
                  size="xs"
                  variant="outline"
                  color="whiteAlpha.700"
                  borderColor="whiteAlpha.300"
                  _hover={{ bg: 'whiteAlpha.100' }}
                  onClick={() => setInput(q)}
                >
                  {q}
                </Button>
              ))}
            </HStack>
          </Box>
        </Box>
      </Slide>
    </>
  );
}
