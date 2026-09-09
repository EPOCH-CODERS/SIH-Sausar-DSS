import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { AlertCircle } from 'lucide-react';

interface ForecastData {
  week: string;
  forecast: number;
  target: number;
}

interface MineForecast {
  mine: string;
  data: ForecastData[];
}

export default function ProductionTracker() {
  const [forecasts, setForecasts] = useState<MineForecast[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMine, setSelectedMine] = useState<string>('Kandri');

  useEffect(() => {
    fetch('http://localhost:8000/api/forecast')
      .then(res => res.json())
      .then(data => {
        setForecasts(data.forecasts);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch forecast data", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="flex-center" style={{ height: '400px' }}>Loading Forecast Data...</div>;

  const currentMineData = forecasts.find(f => f.mine === selectedMine)?.data || [];
  
  // Find weeks where forecast is below target (shortfalls)
  const shortfalls = currentMineData.filter(d => d.forecast < d.target);

  return (
    <div>
      <h2 style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Component 2: Production Forecasting</span>
        <span style={{ fontSize: '0.875rem', fontWeight: 'normal' }} className="text-secondary">
          XGBoost Regressor • Weekly Resolution
        </span>
      </h2>
      <p className="text-secondary mb-4">
        Multi-mine time-series chart of forecasted vs target production with automated shortfall deficit alerts.
      </p>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
        {forecasts.map(f => (
          <button 
            key={f.mine}
            className={`btn ${selectedMine === f.mine ? 'btn-primary' : ''}`}
            style={{ 
              background: selectedMine === f.mine ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
              color: selectedMine === f.mine ? '#fff' : 'var(--text-secondary)',
              border: '1px solid var(--panel-border)'
            }}
            onClick={() => setSelectedMine(f.mine)}
          >
            {f.mine}
          </button>
        ))}
      </div>

      <div className="grid-cols-2" style={{ gridTemplateColumns: '3fr 1fr' }}>
        <div style={{ height: '400px', padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', border: '1px solid var(--panel-border)' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={currentMineData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="week" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Legend />
              <Line type="monotone" dataKey="target" stroke="#10b981" strokeWidth={2} name="Statutory Target (Tonnes)" strokeDasharray="5 5" />
              <Line type="monotone" dataKey="forecast" stroke="#3b82f6" strokeWidth={3} name="AI Forecast (Tonnes)" activeDot={{ r: 8 }} />
              
              {/* Highlight shortfalls */}
              {shortfalls.map((s, idx) => (
                <ReferenceLine key={idx} x={s.week} stroke="#ef4444" strokeDasharray="3 3" />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
            <h3 style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.1rem' }}>
              <AlertCircle size={20} />
              Automated Alerts
            </h3>
            {shortfalls.length > 0 ? (
              <ul style={{ listStylePosition: 'inside', color: '#fca5a5', fontSize: '0.9rem' }}>
                {shortfalls.map((s, idx) => (
                  <li key={idx} style={{ marginBottom: '8px' }}>
                    <strong>{s.week}:</strong> Forecast ({s.forecast}T) is below target ({s.target}T). Deficit: <strong>{s.target - s.forecast}T</strong>.
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ color: '#86efac', fontSize: '0.9rem' }}>No shortfalls forecasted for this mine. On track to meet targets.</p>
            )}
          </div>
          
          <div style={{ padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', border: '1px solid var(--panel-border)', flexGrow: 1 }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>Model Insights</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              The XGBoost regressor incorporates real-time IMD rainfall data and equipment active uptime percentages to predict these production figures. 
              <br/><br/>
              It natively handles non-linear interactions (e.g., monsoon flooding compounding with hoist maintenance) better than LSTMs on sparse mining logs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
