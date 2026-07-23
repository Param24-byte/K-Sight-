'use client';
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import axios from 'axios';

// Fix for default marker icon in Next.js + Leaflet
const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconShadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

interface FIR {
  fir_id: string;
  type: string;
  date: string;
  location_name: string;
  lat: number;
  lng: number;
}

export default function IntelligenceMap() {
  const [firs, setFirs] = useState<FIR[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real environment, handle error state and loading better
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    axios.get(`${API_URL}/api/v1/intelligence/firs`)
      .then(res => {
        if (Array.isArray(res.data)) {
          setFirs(res.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Map Data Error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-4 text-white">Loading Map Intelligence...</div>;

  // Center on Bengaluru roughly
  return (
    <div className="h-full w-full rounded-xl overflow-hidden border border-slate-700 shadow-2xl">
      <MapContainer center={[12.9716, 77.5946]} zoom={11} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        <MarkerClusterGroup chunkedLoading>
          {firs.map((fir, idx) => (
            <Marker key={idx} position={[fir.lat, fir.lng]} icon={icon}>
              <Popup className="bg-slate-800 text-slate-100 p-2 rounded">
                <strong className="text-red-400">{fir.type}</strong><br />
                ID: {fir.fir_id}<br />
                Loc: {fir.location_name}<br />
                Date: {new Date(fir.date).toLocaleDateString()}
              </Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      </MapContainer>
    </div>
  );
}
