import React from 'react';

import Sidebar from './components/Sidebar';
import Header from './components/Header';
import MainContent from './components/MainContent';

function App() {
  return (
    <div className="flex h-screen w-full bg-[var(--bg-primary)]">
      {/* Sidebar - Chat Interface */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 h-full w-full overflow-hidden">
        <Header />
        <MainContent />
      </div>
    </div>
  );
}

export default App;
