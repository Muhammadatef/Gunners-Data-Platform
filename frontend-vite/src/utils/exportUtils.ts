import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import Papa from 'papaparse';

// Export utilities for Arsenal Analytics Platform

/**
 * Export data to CSV format
 */
export const exportToCSV = (data: any[], filename: string) => {
  const csv = Papa.unparse(data);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export season summary to PDF
 */
export const exportSeasonSummaryToPDF = (seasonData: any) => {
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(20);
  doc.setTextColor(239, 1, 7); // Arsenal red
  doc.text('Arsenal FC Analytics', 14, 20);
  
  doc.setFontSize(14);
  doc.setTextColor(0, 0, 0);
  doc.text(`Season Summary: ${seasonData.season}`, 14, 30);
  
  // Summary stats
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 38);
  
  // Record table
  autoTable(doc, {
    startY: 45,
    head: [['Metric', 'Value']],
    body: [
      ['Matches Played', seasonData.played?.toString() || '0'],
      ['Wins', seasonData.wins?.toString() || '0'],
      ['Draws', seasonData.draws?.toString() || '0'],
      ['Losses', seasonData.losses?.toString() || '0'],
      ['Win Rate', `${seasonData.win_rate?.toFixed(1) || '0'}%`],
      ['Points', seasonData.points?.toString() || '0'],
      ['Goals For', seasonData.goals_for?.toString() || '0'],
      ['Goals Against', seasonData.goals_against?.toString() || '0'],
      ['Goal Difference', seasonData.goal_difference?.toString() || '0'],
      ['xG For', seasonData.xg_for?.toFixed(2) || '0'],
      ['xG Against', seasonData.xg_against?.toFixed(2) || '0'],
    ],
    theme: 'striped',
    headStyles: { fillColor: [239, 1, 7] },
  });
  
  // Save
  doc.save(`arsenal_season_summary_${seasonData.season}_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Export match detail to PDF
 */
export const exportMatchDetailToPDF = (matchData: any, shots: any[]) => {
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(20);
  doc.setTextColor(239, 1, 7);
  doc.text('Arsenal FC Analytics', 14, 20);
  
  doc.setFontSize(14);
  doc.setTextColor(0, 0, 0);
  doc.text('Match Detail Report', 14, 30);
  
  // Match info
  doc.setFontSize(12);
  doc.text(`${matchData.home_team} ${matchData.home_goals} - ${matchData.away_goals} ${matchData.away_team}`, 14, 40);
  doc.setFontSize(10);
  doc.text(`Date: ${matchData.match_date}`, 14, 47);
  doc.text(`xG: ${matchData.home_xg?.toFixed(2)} - ${matchData.away_xg?.toFixed(2)}`, 14, 53);
  
  // Shots table
  if (shots && shots.length > 0) {
    autoTable(doc, {
      startY: 60,
      head: [['Player', 'Minute', 'xG', 'Result', 'Type']],
      body: shots.slice(0, 20).map(shot => [
        shot.player_name || 'Unknown',
        shot.minute?.toString() || '-',
        shot.xg?.toFixed(3) || '0',
        shot.result || '-',
        shot.shot_type || '-',
      ]),
      theme: 'striped',
      headStyles: { fillColor: [239, 1, 7] },
    });
  }
  
  // Save
  doc.save(`arsenal_match_${matchData.match_id}_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Export player stats to PDF
 */
export const exportPlayerStatsToPDF = (players: any[], season: string) => {
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(20);
  doc.setTextColor(239, 1, 7);
  doc.text('Arsenal FC Analytics', 14, 20);
  
  doc.setFontSize(14);
  doc.setTextColor(0, 0, 0);
  doc.text(`Player Statistics: ${season}`, 14, 30);
  
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 38);
  
  // Players table
  if (players && players.length > 0) {
    autoTable(doc, {
      startY: 45,
      head: [['Player', 'Shots', 'Goals', 'xG', 'Accuracy %']],
      body: players.map(player => [
        player.player_name || 'Unknown',
        player.total_shots?.toString() || '0',
        player.goals?.toString() || '0',
        player.total_xg?.toFixed(2) || '0',
        player.shot_accuracy?.toFixed(1) || '0',
      ]),
      theme: 'striped',
      headStyles: { fillColor: [239, 1, 7] },
    });
  }
  
  // Save
  doc.save(`arsenal_player_stats_${season}_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Export any data array to CSV
 */
export const exportDataToCSV = (data: any[], filename: string, fields?: string[]) => {
  const csv = Papa.unparse(data, {
    fields: fields,
  });
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
