"use client";

import { useEffect, useRef } from "react";

interface InteractiveMapProps {
  activeCityIndex: number | null;
  onSelectCity: (index: number) => void;
}

const DESTINATIONS = [
  {
    name: "Tokyo, Japan",
    coords: [35.6762, 139.6503] as [number, number],
    zoom: 12,
    description: "Tsukiji Outer Market, teamLab Borderless, and Senso-ji Temple.",
  },
  {
    name: "Shibuya & Harajuku",
    coords: [35.6580, 139.7016] as [number, number],
    zoom: 13.5,
    description: "Shibuya Crossing, Takeshita Street, and Yoyogi Park.",
  },
];

export default function InteractiveMap({ activeCityIndex, onSelectCity }: InteractiveMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    let map: any;
    let isUnmounted = false;

    // Load Leaflet dynamically inside useEffect to ensure it only runs in the browser
    import("leaflet").then((L) => {
      if (isUnmounted || !mapContainerRef.current) return;

      // Safe check: If a map instance already exists, remove it first
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove();
        } catch (e) {
          console.warn("Failed to remove previous map instance", e);
        }
        mapInstanceRef.current = null;
      }

      // Safe check: Reset DOM marker that Leaflet uses to track initialization
      const container = mapContainerRef.current;
      if (container && (container as any)._leaflet_id) {
        (container as any)._leaflet_id = null;
      }

      // Fix Leaflet's default marker icon relative asset resolution issue
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
        iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
      });

      // SVG icon generator using signature Sage accent color
      const createCustomIcon = (isActive: boolean) => {
        const color = isActive ? "#5C755E" : "#7C9A7E"; // Darker sage green when active
        const scale = isActive ? 1.25 : 1.0;
        const shadowOpacity = isActive ? 0.4 : 0.2;
        const html = `
          <div style="transform: scale(${scale}); transform-origin: bottom center; display: flex; flex-direction: column; align-items: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.15));">
              <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2ZM12 11.5C10.62 11.5 9.5 10.38 9.5 9C9.5 7.62 10.62 6.5 12 6.5C13.38 6.5 14.5 7.62 14.5 9C14.5 10.38 13.38 11.5 12 11.5Z" fill="${color}"/>
            </svg>
            <div style="background-color: #000; width: 10px; height: 3px; border-radius: 50%; filter: blur(1.5px); opacity: ${shadowOpacity}; margin-top: -1px;"></div>
          </div>
        `;
        return L.divIcon({
          html,
          className: "custom-leaflet-marker",
          iconSize: [32, 32],
          iconAnchor: [16, 32],
          popupAnchor: [0, -32],
        });
      };

      const defaultCenter = [35.668, 139.68] as [number, number]; // Centered between Tokyo and Shibuya

      map = L.map(container, {
        center: defaultCenter,
        zoom: 12.2,
        zoomControl: false, // Standard controls look clunky, we will customize or place carefully
        scrollWheelZoom: false, // Do not hijack user mouse scrolling
      });

      mapInstanceRef.current = map;

      // Add high-quality custom Zoom control to the bottom right
      L.control.zoom({ position: "bottomright" }).addTo(map);

      // Esri Light Gray Canvas Base (sleek, minimalist, premium gray aesthetic)
      L.tileLayer("https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
        attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
        maxZoom: 16,
      }).addTo(map);

      // Esri Light Gray Canvas Reference (renders all labels in English globally)
      L.tileLayer("https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}", {
        maxZoom: 16,
      }).addTo(map);

      // Force size invalidation to fix the standard Leaflet "partial container render" layout bug
      setTimeout(() => {
        if (map && !isUnmounted) {
          map.invalidateSize();
        }
      }, 150);

      // Plot the markers
      const markers = DESTINATIONS.map((dest, idx) => {
        const marker = L.marker(dest.coords, {
          icon: createCustomIcon(activeCityIndex === idx),
        }).addTo(map);

        const popupContent = `
          <div style="font-family: inherit; padding: 4px; max-width: 190px;">
            <h4 style="font-weight: 600; font-size: 13px; margin: 0 0 3px 0; color: #1A1A1A;">${dest.name}</h4>
            <p style="font-size: 11px; margin: 0; color: #6B6B6B; line-height: 1.35;">${dest.description}</p>
          </div>
        `;

        marker.bindPopup(popupContent, {
          closeButton: false,
          className: "custom-map-popup-container",
        });

        // Trigger active panel update on click
        marker.on("click", () => {
          onSelectCity(idx);
        });

        return marker;
      });

      markersRef.current = markers;
    });

    return () => {
      isUnmounted = true;
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove();
        } catch (e) {
          console.warn("Failed to remove map instance on unmount", e);
        }
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update map viewport when activeCityIndex updates
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Force map to recalculate container size on index updates to prevent layout clipping
    map.invalidateSize();

    import("leaflet").then((L) => {
      const createCustomIcon = (isActive: boolean) => {
        const color = isActive ? "#5C755E" : "#7C9A7E";
        const scale = isActive ? 1.25 : 1.0;
        const shadowOpacity = isActive ? 0.4 : 0.2;
        const html = `
          <div style="transform: scale(${scale}); transform-origin: bottom center; display: flex; flex-direction: column; align-items: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.15));">
              <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2ZM12 11.5C10.62 11.5 9.5 10.38 9.5 9C9.5 7.62 10.62 6.5 12 6.5C13.38 6.5 14.5 7.62 14.5 9C14.5 10.38 13.38 11.5 12 11.5Z" fill="${color}"/>
            </svg>
            <div style="background-color: #000; width: 10px; height: 3px; border-radius: 50%; filter: blur(1.5px); opacity: ${shadowOpacity}; margin-top: -1px;"></div>
          </div>
        `;
        return L.divIcon({
          html,
          className: "custom-leaflet-marker",
          iconSize: [32, 32],
          iconAnchor: [16, 32],
          popupAnchor: [0, -32],
        });
      };

      // Recalculate popup and custom styles
      markersRef.current.forEach((marker, idx) => {
        marker.setIcon(createCustomIcon(activeCityIndex === idx));
        if (activeCityIndex === idx) {
          // Open popup with slight delay to allow smooth panning first
          setTimeout(() => {
            if (mapInstanceRef.current) marker.openPopup();
          }, 350);
        } else {
          marker.closePopup();
        }
      });

      if (activeCityIndex !== null && activeCityIndex >= 0) {
        const dest = DESTINATIONS[activeCityIndex];
        map.setView(dest.coords, dest.zoom, { animate: true, duration: 1.0 });
      } else {
        const defaultCenter = [35.668, 139.68] as [number, number];
        map.setView(defaultCenter, 12.2, { animate: true, duration: 1.0 });
      }
    });
  }, [activeCityIndex]);

  return (
    <div className="w-full h-full rounded-2xl overflow-hidden relative border border-border shadow-card bg-surface">
      <div ref={mapContainerRef} className="w-full h-full z-0" />
      
      {/* Aesthetic Overlays */}
      <div className="absolute top-3 left-3 z-[1000] bg-surface/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-border text-[11px] text-text-primary font-medium shadow-sm flex items-center gap-1.5 select-none pointer-events-none">
        <span className="h-2 w-2 rounded-full bg-accent-sage animate-pulse" />
        <span>Live Interactive Trip Showcase</span>
      </div>

      {activeCityIndex !== null && activeCityIndex >= 0 && (
        <button
          onClick={() => onSelectCity(-1)}
          className="absolute top-3 right-3 z-[1000] bg-surface/90 backdrop-blur-md hover:bg-surface hover:text-text-primary text-[11px] font-semibold text-text-secondary px-3 py-1.5 rounded-xl border border-border shadow-sm transition-all duration-200 active:scale-95 cursor-pointer"
        >
          Reset View
        </button>
      )}

      {/* Styled Popup override rules */}
      <style jsx global>{`
        .custom-map-popup-container .leaflet-popup-content-wrapper {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(8px);
          border-radius: 12px;
          border: 1px solid var(--border, #EBEBEB);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
          padding: 2px;
        }
        .custom-map-popup-container .leaflet-popup-tip {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(8px);
          border: 1px solid var(--border, #EBEBEB);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        .leaflet-container {
          font-family: inherit;
        }
        .custom-leaflet-marker {
          background: none !important;
          border: none !important;
        }
      `}</style>
    </div>
  );
}
