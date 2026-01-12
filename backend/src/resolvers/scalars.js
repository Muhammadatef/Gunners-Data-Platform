import { GraphQLScalarType } from 'graphql';

export const DateScalar = new GraphQLScalarType({
  name: 'Date',
  description: 'Date custom scalar type',
  serialize(value) {
    if (value instanceof Date) {
      return value.toISOString();
    }
    if (typeof value === 'string') {
      return value;
    }
    return null;
  },
  parseValue(value) {
    if (typeof value === 'string') {
      return new Date(value);
    }
    return null;
  },
  parseLiteral(ast) {
    if (ast.kind === 'StringValue') {
      return new Date(ast.value);
    }
    return null;
  },
});

export const DecimalScalar = new GraphQLScalarType({
  name: 'Decimal',
  description: 'Decimal custom scalar type',
  serialize(value) {
    return parseFloat(value);
  },
  parseValue(value) {
    return parseFloat(value);
  },
  parseLiteral(ast) {
    if (ast.kind === 'FloatValue' || ast.kind === 'IntValue') {
      return parseFloat(ast.value);
    }
    return null;
  },
});
