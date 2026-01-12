import { extendTheme } from '@chakra-ui/react';

export const theme = extendTheme({
  colors: {
    arsenal: {
      50: '#fee2e2',
      100: '#fecaca',
      200: '#fca5a5',
      300: '#f87171',
      400: '#ef4444',
      500: '#EF0107', // Arsenal red
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
    gold: {
      500: '#F0AB00',
    },
    navy: {
      50: '#e6f0ff',
      100: '#b3d1ff',
      200: '#80b3ff',
      300: '#4d94ff',
      400: '#1a75ff',
      500: '#063672', // Arsenal navy
      600: '#052b5c',
      700: '#042046',
      800: '#031530',
      900: '#001F3F', // Dark navy
    },
  },
  fonts: {
    heading: `'Inter', system-ui, -apple-system, sans-serif`,
    body: `'Inter', system-ui, -apple-system, sans-serif`,
  },
  styles: {
    global: {
      body: {
        bg: 'linear-gradient(135deg, #001F3F 0%, #063672 50%, #001F3F 100%)',
        bgAttachment: 'fixed',
        color: 'white',
        minHeight: '100vh',
      },
      '*::placeholder': {
        color: 'gray.400',
      },
      '*': {
        scrollbarWidth: 'thin',
        scrollbarColor: '#EF0107 #001F3F',
      },
      '*::-webkit-scrollbar': {
        width: '8px',
      },
      '*::-webkit-scrollbar-track': {
        background: '#001F3F',
      },
      '*::-webkit-scrollbar-thumb': {
        background: '#EF0107',
        borderRadius: '4px',
      },
    },
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'arsenal',
      },
      variants: {
        solid: {
          bg: 'linear-gradient(135deg, #EF0107 0%, #9C0D0F 100%)',
          color: 'white',
          _hover: {
            bg: 'linear-gradient(135deg, #FF4655 0%, #EF0107 100%)',
            transform: 'translateY(-2px)',
            boxShadow: '0 10px 20px rgba(239, 1, 7, 0.3)',
          },
          transition: 'all 0.3s ease',
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          bg: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          borderRadius: 'xl',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s ease',
          _hover: {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(239, 1, 7, 0.2)',
            border: '1px solid rgba(239, 1, 7, 0.3)',
          },
        },
      },
    },
    Tabs: {
      variants: {
        line: {
          tab: {
            color: 'gray.300',
            borderColor: 'transparent',
            bg: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(5px)',
            borderRadius: 'lg',
            mr: 2,
            mb: 2,
            px: 4,
            py: 2,
            transition: 'all 0.3s ease',
            _hover: {
              color: 'white',
              bg: 'rgba(239, 1, 7, 0.2)',
              transform: 'translateY(-2px)',
            },
            _selected: {
              color: 'white',
              bg: 'linear-gradient(135deg, #EF0107 0%, #9C0D0F 100%)',
              borderColor: 'arsenal.500',
              boxShadow: '0 4px 12px rgba(239, 1, 7, 0.4)',
              transform: 'translateY(-2px)',
            },
          },
          tablist: {
            borderBottom: '2px solid rgba(255, 255, 255, 0.1)',
            pb: 2,
          },
          tabpanel: {
            p: 6,
          },
        },
      },
    },
    Stat: {
      baseStyle: {
        container: {
          bg: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          borderRadius: 'xl',
          p: 4,
          border: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'all 0.3s ease',
          _hover: {
            transform: 'scale(1.05)',
            boxShadow: '0 8px 24px rgba(239, 1, 7, 0.2)',
          },
        },
        label: {
          color: 'gray.300',
          fontSize: 'sm',
          fontWeight: 'medium',
        },
        number: {
          color: 'white',
          fontSize: '2xl',
          fontWeight: 'bold',
        },
        helpText: {
          color: 'gray.400',
          fontSize: 'xs',
        },
      },
    },
  },
});
