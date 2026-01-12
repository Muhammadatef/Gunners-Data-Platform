import { ApolloClient, InMemoryCache, HttpLink, from } from '@apollo/client'
import { onError } from '@apollo/client/link/error'

// Use localhost for browser access (not the docker service name)
const graphqlUrl = typeof window !== 'undefined'
  ? 'http://localhost:4000/graphql'  // Browser
  : (import.meta.env.VITE_GRAPHQL_URL || 'http://localhost:4000/graphql')  // Server

console.log('🔗 GraphQL endpoint:', graphqlUrl)

// Error handling link
const errorLink = onError(({ graphQLErrors, networkError, operation }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
      )
    })
  }

  if (networkError) {
    console.error(`[Network error]: ${networkError}`)
    console.error('Operation:', operation.operationName)
    console.error('Network error details:', networkError)
  }
})

// HTTP link
const httpLink = new HttpLink({
  uri: graphqlUrl,
  fetchOptions: {
    mode: 'cors',
  },
  fetch: (uri, options) => {
    console.log(`🚀 GraphQL request to ${uri}`)
    return fetch(uri, options).catch(err => {
      console.error('❌ Fetch failed:', err)
      throw err
    })
  },
})

export const client = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
      errorPolicy: 'all',
    },
    query: {
      errorPolicy: 'all',
      fetchPolicy: 'network-only',
    },
  },
})

// Test connection on initialization
if (typeof window !== 'undefined') {
  console.log('✅ Apollo Client initialized')
}
