/**
 * Data Validation Utilities
 * Ensures metrics reflect reality and data quality
 */

/**
 * Validate match data consistency
 */
export function validateMatchData(match) {
  const errors = [];

  // Validate goals
  if (match.arsenalGoals < 0 || match.opponentGoals < 0) {
    errors.push('Goals cannot be negative');
  }

  // Validate xG
  if (match.arsenalXg < 0 || match.opponentXg < 0) {
    errors.push('xG cannot be negative');
  }

  // Validate result matches score
  const expectedResult = 
    match.arsenalGoals > match.opponentGoals ? 'W' :
    match.arsenalGoals < match.opponentGoals ? 'L' : 'D';
  
  if (match.result !== expectedResult) {
    errors.push(`Result mismatch: expected ${expectedResult} based on score`);
  }

  // Validate xG is reasonable (not too high)
  if (match.arsenalXg > 10 || match.opponentXg > 10) {
    errors.push('xG values seem unreasonably high');
  }

  return errors;
}

/**
 * Validate player stats consistency
 */
export function validatePlayerStats(playerStats) {
  const errors = [];

  // Goals should be non-negative
  if (playerStats.goals < 0) {
    errors.push('Goals cannot be negative');
  }

  // Total shots should be >= goals
  if (playerStats.totalShots < playerStats.goals) {
    errors.push('Total shots should be >= goals');
  }

  // Conversion rate should be between 0 and 100
  const conversionRate = (playerStats.goals / playerStats.totalShots) * 100;
  if (conversionRate < 0 || conversionRate > 100) {
    errors.push('Conversion rate out of valid range');
  }

  // xG should be reasonable
  if (playerStats.totalXg < 0 || playerStats.totalXg > playerStats.totalShots) {
    errors.push('xG values seem invalid');
  }

  // Goals vs xG should be reasonable (typically within -5 to +5)
  const xgDiff = playerStats.goals - playerStats.totalXg;
  if (Math.abs(xgDiff) > 10) {
    errors.push('Goals vs xG difference seems extreme');
  }

  return errors;
}

/**
 * Validate shot data
 */
export function validateShotData(shot) {
  const errors = [];

  // xG should be between 0 and 1
  if (shot.xg < 0 || shot.xg > 1) {
    errors.push('xG must be between 0 and 1');
  }

  // Coordinates should be valid (0-1 range for normalized pitch)
  if (shot.x < 0 || shot.x > 1 || shot.y < 0 || shot.y > 1) {
    errors.push('Shot coordinates out of valid range');
  }

  // Minute should be valid
  if (shot.minute < 0 || shot.minute > 120) {
    errors.push('Minute out of valid range');
  }

  return errors;
}

/**
 * Validate season summary data
 */
export function validateSeasonSummary(summary) {
  const errors = [];

  // Points calculation
  const expectedPoints = (summary.wins * 3) + summary.draws;
  if (summary.points !== expectedPoints) {
    errors.push(`Points mismatch: expected ${expectedPoints}, got ${summary.points}`);
  }

  // Matches should equal wins + draws + losses
  const expectedMatches = summary.wins + summary.draws + summary.losses;
  if (summary.matchesPlayed !== expectedMatches) {
    errors.push(`Matches mismatch: expected ${expectedMatches}, got ${summary.matchesPlayed}`);
  }

  // Goal difference
  const expectedGD = summary.goalsFor - summary.goalsAgainst;
  if (summary.goalDifference !== expectedGD) {
    errors.push(`Goal difference mismatch: expected ${expectedGD}, got ${summary.goalDifference}`);
  }

  return errors;
}

/**
 * Cross-validate data between sources
 */
export function crossValidateData(understatData, fbrefData) {
  const discrepancies = [];

  // Compare goals
  if (understatData.goals !== fbrefData.goals) {
    discrepancies.push({
      field: 'goals',
      understat: understatData.goals,
      fbref: fbrefData.goals,
      difference: Math.abs(understatData.goals - fbrefData.goals),
    });
  }

  // Compare xG (allow small differences due to model variations)
  const xgDiff = Math.abs(understatData.xg - fbrefData.xg);
  if (xgDiff > 0.5) {
    discrepancies.push({
      field: 'xg',
      understat: understatData.xg,
      fbref: fbrefData.xg,
      difference: xgDiff,
    });
  }

  return discrepancies;
}

/**
 * Calculate data completeness score
 */
export function calculateCompleteness(data) {
  const requiredFields = [
    'matchDate',
    'opponent',
    'arsenalGoals',
    'opponentGoals',
    'arsenalXg',
    'opponentXg',
  ];

  const presentFields = requiredFields.filter(field => data[field] !== null && data[field] !== undefined);
  const completeness = (presentFields.length / requiredFields.length) * 100;

  return {
    completeness,
    missingFields: requiredFields.filter(field => !presentFields.includes(field)),
  };
}

/**
 * Validate aggregation consistency
 */
export function validateAggregations(individualData, aggregatedData) {
  const errors = [];

  // Sum of player goals should equal team goals
  const sumPlayerGoals = individualData.reduce((sum, player) => sum + (player.goals || 0), 0);
  if (Math.abs(sumPlayerGoals - aggregatedData.teamGoals) > 1) {
    errors.push(`Goals mismatch: sum of players (${sumPlayerGoals}) != team (${aggregatedData.teamGoals})`);
  }

  // Sum of player xG should approximately equal team xG
  const sumPlayerXg = individualData.reduce((sum, player) => sum + (player.totalXg || 0), 0);
  const xgDiff = Math.abs(sumPlayerXg - aggregatedData.teamXg);
  if (xgDiff > 2) {
    errors.push(`xG mismatch: sum of players (${sumPlayerXg.toFixed(2)}) != team (${aggregatedData.teamXg.toFixed(2)})`);
  }

  return errors;
}
