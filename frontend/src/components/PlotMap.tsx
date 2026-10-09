import { CircleMarker, MapContainer, Popup, TileLayer, Tooltip } from "react-leaflet";
import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";

import { listProperties } from "../api";
import { bestScore, type Property } from "../types";

function colorForScore(s: number) {
  if (s >= 75) return "var(--color-positive)";
  if (s >= 50) return "var(--color-warning)";
  return "var(--color-negative)";
}

export default function PlotMap({ activeId, highlightIds }: { activeId?: string; highlightIds?: string[] }) {
  const { data: plots = [] } = useQuery<Property[]>({
    queryKey: ["properties"], queryFn: listProperties,
  });

  return (
    <MapContainer
      center={[38.8, 23.5]}
      zoom={6}
      style={{ height: "100%", width: "100%" }}
      scrollWheelZoom
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {plots.map((p) => {
        const top = bestScore(p);
        const isActive = activeId === p.property_id;
        const isHighlighted = highlightIds?.includes(p.property_id);
        return (
          <CircleMarker
            key={p.property_id}
            center={[p.location.latitude, p.location.longitude]}
            radius={isActive ? 16 : isHighlighted ? 13 : 10}
            pathOptions={{
              color: colorForScore(top.value),
              fillColor: colorForScore(top.value),
              fillOpacity: 0.55,
              weight: isActive || isHighlighted ? 3 : 2,
            }}
            className="plot-marker"
          >
            <Tooltip direction="top" offset={[0, -8]} opacity={1} permanent>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "0.08em" }}>
                {p.plot_name.toUpperCase()} · {top.value.toFixed(0)}
              </span>
            </Tooltip>
            <Popup>
              <div style={{ minWidth: 220, fontFamily: "var(--font-sans)" }}>
                <div className="terminal-label">{p.region}</div>
                <div style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>{p.plot_name}</div>
                <div style={{ fontSize: 11, marginTop: 6, opacity: 0.75 }}>
                  Best: <strong>{top.label}</strong> · {top.value.toFixed(1)}/100
                </div>
                <div style={{ fontSize: 11, marginTop: 4 }}>
                  Price €{(p.price_eur / 1e6).toFixed(2)}M · {(p.area_m2 / 1000).toFixed(0)}k m²
                </div>
                {p.suggested_crops?.length > 0 && (
                  <div style={{ fontSize: 10, marginTop: 6, opacity: 0.6 }}>
                    Crops: {p.suggested_crops.slice(0, 4).join(", ")}
                  </div>
                )}
                <Link
                  to="/plots/$plotId"
                  params={{ plotId: p.property_id }}
                  style={{
                    display: "inline-block", marginTop: 10, padding: "4px 10px",
                    background: "var(--color-primary)", color: "var(--color-primary-foreground)",
                    textDecoration: "none", fontSize: 11, fontWeight: 600, borderRadius: 4,
                  }}
                >
                  Open brief →
                </Link>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
