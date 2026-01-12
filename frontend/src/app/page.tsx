'use client';

import {
  Container,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { useSeason } from '@/contexts/SeasonContext';

// Disable static generation for this page
export const dynamic = 'force-dynamic';
import SeasonOverview from '@/components/dashboards/SeasonOverview';
import MatchDetail from '@/components/dashboards/MatchDetail';
import PlayerStats from '@/components/dashboards/PlayerStats';
import TacticalAnalysis from '@/components/dashboards/TacticalAnalysis';
import ShotNetworks from '@/components/dashboards/ShotNetworks';
import ExpectedThreat from '@/components/dashboards/ExpectedThreat';
import PlayerMatchAnalysis from '@/components/dashboards/PlayerMatchAnalysis';
import OpponentAnalysis from '@/components/dashboards/OpponentAnalysis';
import PerformanceTrends from '@/components/dashboards/PerformanceTrends';
import PlayerComparison from '@/components/dashboards/PlayerComparison';
import MatchInsights from '@/components/dashboards/MatchInsights';

export default function Home() {
  const { season } = useSeason();

  return (
    <Container maxW="container.xl" py={8}>
      <Tabs colorScheme="arsenal" variant="line">
        <TabList overflowX="auto" overflowY="hidden">
          <Tab>📊 Season Overview</Tab>
          <Tab>⚽ Match Detail</Tab>
          <Tab>👤 Player Stats</Tab>
          <Tab>📈 Tactical Analysis</Tab>
          <Tab>🔗 Shot Networks</Tab>
          <Tab>📍 Expected Threat</Tab>
          <Tab>🔥 Player Match</Tab>
          <Tab>🆚 Opponent Analysis</Tab>
          <Tab>📉 Performance Trends</Tab>
          <Tab>⚖️ Player Comparison</Tab>
          <Tab>💡 Match Insights</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <SeasonOverview season={season} />
          </TabPanel>
          <TabPanel>
            <MatchDetail season={season} />
          </TabPanel>
          <TabPanel>
            <PlayerStats season={season} />
          </TabPanel>
          <TabPanel>
            <TacticalAnalysis season={season} />
          </TabPanel>
          <TabPanel>
            <ShotNetworks season={season} />
          </TabPanel>
          <TabPanel>
            <ExpectedThreat season={season} />
          </TabPanel>
          <TabPanel>
            <PlayerMatchAnalysis season={season} />
          </TabPanel>
          <TabPanel>
            <OpponentAnalysis season={season} />
          </TabPanel>
          <TabPanel>
            <PerformanceTrends season={season} />
          </TabPanel>
          <TabPanel>
            <PlayerComparison season={season} />
          </TabPanel>
          <TabPanel>
            <MatchInsights season={season} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  );
}
