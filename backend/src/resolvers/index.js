import { seasonResolvers } from './season.js';
import { matchResolvers } from './match.js';
import { playerResolvers } from './player.js';
import { tacticalResolvers } from './tactical.js';
import { advancedResolvers } from './advanced.js';
import { DateScalar, DecimalScalar } from './scalars.js';

export const resolvers = {
  Date: DateScalar,
  Decimal: DecimalScalar,
  Query: {
    ...seasonResolvers.Query,
    ...matchResolvers.Query,
    ...playerResolvers.Query,
    ...tacticalResolvers.Query,
    ...advancedResolvers.Query,
  },
};
