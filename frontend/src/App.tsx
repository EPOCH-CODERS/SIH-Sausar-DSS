import { useState, useEffect } from 'react';
import { Map, Activity, Layers, AlertTriangle } from 'lucide-react';
import ProspectivityExplorer from './components/ProspectivityExplorer';
import ProductionTracker from './components/ProductionTracker';
import DecisionConsole from './components/DecisionConsole';

function App() {
  const [activeTab, setActiveTab] = useState('prospectivity');

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>

      
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', letterSpacing: '-0.5px' }}>
          MOIL Decision Support System
        </h1>
        <p className="text-secondary">
          AI/ML and Space Technology to Identify Manganese Reserves and Overcome Production Shortfalls
        </p>
      </header>

      <div className="nav-bar">
        <button 
          className={`nav-tab flex-center ${activeTab === 'prospectivity' ? 'active' : ''}`}
          onClick={() => setActiveTab('prospectivity')}
          style={{ gap: '8px' }}
        >
          <Map size={18} />
          Prospectivity Explorer
        </button>
        <button 
          className={`nav-tab flex-center ${activeTab === 'production' ? 'active' : ''}`}
          onClick={() => setActiveTab('production')}
          style={{ gap: '8px' }}
        >
          <Activity size={18} />
          Production Tracker
        </button>
        <button 
          className={`nav-tab flex-center ${activeTab === 'decision' ? 'active' : ''}`}
          onClick={() => setActiveTab('decision')}
          style={{ gap: '8px' }}
        >
          <Layers size={18} />
          Decision Console
        </button>
      </div>

      <main className="glass-panel" style={{ minHeight: '600px' }}>
        {activeTab === 'prospectivity' && <ProspectivityExplorer />}
        {activeTab === 'production' && <ProductionTracker />}
        {activeTab === 'decision' && <DecisionConsole />}
      </main>
    </div>
  );
}

export default App;
