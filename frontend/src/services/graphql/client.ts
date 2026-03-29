import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const graphqlUri = import.meta.env.VITE_GRAPHQL_URL || '/graphql';

const httpLink = createHttpLink({
  uri: graphqlUri,
});

export const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
});
