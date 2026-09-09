import { useState, useEffect } from 'react';
import { Check, X, Edit2, ShieldAlert } from 'lucide-react';

interface Transfer {
  id: string;
  from: string;
  to: string;
  equipment: string;
  type: string;
  grade_multiplier: number;
  status: string;
}

interface Target {
  id: string;
  name: string;
  priority_score: number;
  band: string;
  distance_km: number;
  status: string;
}

export default function DecisionConsole() {
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [targets, setTargets] = useState<Target[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/api/decision/tier1').then(res => res.json()),
      fetch('http://localhost:8000/api/decision/tier2').then(res => res.json())
    ]).then(([tier1Data, tier2Data]) => {
      setTransfers(tier1Data.transfers);
      setTargets(tier2Data.targets);
      setLoading(false);
    }).catch(err => {
      console.error("Failed to fetch decision data", err);
      setLoading(false);
    });
  }, []);

  const handleAction = (id: string, action: string, listType: 'transfer' | 'target') => {
    fetch('http://localhost:8000/api/decision/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transfer_id: id, action: action })
    })
    .then(res => res.json())
    .then(data => {
      setActionMessage(data.message);
      if (listType === 'transfer') {
        setTransfers(transfers.map(t => t.id === id ? { ...t, status: action } : t));
      } else {
        setTargets(targets.map(t => t.id === id ? { ...t, status: action } : t));
      }
      setTimeout(() => setActionMessage(''), 3000);
    });
  };

  if (loading) return <div className="flex-center" style={{ height: '400px' }}>Loading Decision Engine...</div>;

  return (
    <div>
      <h2 style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Component 3: Two-Tiered Decision Engine</span>
        <span style={{ fontSize: '0.875rem', fontWeight: 'normal' }} className="text-secondary">
          Human Approval Governance Layer
        </span>
      </h2>
      <p className="text-secondary mb-4">
        Equipment reallocation schedules and ranked exploration targets with [Accept], [Modify], and [Reject] controls. The AI never dispatches machinery autonomously.
      </p>

      {actionMessage && (
        <div style={{ padding: '12px', background: 'rgba(16, 185, 129, 0.2)', border: '1px solid var(--success)', color: '#fff', borderRadius: '8px', marginBottom: '16px', textAlign: 'center' }}>
          {actionMessage}
        </div>
      )}

      <div style={{ display: 'grid', gap: '32px' }}>
        {/* Tier 1 */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, color: 'var(--accent)' }}>Tier 1: Immediate Fleet Reallocation</h3>
            <span style={{ background: 'rgba(255,255,255,0.1)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', color: '#cbd5e1' }}>DAYS TO WEEKS</span>
          </div>
          


          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {transfers.map(t => (
              <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--panel-border)', borderRadius: '12px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>{t.equipment}</span>
                    <span style={{ background: 'var(--accent)', color: 'white', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>{t.type}</span>
                    <span style={{ color: '#10b981', fontSize: '0.85rem' }}>{t.grade_multiplier}x Grade Multiplier</span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                    Move from <strong>{t.from}</strong> to <strong>{t.to}</strong>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {t.status === 'Pending' ? (
                    <>
                      <button className="btn btn-success flex-center" onClick={() => handleAction(t.id, 'Accepted', 'transfer')} title="Accept"><Check size={16} /></button>
                      <button className="btn flex-center" style={{ background: 'rgba(255,255,255,0.1)', color: 'white' }} onClick={() => handleAction(t.id, 'Modified', 'transfer')} title="Modify"><Edit2 size={16} /></button>
                      <button className="btn btn-danger flex-center" onClick={() => handleAction(t.id, 'Rejected', 'transfer')} title="Reject"><X size={16} /></button>
                    </>
                  ) : (
                    <span style={{ 
                      padding: '6px 12px', 
                      borderRadius: '8px', 
                      background: t.status === 'Accepted' ? 'rgba(16, 185, 129, 0.2)' : t.status === 'Rejected' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255,255,255,0.1)',
                      color: t.status === 'Accepted' ? '#10b981' : t.status === 'Rejected' ? '#ef4444' : 'white',
                      fontWeight: 600,
                      fontSize: '0.875rem'
                    }}>
                      {t.status}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tier 2 */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, color: '#f59e0b' }}>Tier 2: Strategic Exploration Ranking</h3>
            <span style={{ background: 'rgba(255,255,255,0.1)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', color: '#cbd5e1' }}>MONTHS TO YEARS</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {targets.map(t => (
              <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--panel-border)', borderRadius: '12px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>{t.name}</span>
                    <span style={{ 
                      background: t.band === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)', 
                      color: t.band === 'High' ? '#fca5a5' : '#fcd34d', 
                      padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' 
                    }}>{t.band} Prospectivity</span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                    Priority Score: <strong style={{ color: '#fff' }}>{t.priority_score}</strong> | Distance to Infrastructure: <strong>{t.distance_km} km</strong>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {t.status === 'Pending' ? (
                    <>
                      <button className="btn btn-success flex-center" onClick={() => handleAction(t.id, 'Accepted', 'target')} title="Accept"><Check size={16} /></button>
                      <button className="btn flex-center" style={{ background: 'rgba(255,255,255,0.1)', color: 'white' }} onClick={() => handleAction(t.id, 'Modified', 'target')} title="Modify"><Edit2 size={16} /></button>
                      <button className="btn btn-danger flex-center" onClick={() => handleAction(t.id, 'Rejected', 'target')} title="Reject"><X size={16} /></button>
                    </>
                  ) : (
                    <span style={{ 
                      padding: '6px 12px', 
                      borderRadius: '8px', 
                      background: t.status === 'Accepted' ? 'rgba(16, 185, 129, 0.2)' : t.status === 'Rejected' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255,255,255,0.1)',
                      color: t.status === 'Accepted' ? '#10b981' : t.status === 'Rejected' ? '#ef4444' : 'white',
                      fontWeight: 600,
                      fontSize: '0.875rem'
                    }}>
                      {t.status}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
