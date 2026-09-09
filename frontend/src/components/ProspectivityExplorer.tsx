import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface Mine {
  name: string;
  lat: number;
  lon: number;
  type: string;
  band: string;
}

export default function ProspectivityExplorer() {
  const [mines, setMines] = useState<Mine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/prospectivity')
      .then(res => res.json())
      .then(data => {
        setMines(data.mines);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch prospectivity data", err);
        setLoading(false);
      });
  }, []);

  const getMarkerColor = (band: string) => {
    switch (band) {
      case 'High': return '#ef4444'; // Red
      case 'Medium': return '#f59e0b'; // Amber
      case 'Low': return '#3b82f6'; // Blue
      default: return '#94a3b8';
    }
  };

  if (loading) return <div className="flex-center" style={{ height: '400px' }}>Loading Map Data...</div>;

  return (
    <div>
      <h2 style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Component 1: Mineral Prospectivity Mapping</span>
        <span style={{ fontSize: '0.875rem', fontWeight: 'normal' }} className="text-secondary">
          Random Forest • Sausar Belt
        </span>
      </h2>
      <p className="text-secondary mb-4">
        Interactive map displaying High/Medium/Low prospectivity zones with tree-agreement uncertainty opacity and MOIL mine markers.
      </p>

      <div style={{ height: '500px', width: '100%', borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--panel-border)' }}>
        <MapContainer center={[21.5, 79.5]} zoom={9} style={{ height: '100%', width: '100%', background: '#0b0f19' }}>
          {/* Using a dark map tile layer to fit the theme */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          
          {mines.map((mine, idx) => (
            <CircleMarker 
              key={idx} 
              center={[mine.lat, mine.lon]}
              pathOptions={{ 
                color: getMarkerColor(mine.band),
                fillColor: getMarkerColor(mine.band),
                fillOpacity: mine.band === 'High' ? 0.95 : (mine.band === 'Medium' ? 0.70 : 0.40) // Tree agreement opacity
              }}
              radius={mine.band === 'High' ? 12 : 8}
            >
              <Tooltip permanent={mine.band === 'High'} direction="top" opacity={0.9}>
                {mine.name}
              </Tooltip>
              <Popup>
                <div style={{ color: '#000' }}>
                  <strong>{mine.name}</strong><br/>
                  Type: {mine.type}<br/>
                  Prospectivity: {mine.band}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      
      <div className="mt-4 flex-center" style={{ gap: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '16px', height: '16px', borderRadius: '50%', background: '#ef4444', opacity: 0.95 }}></div>
          <span className="text-secondary">High</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '16px', height: '16px', borderRadius: '50%', background: '#f59e0b', opacity: 0.70 }}></div>
          <span className="text-secondary">Medium</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '16px', height: '16px', borderRadius: '50%', background: '#3b82f6', opacity: 0.40 }}></div>
          <span className="text-secondary">Low</span>
        </div>
      </div>
    </div>
  );
}
