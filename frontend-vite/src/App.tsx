import { Container, Tabs, TabList, TabPanels, Tab, TabPanel, Box } from '@chakra-ui/react'
import Header from './components/Header'
import Footer from './components/Footer'
import { SeasonProvider, useSeason } from './contexts/SeasonContext'
import SeasonOverview from './components/dashboards/SeasonOverview'
import MatchDetail from './components/dashboards/MatchDetail'
import PlayerStats from './components/dashboards/PlayerStats'
import TacticalAnalysis from './components/dashboards/TacticalAnalysis'
import ShotNetworks from './components/dashboards/ShotNetworks'
import ExpectedThreat from './components/dashboards/ExpectedThreat'
import PlayerMatchAnalysis from './components/dashboards/PlayerMatchAnalysis'
import OpponentAnalysis from './components/dashboards/OpponentAnalysis'
import PerformanceTrends from './components/dashboards/PerformanceTrends'
import PlayerComparison from './components/dashboards/PlayerComparison'
import MatchInsights from './components/dashboards/MatchInsights'

function AppContent() {
  const { season } = useSeason()
  const currentSeason = season || '2024-25'

  return (
    <Box minH="100vh">
      <Header />
      <Container maxW="container.xl" py={8}>
        <Tabs
          colorScheme="arsenal"
          variant="line"
        >
          <TabList
            overflowX="auto"
            overflowY="hidden"
            flexWrap="wrap"
            css={{
              '&::-webkit-scrollbar': {
                height: '6px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'rgba(255, 255, 255, 0.05)',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#EF0107',
                borderRadius: '3px',
              },
            }}
          >
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
              <SeasonOverview season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <MatchDetail season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <PlayerStats season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <TacticalAnalysis season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <ShotNetworks season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <ExpectedThreat season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <PlayerMatchAnalysis season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <OpponentAnalysis season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <PerformanceTrends season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <PlayerComparison season={currentSeason} />
            </TabPanel>
            <TabPanel>
              <MatchInsights season={currentSeason} />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Container>
      <Footer />
    </Box>
  )
}

function App() {
  return (
    <SeasonProvider>
      <AppContent />
    </SeasonProvider>
  )
}

export default App
