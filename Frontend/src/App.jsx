import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from "recharts";


// No icon library — every indicator below (status dot, up/down change, loading
// state) is built from plain text glyphs or CSS, not an icon package.

/* ============================== DESIGN TOKENS ============================== */


const C = {
  navy: "#201B14", ink: "#1E1A14", sub: "#6B6153", paper: "#F7F4EC", card: "#FFFFFF",
  line: "#E6DFCF", green: "#3F6B34", greenBg: "#EBF0E1", red: "#9C3B2E", redBg: "#F5E6E1",
  amber: "#A6752C", amberBg: "#F5ECD9", blue: "#B1452B", blueBg: "#F5E5DC",
};

const FONT_HEAD = "'IBM Plex Sans', system-ui, sans-serif"; 
const FONT_BODY = "'Public Sans', system-ui, sans-serif"; 
const FONT_MONO = "'IBM Plex Mono', ui-monospace, monospace";

/* ============================== API CONFIG ==============================
   ONE base URL, built once, used everywhere below. Your FastAPI backend
   must have CORS enabled for this frontend's origin:
     from fastapi.middleware.cors import CORSMiddleware
     app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
============================================================================ */
const API_BASE_URL = "http://127.0.0.1:8000";

async function apiFetch(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    let detail = "";
    try { const j = await res.json(); detail = j.detail || ""; } catch (e) { /* ignore */ }
    throw new Error(detail || `Request failed (HTTP ${res.status})`);
  }
  return res.json();
}

// Some endpoints in the spec are shown as a single example object but are
// described as feeding a trend graph / "50 values" — almost certainly arrays
// in the real response. This normalizes either shape into an array so the
// UI doesn't break if the real backend returns one object instead of a list.


function formatDate(dateString) {
  if (!dateString) return "";
  const [year, month, day] = dateString.slice(0, 10).split("-");
  return `${day}-${month}-${year}`;
}


function asArray(data) {
  if (Array.isArray(data)) return data;
  if (data && typeof data === "object") return [data];
  return [];
}

const api = {
  index: () => apiFetch("/api/index"),
  trends: () => apiFetch("/api/trends"),
  routes: () => apiFetch("/api/routes"),
  routeIndex: (routeId) => apiFetch(`/api/routes/${routeId}`),
  airlines: () => apiFetch("/api/airlines"),
  airlineIndex: (airlineId) => apiFetch(`/api/airlines/${airlineId}`),
  bookingWindows: () => apiFetch("/api/booking-windows"),
  contributions: (date, dimensionType) =>
    apiFetch(`/api/contributions?index_date=${date}${dimensionType ? `&dimension_type=${dimensionType}` : ""}`),
};

/* ============================== DATA HOOK ============================== */
function useApiData(fetchFn, deps) {
  const [state, setState] = useState({ loading: true, error: null, data: null });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState({ loading: true, error: null, data: null });
    fetchFn()
      .then((data) => { if (!cancelled) setState({ loading: false, error: null, data }); })
      .catch((err) => { if (!cancelled) setState({ loading: false, error: err.message || "Unable to connect to backend", data: null }); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return { ...state, retry: () => setTick((t) => t + 1) };
}

/* ============================== SHARED UI ============================== */
function Card({ children, style }) {
  return <div style={{ background: C.card, border: `1px solid ${C.line}`, borderRadius: 2, padding: 20, ...style }}>{children}</div>;
}

function ChangeTag({ value }) {
  if (value === null || value === undefined) return <span style={{ color: C.sub, fontSize: 13 }}>—</span>;
  const up = value >= 0;
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 3, fontFamily: FONT_MONO, fontWeight: 600, fontSize: 13, color: up ? C.green : C.red }}>
      {up ? "▲" : "▼"}
      {up ? "+" : ""}{value.toFixed(2)}%
    </span>
  );
}

function LoadingState({ label = "Loading...", rows = 3 }) {
  return (
    <Card>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="ai-skeleton-bar" style={{
            height: 12, borderRadius: 2, width: i === rows - 1 ? "55%" : "100%",
          }} />
        ))}
      </div>
      <div style={{ fontSize: 11, color: C.sub, marginTop: 10, fontFamily: FONT_MONO }}>{label}</div>
    </Card>
  );
}

function ErrorState({ message, onRetry }) {
  return (
    <Card style={{ borderColor: C.red }}>
      <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
        <span style={{ fontFamily: FONT_MONO, fontWeight: 700, fontSize: 16, color: C.red, lineHeight: 1, flexShrink: 0, marginTop: 2 }}>!</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: FONT_HEAD, fontWeight: 600, fontSize: 14, color: C.ink }}>Unable to connect to backend</div>
          <div style={{ fontSize: 13, color: C.sub, marginTop: 4 }}>{message}</div>
          <div style={{ fontSize: 12, color: C.sub, marginTop: 10, background: C.paper, padding: 10, borderRadius: 2, border: `1px solid ${C.line}`, fontFamily: FONT_MONO, lineHeight: 1.6 }}>
            Checklist:<br />
            1. Backend running at <span style={{ color: C.ink }}>{API_BASE_URL}</span>?<br />
            2. CORS enabled in main.py for this frontend's origin?<br />
            3. Endpoint path/shape matches what this frontend expects?
          </div>
          <button onClick={onRetry} style={{
            marginTop: 12, fontFamily: FONT_MONO, fontSize: 12, fontWeight: 600, padding: "7px 14px",
            background: C.navy, color: "#fff", border: "none", borderRadius: 2, cursor: "pointer",
          }}>Retry</button>
        </div>
      </div>
    </Card>
  );
}

function EmptyState({ message = "No data available." }) {
  return <Card style={{ color: C.sub, fontSize: 13, textAlign: "center" }}>{message}</Card>;
}

function ChartTooltip({ xLabel, xField, yField, yLabel, formatX }) {
  return function Inner({ active, payload }) {
    if (!active || !payload || !payload.length) return null;
    const d = payload[0].payload;

    const formattedX =
      formatX
        ? formatX(d[xField])
        : xField === "index_date"
          ? formatDate(d[xField])
          : d[xField];

    return (
      <div style={{ background: C.navy, color: "#fff", padding: "10px 12px", borderRadius: 2, fontFamily: FONT_MONO, fontSize: 12, lineHeight: 1.6 }}>
        <div style={{ fontFamily: FONT_BODY, fontWeight: 600, marginBottom: 4 }}>
          {xLabel}: {formattedX}
        </div>
        <div>{yLabel}: {d[yField]}</div>
      </div>
    );
  };
}


/* ============================== BACKEND STATUS ============================== */
function useBackendStatus() {
  const check = useCallback(() => {
    api.index().catch(() => {});
  }, []);

  useEffect(() => {
    check();
  }, [check]);

  return { check };
}

/* ============================== HELPERS ============================== */
function latestByType(records, type) {
  const filtered = (records || []).filter((r) => r.index_type === type);
  if (!filtered.length) return null;
  return [...filtered].sort((a, b) => new Date(b.index_date) - new Date(a.index_date))[0];
}

function formatRoute(r) {
  return `${r.source_city} → ${r.destination_city}`;
}

function formatAirline(a) {
  // airline_code can be null per spec — never assume it's a string
  return a.airline_code ? `${a.airline_name} (${a.airline_code})` : a.airline_name;
}

/* ============================== A. OVERVIEW / HOME ============================== */
function Overview() {
  const { loading, error, data, retry } = useApiData(api.index, []);
  const records = asArray(data);
  const latest = useMemo(() => latestByType(records, "daily") || records[records.length - 1] || null, [records]);
  const recent = useMemo(
    () => [...records].filter((r) => r.index_type === "daily").sort((a, b) => new Date(a.index_date) - new Date(b.index_date)).slice(-14),
    [records]
  );

  const todayISO = new Date().toISOString().slice(0, 10);
  const { data: contribData } = useApiData(() => api.contributions(latest?.index_date || todayISO), [latest?.index_date]);
  const topContributors = asArray(contribData).slice(0, 5);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 24,
            fontWeight: 600,
            letterSpacing: "0.1px",
            lineHeight: 1.25,
            color: C.ink,
            margin: 0,
          }}
        >
          Overview
        </h1>
      </div>

      {loading && <LoadingState label="Loading..." />}
      {error && <ErrorState message={error} onRetry={retry} />}
      {!loading && !error && !latest && <EmptyState />}

      {!loading && !error && latest && (
        <>
          <Card style={{ background: C.navy, border: "none", color: "#fff" }}>
            <span style={{ fontSize: 12, color: "#C9BEA8", letterSpacing: 0.5 }}>CURRENT AIRFARE PRICE INDEX</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginTop: 6, flexWrap: "wrap" }}>
              <span style={{ fontFamily: FONT_MONO, fontSize: 42, fontWeight: 700 }}>{latest.index_value}</span>
              <ChangeTag value={latest.percentage_change} />
              <span style={{ color: "#C9BEA8", fontSize: 13 }}>as of {latest.index_date}</span>
            </div>
          </Card>

          {recent.length > 1 && (
            <Card>
              <h3 style={{ fontFamily: FONT_HEAD, fontSize: 15, fontWeight: 600, margin: "0 0 12px" }}>Recent Index Movement</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={recent} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                  <CartesianGrid stroke={C.line} vertical={false} />
                  <XAxis
                    dataKey="index_date"
                    tickFormatter={formatDate}
                    tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }}
                    axisLine={{ stroke: C.line }}
                    tickLine={false}
                    minTickGap={30}
                  />
                  <YAxis tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }} axisLine={false} tickLine={false} width={40} />
                  <ReferenceLine y={100} stroke={C.sub} strokeDasharray="4 4" />
                  <Tooltip content={ChartTooltip({ xLabel: "Date", xField: "index_date", yField: "index_value", yLabel: "Index" })} />
                  <Line type="monotone" dataKey="index_value" stroke={C.blue} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          )}

          {topContributors.length > 0 && (
            <Card>
              <h3 style={{ fontFamily: FONT_HEAD, fontSize: 15, fontWeight: 600, margin: "0 0 4px" }}>Quick Contribution Summary</h3>
              <ContributionBars items={topContributors} />
            </Card>
          )}
        </>
      )}
    </div>
  );
}

/* ============================== B. TRENDS ============================== */
function Trends() {
  const [type, setType] = useState("daily");
  const { loading, error, data, retry } = useApiData(api.trends, []);
  const records = asArray(data);
  const filtered = useMemo(
    () => records.filter((r) => r.index_type === type).sort((a, b) => new Date(a.index_date) - new Date(b.index_date)),
    [records, type]
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 24,
            fontWeight: 600,
            letterSpacing: "0.1px",
            lineHeight: 1.25,
            color: C.ink,
            margin: 0,
          }}
        >
          Trends
        </h1>
      </div>

      <Card>
        <div style={{ display: "flex", gap: 6 }}>
          {["daily", "weekly", "monthly"].map((t) => (
            <button key={t} onClick={() => setType(t)} style={{
              fontFamily: FONT_MONO, fontSize: 12, fontWeight: 600, padding: "7px 14px", borderRadius: 2,
              border: `1px solid ${t === type ? C.navy : C.line}`, background: t === type ? C.navy : "transparent",
              color: t === type ? "#fff" : C.sub, cursor: "pointer", textTransform: "uppercase",
            }}>{t}</button>
          ))}
        </div>
      </Card>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={retry} />}
      {!loading && !error && filtered.length === 0 && <EmptyState message={`No ${type} records available.`} />}
      {!loading && !error && filtered.length > 0 && (
        <Card>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={filtered} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.line} vertical={false} />
              <XAxis
                dataKey="index_date"
                tickFormatter={formatDate}
                tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }}
                axisLine={{ stroke: C.line }}
                tickLine={false}
                minTickGap={30}
              />
              <YAxis tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }} axisLine={false} tickLine={false} width={40} />
              <ReferenceLine y={100} stroke={C.sub} strokeDasharray="4 4" />
              <Tooltip content={ChartTooltip({ xLabel: "Date", xField: "index_date", yField: "index_value", yLabel: "Index" })} />
              <Line type="monotone" dataKey="index_value" stroke={C.blue} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}

/* ============================== C. ROUTE ANALYSIS ============================== */
function RouteAnalysis() {
  const { loading: loadingRoutes, error: errorRoutes, data: routesData, retry: retryRoutes } = useApiData(api.routes, []);
  const routes = asArray(routesData);

  // Starting Destination options = every unique source_city the backend actually has.
  const startingOptions = useMemo(() => [...new Set(routes.map((r) => r.source_city))].sort(), [routes]);
  const [startCity, setStartCity] = useState("");
  useEffect(() => { if (!startCity && startingOptions.length) setStartCity(startingOptions[0]); }, [startingOptions, startCity]);

  // Ending Destination options = ONLY destinations the backend pairs with the
  // selected starting city — never the full city list, and never the
  // starting city itself (belt-and-braces filter, even though the route data
  // structurally never has source === destination).
  const endingOptions = useMemo(
    () => routes.filter((r) => r.source_city === startCity && r.destination_city !== startCity).map((r) => r.destination_city),
    [routes, startCity]
  );
  const [endCity, setEndCity] = useState("");
  // Whenever the starting city changes, the previous ending choice may no
  // longer be valid for this new pair — reset to the first valid option.
  useEffect(() => {
    if (!endingOptions.includes(endCity)) setEndCity(endingOptions[0] || "");
  }, [endingOptions, endCity]);

  const selectedRoute = routes.find((r) => r.source_city === startCity && r.destination_city === endCity);

  const { loading, error, data, retry } = useApiData(
    () => (selectedRoute ? api.routeIndex(selectedRoute.route_id) : Promise.resolve([])),
    [selectedRoute?.route_id]
  );
  const records = useMemo(
    () => asArray(data).sort((a, b) => new Date(a.index_date) - new Date(b.index_date)),
    [data]
  );
  const latest = records[records.length - 1];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 24,
            fontWeight: 600,
            letterSpacing: "0.1px",
            lineHeight: 1.25,
            color: C.ink,
            margin: 0,
          }}
        >
          Route Analysis
        </h1>
      </div>

      {loadingRoutes && <LoadingState label="Loading routes..." />}
      {errorRoutes && <ErrorState message={errorRoutes} onRetry={retryRoutes} />}

      {!loadingRoutes && !errorRoutes && (
        <Card>
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
            <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: C.sub, fontWeight: 500, minWidth: 200 }}>
              Starting Destination
              <select value={startCity} onChange={(e) => setStartCity(e.target.value)}
                style={{ fontFamily: FONT_BODY, fontSize: 13, padding: "8px 10px", borderRadius: 2, border: `1px solid ${C.line}` }}>
                {startingOptions.length === 0 && <option value="">No routes found</option>}
                {startingOptions.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </label>
            <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: C.sub, fontWeight: 500, minWidth: 200 }}>
              Ending Destination
              <select value={endCity} onChange={(e) => setEndCity(e.target.value)}
                style={{ fontFamily: FONT_BODY, fontSize: 13, padding: "8px 10px", borderRadius: 2, border: `1px solid ${C.line}` }}>
                {endingOptions.length === 0 && <option value="">No destinations from {startCity}</option>}
                {endingOptions.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </label>
          </div>
        </Card>
      )}

      {!loadingRoutes && !errorRoutes && selectedRoute && (
        <>
          {loading && <LoadingState label={`Loading ${formatRoute(selectedRoute)}...`} />}
          {error && <ErrorState message={error} onRetry={retry} />}
          {!loading && !error && records.length === 0 && <EmptyState />}
          {!loading && !error && records.length > 0 && (
            <Card>
              <h3 style={{ fontFamily: FONT_HEAD, fontSize: 15, fontWeight: 600, margin: "0 0 4px" }}>{formatRoute(selectedRoute)}</h3>
              {latest && (
                <div style={{ display: "flex", gap: 20, marginBottom: 14 }}>
                  <div>
                    <div style={{ fontSize: 11, color: C.sub, textTransform: "uppercase" }}>Index</div>
                    <div style={{ fontFamily: FONT_MONO, fontSize: 18, fontWeight: 600 }}>{latest.index_value}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: C.sub, textTransform: "uppercase" }}>Change</div>
                    <ChangeTag value={latest.percentage_change} />
                  </div>
                </div>
              )}
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={records} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                  <CartesianGrid stroke={C.line} vertical={false} />
                  <XAxis
                    dataKey="index_date"
                    tickFormatter={formatDate}
                    tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }}
                    axisLine={{ stroke: C.line }}
                    tickLine={false}
                    minTickGap={30}
                  />
                  <YAxis tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }} axisLine={false} tickLine={false} width={40} />
                  <ReferenceLine y={100} stroke={C.sub} strokeDasharray="4 4" />
                  <Tooltip content={ChartTooltip({ xLabel: "Date", xField: "index_date", yField: "index_value", yLabel: "Index" })} />
                  <Line type="monotone" dataKey="index_value" stroke={C.blue} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

/* ============================== D. AIRLINE ANALYSIS ============================== */
function AirlineAnalysis() {
  const { loading: loadingAirlines, error: errorAirlines, data: airlinesData, retry: retryAirlines } = useApiData(api.airlines, []);
  const airlines = asArray(airlinesData);
  const [selectedId, setSelectedId] = useState(null);
  useEffect(() => { if (!selectedId && airlines.length) setSelectedId(airlines[0].airline_id); }, [airlines, selectedId]);
  const selectedAirline = airlines.find((a) => a.airline_id === selectedId);

  const { loading, error, data, retry } = useApiData(
    () => (selectedId ? api.airlineIndex(selectedId) : Promise.resolve([])),
    [selectedId]
  );
  const records = useMemo(
    () => asArray(data).sort((a, b) => new Date(a.index_date) - new Date(b.index_date)),
    [data]
  );
  const latest = records[records.length - 1];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 24,
            fontWeight: 600,
            letterSpacing: "0.1px",
            lineHeight: 1.25,
            color: C.ink,
            margin: 0,
          }}
        >
          Airline Analysis
        </h1>
      </div>

      {loadingAirlines && <LoadingState label="Loading airlines..." />}
      {errorAirlines && <ErrorState message={errorAirlines} onRetry={retryAirlines} />}

      {!loadingAirlines && !errorAirlines && (
        <Card>
          <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: C.sub, fontWeight: 500, maxWidth: 280 }}>
            Select Airline
            <select value={selectedId || ""} onChange={(e) => setSelectedId(Number(e.target.value))}
              style={{ fontFamily: FONT_BODY, fontSize: 13, padding: "8px 10px", borderRadius: 2, border: `1px solid ${C.line}` }}>
              {airlines.length === 0 && <option value="">No airlines found</option>}
              {airlines.map((a) => <option key={a.airline_id} value={a.airline_id}>{formatAirline(a)}</option>)}
            </select>
          </label>
        </Card>
      )}

      {!loadingAirlines && !errorAirlines && selectedAirline && (
        <>
          {loading && <LoadingState label={`Loading ${formatAirline(selectedAirline)}...`} />}
          {error && <ErrorState message={error} onRetry={retry} />}
          {!loading && !error && records.length === 0 && <EmptyState />}
          {!loading && !error && records.length > 0 && (
            <Card>
              <h3 style={{ fontFamily: FONT_HEAD, fontSize: 15, fontWeight: 600, margin: "0 0 4px" }}>{formatAirline(selectedAirline)}</h3>
              {latest && (
                <div style={{ display: "flex", gap: 20, marginBottom: 14 }}>
                  <div>
                    <div style={{ fontSize: 11, color: C.sub, textTransform: "uppercase" }}>Index</div>
                    <div style={{ fontFamily: FONT_MONO, fontSize: 18, fontWeight: 600 }}>{latest.index_value}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: C.sub, textTransform: "uppercase" }}>Change</div>
                    <ChangeTag value={latest.percentage_change} />
                  </div>
                </div>
              )}
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={records} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                  <CartesianGrid stroke={C.line} vertical={false} />
                  <XAxis
                    dataKey="index_date"
                    tickFormatter={formatDate}
                    tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }}
                    axisLine={{ stroke: C.line }}
                    tickLine={false}
                    minTickGap={30}
                  />
                  <YAxis tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }} axisLine={false} tickLine={false} width={40} />
                  <ReferenceLine y={100} stroke={C.sub} strokeDasharray="4 4" />
                  <Tooltip content={ChartTooltip({ xLabel: "Date", xField: "index_date", yField: "index_value", yLabel: "Index" })} />
                  <Line type="monotone" dataKey="index_value" stroke={C.blue} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

/* ============================== E. BOOKING WINDOW ANALYSIS ============================== */
function BookingWindowAnalysis() {
  const { loading, error, data, retry } = useApiData(api.bookingWindows, []);
  // IMPORTANT: sort/display by days_before_departure, NEVER booking_window_id —
  // the spec is explicit that IDs are not sequential with days.
  const records = useMemo(
    () => asArray(data).sort((a, b) => a.days_before_departure - b.days_before_departure),
    [data]
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 24,
            fontWeight: 600,
            letterSpacing: "0.1px",
            lineHeight: 1.25,
            color: C.ink,
            margin: 0,
          }}
        >
          Booking Window Analysis
        </h1>
      </div>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={retry} />}
      {!loading && !error && records.length === 0 && <EmptyState />}
      {!loading && !error && records.length > 0 && (
        <>
          <Card>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={records} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                <CartesianGrid stroke={C.line} vertical={false} />
                <XAxis dataKey="days_before_departure" tickFormatter={(d) => `T+${d}`}
                  tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }} axisLine={{ stroke: C.line }} tickLine={false} />
                <YAxis tick={{ fontFamily: FONT_MONO, fontSize: 10, fill: C.sub }} axisLine={false} tickLine={false} width={40} />
                <ReferenceLine y={100} stroke={C.sub} strokeDasharray="4 4" />
                <Tooltip content={ChartTooltip({ xLabel: "Booking Window", xField: "days_before_departure", yField: "index_value", yLabel: "Index", formatX: (d) => `T+${d}` })} />
                <Bar dataKey="index_value" fill={C.blue} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
          <Card style={{ padding: 0, overflow: "hidden" }}>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: FONT_BODY, fontSize: 13, minWidth: 420 }}>
                <thead>
                  <tr>
                    {["Booking Window", "Index", "Change"].map((h) => (
                      <th key={h} style={{ textAlign: "left", padding: "10px 20px", color: C.sub, fontWeight: 600, fontSize: 11, letterSpacing: 0.4, textTransform: "uppercase", borderBottom: `1px solid ${C.line}` }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {records.map((r) => (
                    <tr key={r.booking_window_id} style={{ borderBottom: `1px solid ${C.line}` }}>
                      <td style={{ padding: "10px 20px", fontFamily: FONT_MONO, fontWeight: 600 }}>T+{r.days_before_departure}</td>
                      <td style={{ padding: "10px 20px", fontFamily: FONT_MONO }}>{r.index_value}</td>
                      <td style={{ padding: "10px 20px" }}><ChangeTag value={r.percentage_change} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}

/* ============================== 3. WHY DID THE INDEX CHANGE? ============================== */
function ContributionBars({ items }) {
  const max = Math.max(1, ...items.map((i) => Math.abs(i.contribution)));
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {items.map((item) => {
        const up = item.contribution >= 0;
        const widthPct = (Math.abs(item.contribution) / max) * 100;
        return (
          <div key={item.dimension_value} style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ width: 130, fontSize: 12, color: C.ink, flexShrink: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.dimension_value}</span>
            <div style={{ flex: 1, background: C.paper, borderRadius: 2, height: 16, position: "relative" }}>
              <div style={{ width: `${widthPct}%`, height: "100%", borderRadius: 2, background: up ? C.green : C.red }} />
            </div>
            <span style={{ width: 64, textAlign: "right", fontFamily: FONT_MONO, fontSize: 12, fontWeight: 600, color: up ? C.green : C.red }}>
              {up ? "+" : ""}{item.contribution.toFixed(2)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function WhyDidItChange() {
  const minDate = "2023-01-16";
  const maxDate = "2023-03-06";

  const [date, setDate] = useState(maxDate);
  const [confirmedDate, setConfirmedDate] = useState(maxDate);

  const airlineQ = useApiData(() => api.contributions(confirmedDate, "airline"), [confirmedDate]);
  const routeQ = useApiData(() => api.contributions(confirmedDate, "route"), [confirmedDate]);
  
  const indexQ = useApiData(
    () => api.index(confirmedDate),
    [confirmedDate]
  );

  const indexData = asArray(indexQ.data);
  const selectedIndex = indexData.find(
  (item) =>
    item.index_date === confirmedDate &&
    item.index_type === "daily"
);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1
            style={{
              fontFamily: FONT_HEAD,
              fontSize: 24,
              fontWeight: 600,
              letterSpacing: "0.1px",
              lineHeight: 1.25,
              color: C.ink,
              margin: 0,
            }}
          >
            Why Did the Index Change?
          </h1>
        <p style={{ color: C.sub, fontSize: 13, marginTop: 4 }}>
        </p>
      </div>

      <Card>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "flex-end" }}>
          <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: C.sub, fontWeight: 500 }}>
            Index Date
            <input
              type="date"
              value={date}
              min={minDate}
              max={maxDate}
              onChange={(e) => setDate(e.target.value)}
              style={{
                fontFamily: FONT_BODY,
                fontSize: 13,
                padding: "8px 10px",
                borderRadius: 2,
                border: `1px solid ${C.line}`,
              }}
            />
          </label>
          <button onClick={() => setConfirmedDate(date)} style={{
            fontFamily: FONT_MONO, fontSize: 13, fontWeight: 600, padding: "9px 18px",
            background: C.navy, color: "#fff", border: "none", borderRadius: 2, cursor: "pointer",
          }}>VIEW CONTRIBUTIONS</button>
        </div>
      </Card>


      <Card>
        <div style={{ display: "flex", gap: 40, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontSize: 11, color: C.sub, marginBottom: 6 }}>
              OVERALL AIRFARE PRICE INDEX
            </div>
            {indexQ.loading ? (
              <LoadingState />
            ) : indexQ.error ? (
              <ErrorState message={indexQ.error} onRetry={indexQ.retry} />
            ) : (
              <div style={{
                fontFamily: FONT_HEAD,
                fontSize: 28,
                fontWeight: 700,
                color: C.ink,
              }}>
                {selectedIndex ? Number(selectedIndex.index_value).toFixed(2) : "—"}
              </div>
            )}
          </div>
          
          <div>
            <div style={{ fontSize: 11, color: C.sub, marginBottom: 6 }}>
              PERCENTAGE CHANGE
            </div>
            {indexQ.loading ? (
              <LoadingState />
            ) : indexQ.error ? (
              <ErrorState message={indexQ.error} onRetry={indexQ.retry} />
            ) : (
              <div style={{
                fontFamily: FONT_HEAD,
                fontSize: 28,
                fontWeight: 700,
                color: selectedIndex && Number(selectedIndex.percentage_change) >= 0
                  ? C.green
                  : C.red,
              }}>
                {selectedIndex
                  ? `${Number(selectedIndex.percentage_change) >= 0 ? "+" : ""}${Number(selectedIndex.percentage_change).toFixed(2)}%`
                  : "—"}
              </div>
            )}
          </div>
        </div>
      </Card>


      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
        <Card>
          <h3 style={{ fontFamily: FONT_HEAD, fontSize: 14, fontWeight: 600, margin: "0 0 14px" }}>Top Airline Contributors</h3>
          {airlineQ.loading && <LoadingState />}
          {airlineQ.error && <ErrorState message={airlineQ.error} onRetry={airlineQ.retry} />}
          {!airlineQ.loading && !airlineQ.error && asArray(airlineQ.data).length === 0 && <EmptyState />}
          {!airlineQ.loading && !airlineQ.error && asArray(airlineQ.data).length > 0 && (
            <ContributionBars items={asArray(airlineQ.data)} />
          )}
        </Card>
        <Card>
          <h3 style={{ fontFamily: FONT_HEAD, fontSize: 14, fontWeight: 600, margin: "0 0 14px" }}>Top Route Contributors</h3>
          {routeQ.loading && <LoadingState />}
          {routeQ.error && <ErrorState message={routeQ.error} onRetry={routeQ.retry} />}
          {!routeQ.loading && !routeQ.error && asArray(routeQ.data).length === 0 && <EmptyState />}
          {!routeQ.loading && !routeQ.error && asArray(routeQ.data).length > 0 && (
            <ContributionBars items={asArray(routeQ.data)} />
          )}
        </Card>
      </div>
    </div>
  );
}



/* ============================== About ============================== */


function About() {
  const sectionStyle = {
    fontFamily: FONT_HEAD,
    fontSize: 19,
    fontWeight: 700,
    color: C.ink,
    margin: 0,
    marginBottom: 10,
  };

  const textStyle = {
    fontFamily: FONT_BODY,
    fontSize: 16,
    lineHeight: 1.7,
    color: C.ink,
    margin: 0,
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 28,
        width: "100%",
        maxWidth: 1000,
        textAlign: "left",
      }}
    >
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 26,
            fontWeight: 600,
            letterSpacing: "0.1px",
            lineHeight: 1.25,
            color: C.ink,
            margin: 0,
          }}
        >
          About AeroIndex
        </h1>

        <p
          style={{
            fontFamily: FONT_BODY,
            fontSize: 19,
            color: C.sub,
            marginTop: 8,
            marginBottom: 0,
          }}
        >
          Airfare Price Index Dashboard for India
        </p>
      </div>

      <div>
        <p style={{ ...textStyle, marginBottom: 10 }}>
          AeroIndex is an airfare price index dashboard developed for
          Smart India Hackathon (SIH26056) to monitor and analyze changes
          in airfares across routes, airlines, and booking windows.
        </p>

        <p style={textStyle}>
          The dashboard provides an index-based view of airfare movement.
          It is designed for analysis and monitoring, not for ticket
          booking or cheapest-ticket recommendations.
        </p>
      </div>
      <br />
      <div>
        <h2 style={sectionStyle}>Project</h2>
        <p style={textStyle}>
          Smart India Hackathon<br />
          Problem Statement: SIH26056
        </p>
      </div>
      <br />
      <div>
        <h2 style={sectionStyle}>Current Data Source</h2>

        <p style={{ ...textStyle, marginBottom: 8 }}>
          The current prototype uses the following Kaggle dataset:
        </p>

        <a
          href="https://www.kaggle.com/datasets/yashdharme36/airfare-ml-predicting-flight-fares"
          target="_blank"
          rel="noreferrer"
          style={{
            fontFamily: FONT_BODY,
            fontSize: 13,
            color: C.navy,
            fontWeight: 700,
            textDecoration: "underline",
          }}
        >
          Airfare ML: Predicting Flight Fares — Kaggle ↗
        </a>
      </div>
      <br />
      <div>
        <h2 style={sectionStyle}>Current Data Coverage</h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            gap: 20,
            fontFamily: FONT_BODY,
            fontSize: 15,
            lineHeight: 1.6,
            color: C.ink,
          }}
        >
          <div>
            <div style={{ color: C.sub, marginBottom: 3 }}>Date range</div>
            <strong>16-01-2023 to 06-03-2023</strong>
          </div>

          <div>
            <div style={{ color: C.sub, marginBottom: 3 }}>Airlines</div>
            <strong>9</strong>
          </div>

          <div>
            <div style={{ color: C.sub, marginBottom: 3 }}>Routes</div>
            <strong>42</strong>
          </div>

          <div>
            <div style={{ color: C.sub, marginBottom: 3 }}>Booking windows</div>
            <strong>T+1 to T+50</strong>
          </div>
        </div>
      </div>
      <br />
      <div>
        <h2 style={sectionStyle}>Calculation Methodology</h2>

        <div style={textStyle}>
          <div style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 700, marginBottom: 6 }}>
              Base Period:
            </div>
            <div>
              The first 7-day base period (16-01-2023 to 22-01-2023) is used
              as the reference period, with the index referenced to 100.
            </div>
          </div>
          <div style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 700, marginBottom: 6 }}>
              Daily Index:
            </div>
            <div>
              Median airfare is calculated for each route on each date. Each
              route's fare is compared with its base-period median fare to
              obtain a price relative. The average of these route-level price
              relatives gives the overall daily index.
            </div>
          </div>

          <div style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 700, marginBottom: 6 }}>
              Weekly & Monthly Index:
            </div>
            <div>
              Weekly and monthly indices are calculated as the average of the
              corresponding daily index values within each week or month.
            </div>
          </div>

          <div style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 700, marginBottom: 6 }}>
              Percentage Change:
            </div>
            <div>
              Index movement is measured against the previous corresponding
              period, such as the previous day, week, month, route value, or
              airline value.
            </div>
          </div>

          <div style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 700, marginBottom: 6 }}>
              Booking Windows:
            </div>
            <div>
              T+1 to T+50 are analysed individually. T+1 is the reference
              window, and each window's median fare is compared with the T+1
              median fare.
            </div>
          </div>

          <div>
            <div style={{ fontWeight: 700, marginBottom: 6 }}>
              Change Attribution:
            </div>
            <div>
              Route contributions use the same route-level price relatives
              used in the daily index, allowing daily index changes to be
              explained through individual route movements. Airline
              contributions provide a separate airline-level breakdown.
            </div>
          </div>
        </div>
      </div>
      <br />
      <div>
        <h2 style={sectionStyle}>Dashboard Scope</h2>

        <div
          style={{
            ...textStyle,
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            columnGap: 40,
            rowGap: 6,
          }}
        >
          <div>• Overall Airfare Price Index</div>
          <div>• Historical index trends</div>
          <div>• Route-wise analysis</div>
          <div>• Airline-wise analysis</div>
          <div>• Booking-window analysis</div>
          <div>• Index change contribution analysis</div>
        </div>
      </div>

      <div
        style={{
          borderTop: `1px solid ${C.line}`,
          paddingTop: 16,
        }}
      >
        <p
          style={{
            fontFamily: FONT_BODY,
            fontSize: 12,
            lineHeight: 1.7,
            color: C.sub,
            margin: 0,
          }}
        >
          <strong>Prototype Data Notice:</strong> The current dashboard
          uses historical Kaggle data as prototype data. The intended
          production system will use permitted airline, NDC, OTA/API,
          or other authorized data sources.
        </p>
      </div>
    </div>
  );
}





/* ============================== NAV / LAYOUT ============================== */
const NAV = [
  { key: "overview", label: "Overview" },
  { key: "trends", label: "Trends" },
  { key: "routes", label: "Route Analysis" },
  { key: "airlines", label: "Airline Analysis" },
  { key: "booking", label: "Booking Window" },
  { key: "why", label: "Why Did It Change?" },
  { key: "about", label: "About" },
];

export default function App() {
  const [page, setPage] = useState("overview");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { check } = useBackendStatus();


  return (
    <div style={{ fontFamily: FONT_BODY, background: C.paper, minHeight: "100vh", color: C.ink, display: "block", width: "100%" }}>
        <aside
          style={{ width: 220, background: C.navy, flexShrink: 0, padding: "20px 14px", display: "flex", flexDirection: "column", gap: 24 }}
          className={`ai-sidebar ${mobileMenuOpen ? "mobile-open" : ""}`}
        >
        <div>
          <div style={{ fontFamily: FONT_HEAD, fontWeight: 700, fontSize: 16, color: "#fff" }}>MENU</div>
        </div>
        <nav style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {NAV.map((n) => {
            const activeItem = page === n.key;
            return (
              <button
                key={n.key}
                onClick={() => {
                  setPage(n.key);
                  setMobileMenuOpen(false);
                }}
                style={{
                  padding: "9px 12px", borderRadius: 2,
                  background: activeItem ? "#fff" : "transparent", border: "none", cursor: "pointer",
                  textAlign: "left", color: activeItem ? C.navy : "#C9BEA8", fontSize: 13,
                  fontWeight: activeItem ? 700 : 500,
                }}>{n.label}</button>
            );
          })}
        </nav>
      </aside>

      <div style={{ flex: 1, minWidth: 0 }}>
        <header style={{
          height: 56,
          borderBottom: `1px solid ${C.line}`,
          background: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 20px",
          position: "relative",
        }}>
          <button
            className="ai-menu-button"
            onClick={() => setMobileMenuOpen((open) => !open)}
          >
            {mobileMenuOpen ? "✕" : "☰"}
          </button>
        
          <div style={{
            position: "absolute",
            left: "50%",
            transform: "translateX(-50%)",
            fontFamily: FONT_HEAD,
            fontWeight: 700,
            fontSize: 32,
            color: C.ink,
          }}>
            AeroIndex
          </div>
        
          <div style={{
            marginLeft: "auto",
            display: "flex",
            alignItems: "center",
            gap: 14,
          }}>
            
            
            <button
              onClick={check}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                background: C.ink,
                border: `1px solid ${C.ink}`,
                color: "#fff",
                borderRadius: 2,
                padding: "6px 12px",
                cursor: "pointer",
                fontSize: 12,
                fontFamily: FONT_MONO,
                fontWeight: 600,
              }}
            >
              ↻ Refresh
            </button>
          </div>
        </header>

        {status === "offline" && (
          <div style={{ background: C.redBg, borderBottom: `1px solid #E0C4BC`, padding: "8px 20px", fontSize: 12, color: C.red, fontFamily: FONT_MONO }}>
            Backend not reachable at {API_BASE_URL} — start it, and confirm CORS is enabled for this origin.
          </div>
        )}

        <div style={{ padding: 24, width: "100%", boxSizing: "border-box" }}>
          {page === "overview" && <Overview />}
          {page === "trends" && <Trends />}
          {page === "routes" && <RouteAnalysis />}
          {page === "airlines" && <AirlineAnalysis />}
          {page === "booking" && <BookingWindowAnalysis />}
          {page === "why" && <WhyDidItChange />}
          {page === "about" && <About />}
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600;700&family=Public+Sans:wght@400;500;600&display=swap');
        * { box-sizing: border-box; }
        .ai-skeleton-bar {
          background: linear-gradient(90deg, ${C.line} 25%, #F0EAD9 37%, ${C.line} 63%);
          background-size: 400% 100%;
          animation: ai-shimmer 1.4s ease infinite;
        }
        @keyframes ai-shimmer {
          0% { background-position: 100% 50%; }
          100% { background-position: 0 50%; }
        }

        @media (min-width: 768px) {
          .ai-sidebar {
            position: fixed;
            top: 56px;
            left: -220px;
            height: calc(100vh - 56px);
            z-index: 1000;
            transition: left 0.25s ease;
          }

          .ai-sidebar.mobile-open {
            left: 0 !important;
          }
        }

        @media (max-width: 767px) {
          .ai-sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            z-index: 1000;
            transform: translateX(-100%);
            transition: transform 0.25s ease;
          }

          .ai-sidebar.mobile-open {
            transform: translateX(0);
          }

          .ai-menu-button {
            display: block;
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 2000;
            width: 38px;
            height: 38px;
            border: 1px solid #D8D0C0;
            border-radius: 4px;
            background: #fff;
            color: #1F1B16;
            font-size: 22px;
            cursor: pointer;
          }
        }

        @media (min-width: 768px) {
          .ai-menu-button {
            display: block;
            width: 38px;
            height: 38px;
            border: 1px solid #D8D0C0;
            border-radius: 4px;
            background: #fff;
            color: #1F1B16;
            font-size: 22px;
            cursor: pointer;
          }
        }
      `}</style>
    </div>
  );
}
