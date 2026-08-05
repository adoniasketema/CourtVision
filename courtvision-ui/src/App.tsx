import { useStore } from './store/useStore';
import { UploadScreen } from './components/UploadScreen';
import { Sidebar } from './components/layout/Sidebar';
import { Topbar } from './components/layout/Topbar';
import { VideoTab } from './components/video/VideoTab';
import { TeamTab } from './components/team/TeamTab';
import { ReportsTab } from './components/reports/ReportsTab';

function App() {
  const processingComplete = useStore(state => state.processingComplete);
  const currentTab = useStore(state => state.currentTab);

  if (!processingComplete) {
    return <UploadScreen />;
  }

  return (
    <div className="flex h-screen bg-charcoal-900 text-gray-100 overflow-hidden font-sans selection:bg-brand selection:text-white">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden bg-charcoal-950/30">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6 relative">
          {currentTab === 'video' && <VideoTab />}
          {currentTab === 'team' && <TeamTab />}
          {currentTab === 'reports' && <ReportsTab />}
        </main>
      </div>
    </div>
  );
}

export default App;
