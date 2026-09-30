import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sidebar } from './components/layout/Sidebar';
import { TopHeader } from './components/layout/TopHeader';
import { WelcomePage } from './pages/WelcomePage';
import { DashboardPage } from './pages/DashboardPage';
import { SimulationStudioPage } from './pages/SimulationStudioPage';
import { ScenarioLabPage } from './pages/ScenarioLabPage';
import { AcademyPage } from './pages/AcademyPage';
import { AssessmentsPage } from './pages/AssessmentsPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { DevDiagnosticsModal } from './components/dev/DevDiagnosticsModal';
import './App.css';

const PageLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const [isDebugOpen, setIsDebugOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  React.useEffect(() => {
    const handleFullscreen = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreen);
    return () => document.removeEventListener('fullscreenchange', handleFullscreen);
  }, []);

  const getPageTitle = (path: string) => {
    switch (path) {
      case '/dashboard': return 'Command Center';
      case '/simulation': return 'Simulation Studio';
      case '/scenarios': return 'Scenario Lab';
      case '/academy': return 'Hadoop Academy';
      case '/assessments': return 'Assessments';
      case '/history': return 'History & Insights';
      case '/settings': return 'Settings';
      default: return 'TEDDY Platform';
    }
  };

  const mockState = {
    session: { session_id: 'ses_demo_123', status: 'ACTIVE', current_topic: 'HDFS Architecture' },
    user: { user_id: 'usr_evaluator', display_name: 'Evaluator Account' },
    simulation: { system: 'HDFS', status: 'IDLE', current_stage: 'INITIALIZATION' }
  };

  if (isFullscreen) {
    return (
      <div style={{ width: '100vw', height: '100vh', backgroundColor: '#070a12', overflow: 'hidden' }}>
        {children}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#070a12' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopHeader
          title={getPageTitle(location.pathname)}
          onOpenDebugModal={() => setIsDebugOpen(true)}
        />
        <main style={{ flex: 1, overflowY: 'auto' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
              style={{ height: '100%' }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      <DevDiagnosticsModal
        isOpen={isDebugOpen}
        onClose={() => setIsDebugOpen(false)}
        state={mockState}
      />
    </div>
  );
};

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/welcome" element={<WelcomePage />} />
        <Route
          path="/*"
          element={
            <PageLayout>
              <Routes>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/simulation" element={<SimulationStudioPage />} />
                <Route path="/scenarios" element={<ScenarioLabPage />} />
                <Route path="/academy" element={<AcademyPage />} />
                <Route path="/assessments" element={<AssessmentsPage />} />
                <Route path="/history" element={<HistoryPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </PageLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
