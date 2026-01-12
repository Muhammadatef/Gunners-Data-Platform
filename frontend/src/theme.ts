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
  },
  fonts: {
    heading: `'Inter', system-ui, -apple-system, sans-serif`,
    body: `'Inter', system-ui, -apple-system, sans-serif`,
  },
  styles: {
    global: {
      body: {
        bg: '#F9FAFB',
        color: '#1F2937',
      },
    },
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'arsenal',
      },
    },
    Tabs: {
      variants: {
        line: {
          tab: {
            _selected: {
              color: 'arsenal.500',
              borderColor: 'arsenal.500',
            },
          },
        },
      },
    },
  },
});
