import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import {
  RefreshCw,
  LayoutDashboard,
  CalendarDays,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Route as RouteIcon,
  CircleDot,
  AlertTriangle,
} from "lucide-react";

/* ============================== DESIGN TOKENS ============================== */

const C = {
  navy: "#0B1E3D",
  ink: "#101828",
  sub: "#5B6472",
  paper: "#F7F8FA",
  card: "#FFFFFF",
  line: "#E2E5EA",
  green: "#16833B",
  greenBg: "#EAF6EE",
  red: "#C81E3A",
  redBg: "#FCEAEE",
  amber: "#B7791F",
  amberBg: "#FBF3E4",
  blue: "#2054C7",
  blueBg: "#EAF0FD",
};

const FONT_HEAD = "'IBM Plex Sans', system-ui, sans-serif";
const FONT_BODY = "'Inter', system-ui, sans-serif";
const FONT_MONO = "'IBM Plex Mono', ui-monospace, monospace";

/* ============================== API CONFIG ============================== */

const API_BASE = "http://127.0.0.1:8000";

async function apiFetch(path) {
  const res = await fetch(`${API_BASE}${path}`);

  if (!res.ok) {
    let detail = "";

    try {
      const j = await res.json();
      detail = j.detail || "";
    } catch (e) {
      /* ignore */
    }

    throw new Error(detail || `Request failed (HTTP ${res.status})`);
  }

  return res.json();
}

const api = {
  ping: () => apiFetch("/"),
  current: () => apiFetch("/api/current"),
  history: (start, end) =>
    apiFetch(`/api/history?start_date=${start}&end_date=${end}`),
  weekly: () => apiFetch("/api/weekly"),
  monthly: () => apiFetch("/api/monthly"),
  routes: (route) =>
    apiFetch(
      `/api/routes${route ? `?route=${encodeURIComponent(route)}` : ""}`
    ),
};

/* ============================== DATA HOOK ============================== */

function useApiData(fetchFn, deps) {
  const [state, setState] = useState({
    loading: true,
    error: null,
    data: null,
  });

  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;

    setState({
      loading: true,
      error: null,
      data: null,
    });

    fetchFn()
      .then((data) => {
        if (!cancelled) {
          setState({
            loading: false,
            error: null,
            data,
          });
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setState({
            loading: false,
            error: err.message || "Failed to fetch",
            data: null,
          });
        }
      });

    return () => {
      cancelled = true;
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return {
    ...state,
    retry: () => setTick((t) => t + 1),
  };
}

/* ============================== SHARED UI ============================== */

function Pill({ children, tone = "neutral" }) {
  const tones = {
    neutral: {
      bg: C.line,
      fg: C.sub,
    },
    green: {
      bg: C.greenBg,
      fg: C.green,
    },
    red: {
      bg: C.redBg,
      fg: C.red,
    },
    amber: {
      bg: C.amberBg,
      fg: C.amber,
    },
    blue: {
      bg: C.blueBg,
      fg: C.blue,
    },
  };

  const s = tones[tone];

  return (
    <span
      style={{
        background: s.bg,
        color: s.fg,
        fontFamily: FONT_MONO,
        fontSize: 11,
        fontWeight: 600,
        padding: "3px 8px",
        borderRadius: 4,
        letterSpacing: 0.3,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
  );
}

function ChangeTag({ value }) {
  if (value === null || value === undefined) {
    return (
      <span style={{ color: C.sub, fontSize: 13 }}>
        —
      </span>
    );
  }

  const up = value >= 0;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 3,
        fontFamily: FONT_MONO,
        fontWeight: 600,
        fontSize: 13,
        color: up ? C.green : C.red,
      }}
    >
      {up ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
      {up ? "+" : ""}
      {value.toFixed(2)}%
    </span>
  );
}

function Card({ children, style }) {
  return (
    <div
      style={{
        background: C.card,
        border: `1px solid ${C.line}`,
        borderRadius: 6,
        padding: 20,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

function qualityTone(status) {
  if (!status) return "neutral";

  const s = String(status).toLowerCase();

  if (
    s.includes("good") ||
    s.includes("high") ||
    s.includes("ok")
  ) {
    return "green";
  }

  if (
    s.includes("partial") ||
    s.includes("medium")
  ) {
    return "amber";
  }

  if (
    s.includes("poor") ||
    s.includes("low") ||
    s.includes("bad")
  ) {
    return "red";
  }

  return "blue";
}

/* ============================== LOADING / ERROR / EMPTY ============================== */

function LoadingState({
  label = "Loading data from backend...",
}) {
  return (
    <Card
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        color: C.sub,
        fontSize: 13,
      }}
    >
      <RefreshCw
        size={15}
        style={{
          animation: "spin 0.8s linear infinite",
        }}
      />
      {label}
    </Card>
  );
}

function ErrorState({ message, onRetry }) {
  return (
    <Card style={{ borderColor: C.red }}>
      <div
        style={{
          display: "flex",
          gap: 10,
          alignItems: "flex-start",
        }}
      >
        <AlertTriangle
          size={18}
          color={C.red}
          style={{
            flexShrink: 0,
            marginTop: 2,
          }}
        />

        <div style={{ flex: 1 }}>
          <div
            style={{
              fontFamily: FONT_HEAD,
              fontWeight: 600,
              fontSize: 14,
              color: C.ink,
            }}
          >
            Couldn't reach the backend
          </div>

          <div
            style={{
              fontSize: 13,
              color: C.sub,
              marginTop: 4,
            }}
          >
            {message}
          </div>

          <div
            style={{
              fontSize: 12,
              color: C.sub,
              marginTop: 10,
              background: C.paper,
              padding: 10,
              borderRadius: 4,
              border: `1px solid ${C.line}`,
              fontFamily: FONT_MONO,
              lineHeight: 1.6,
            }}
          >
            Checklist:
            <br />
            1. Backend running? →{" "}
            <span style={{ color: C.ink }}>
              python -m uvicorn main:app --reload
            </span>
            <br />
            2. Reachable at{" "}
            <span style={{ color: C.ink }}>
              {API_BASE}
            </span>
            ?
            <br />
            3. CORS enabled in main.py for this frontend's origin?
          </div>

          <button
            onClick={onRetry}
            style={{
              marginTop: 12,
              fontFamily: FONT_MONO,
              fontSize: 12,
              fontWeight: 600,
              padding: "7px 14px",
              background: C.navy,
              color: "#fff",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            Retry
          </button>
        </div>
      </div>
    </Card>
  );
}

function EmptyState({
  message = "No records returned for this query.",
}) {
  return (
    <Card
      style={{
        color: C.sub,
        fontSize: 13,
        textAlign: "center",
      }}
    >
      {message}
    </Card>
  );
}

function TrendTooltip({
  active,
  payload,
  xKey = "date",
  yKey = "airfare_index",
  yLabel = "Index",
}) {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const d = payload[0].payload;

  return (
    <div
      style={{
        background: C.navy,
        color: "#fff",
        padding: "10px 12px",
        borderRadius: 6,
        fontFamily: FONT_MONO,
        fontSize: 12,
        lineHeight: 1.6,
      }}
    >
      <div
        style={{
          fontFamily: FONT_BODY,
          fontWeight: 600,
          marginBottom: 4,
        }}
      >
        {d[xKey]}
      </div>

      <div>
        {yLabel}: {d[yKey]}
      </div>
    </div>
  );
}

/* ============================== BACKEND STATUS ============================== */

function useBackendStatus() {
  const [status, setStatus] = useState("checking");

  const check = useCallback(() => {
    setStatus("checking");

    api
      .ping()
      .then(() => setStatus("online"))
      .catch(() => setStatus("offline"));
  }, []);

  useEffect(() => {
    check();
  }, [check]);

  return {
    status,
    check,
  };
}

/* ============================== OVERVIEW PAGE ============================== */

function Overview() {
  const {
    loading,
    error,
    data,
    retry,
  } = useApiData(api.current, []);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 24,
            fontWeight: 700,
            color: C.ink,
            margin: 0,
          }}
        >
          Airfare Price Index — Live from Backend
        </h1>

        <p
          style={{
            color: C.sub,
            fontSize: 13,
            marginTop: 6,
          }}
        >
          Data below is fetched directly from{" "}
          <code
            style={{
              fontFamily: FONT_MONO,
            }}
          >
            {API_BASE}/api/current
          </code>
          .
        </p>
      </div>

      {loading && (
        <LoadingState label="Fetching current index..." />
      )}

      {error && (
        <ErrorState
          message={error}
          onRetry={retry}
        />
      )}

      {!loading && !error && data && (
        <Card
          style={{
            background: C.navy,
            border: "none",
            color: "#fff",
          }}
        >
          <span
            style={{
              fontSize: 12,
              color: "#AFC1E0",
              letterSpacing: 0.5,
            }}
          >
            AIRFARE PRICE INDEX
          </span>

          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 16,
              marginTop: 6,
              flexWrap: "wrap",
            }}
          >
            <span
              style={{
                fontFamily: FONT_MONO,
                fontSize: 42,
                fontWeight: 700,
              }}
            >
              {data.airfare_index}
            </span>

            <span
              style={{
                color: "#AFC1E0",
                fontSize: 13,
              }}
            >
              as of {data.date}
            </span>
          </div>

          <div
            style={{
              display: "flex",
              gap: 24,
              marginTop: 16,
              flexWrap: "wrap",
            }}
          >
            <div>
              <div
                style={{
                  fontSize: 11,
                  color: "#8CA3CC",
                }}
              >
                COVERAGE
              </div>

              <div
                style={{
                  fontFamily: FONT_MONO,
                  fontSize: 16,
                  fontWeight: 600,
                }}
              >
                {data.coverage_percent}%
              </div>
            </div>

            <div>
              <div
                style={{
                  fontSize: 11,
                  color: "#8CA3CC",
                }}
              >
                QUALITY STATUS
              </div>

              <div style={{ marginTop: 2 }}>
                <Pill
                  tone={qualityTone(
                    data.quality_status
                  )}
                >
                  {data.quality_status}
                </Pill>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

/* ============================== DAILY HISTORY PAGE ============================== */

function DailyHistory() {
  const todayISO = new Date()
    .toISOString()
    .slice(0, 10);

  const thirtyAgo = new Date(
    Date.now() - 30 * 86400000
  )
    .toISOString()
    .slice(0, 10);

  const [start, setStart] = useState(
    thirtyAgo
  );

  const [end, setEnd] = useState(todayISO);

  const [range, setRange] = useState({
    start: thirtyAgo,
    end: todayISO,
  });

  const {
    loading,
    error,
    data,
    retry,
  } = useApiData(
    () =>
      api.history(
        range.start,
        range.end
      ),
    [range.start, range.end]
  );

  const records = data?.records || [];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 22,
            fontWeight: 700,
            color: C.ink,
            margin: 0,
          }}
        >
          Daily Index History
        </h1>

        <p
          style={{
            color: C.sub,
            fontSize: 13,
            marginTop: 4,
          }}
        >
          GET /api/history — pick a date range from your actual imported data.
        </p>
      </div>

      <Card>
        <div
          style={{
            display: "flex",
            gap: 16,
            flexWrap: "wrap",
            alignItems: "flex-end",
          }}
        >
          <label
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 4,
              fontSize: 12,
              color: C.sub,
              fontWeight: 500,
            }}
          >
            Start date

            <input
              type="date"
              value={start}
              onChange={(e) =>
                setStart(e.target.value)
              }
              style={{
                fontFamily: FONT_BODY,
                fontSize: 13,
                padding: "8px 10px",
                borderRadius: 4,
                border: `1px solid ${C.line}`,
              }}
            />
          </label>

          <label
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 4,
              fontSize: 12,
              color: C.sub,
              fontWeight: 500,
            }}
          >
            End date

            <input
              type="date"
              value={end}
              onChange={(e) =>
                setEnd(e.target.value)
              }
              style={{
                fontFamily: FONT_BODY,
                fontSize: 13,
                padding: "8px 10px",
                borderRadius: 4,
                border: `1px solid ${C.line}`,
              }}
            />
          </label>

          <button
            onClick={() =>
              setRange({
                start,
                end,
              })
            }
            style={{
              fontFamily: FONT_MONO,
              fontSize: 13,
              fontWeight: 600,
              padding: "9px 18px",
              background: C.navy,
              color: "#fff",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            LOAD RANGE
          </button>
        </div>
      </Card>

      {loading && <LoadingState />}

      {error && (
        <ErrorState
          message={error}
          onRetry={retry}
        />
      )}

      {!loading &&
        !error &&
        records.length === 0 && (
          <EmptyState message="No daily records in this date range — check the range matches your imported CSV data." />
        )}

      {!loading &&
        !error &&
        records.length > 0 && (
          <>
            <Card>
              <ResponsiveContainer
                width="100%"
                height={260}
              >
                <LineChart
                  data={records}
                  margin={{
                    top: 4,
                    right: 8,
                    left: -8,
                    bottom: 0,
                  }}
                >
                  <CartesianGrid
                    stroke={C.line}
                    vertical={false}
                  />

                  <XAxis
                    dataKey="date"
                    tick={{
                      fontFamily: FONT_MONO,
                      fontSize: 10,
                      fill: C.sub,
                    }}
                    axisLine={{
                      stroke: C.line,
                    }}
                    tickLine={false}
                    minTickGap={30}
                  />

                  <YAxis
                    tick={{
                      fontFamily: FONT_MONO,
                      fontSize: 10,
                      fill: C.sub,
                    }}
                    axisLine={false}
                    tickLine={false}
                    width={36}
                  />

                  <ReferenceLine
                    y={100}
                    stroke={C.sub}
                    strokeDasharray="4 4"
                  />

                  <Tooltip
                    content={<TrendTooltip />}
                  />

                  <Line
                    type="monotone"
                    dataKey="airfare_index"
                    stroke={C.blue}
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            <RecordsTable
              columns={[
                "date",
                "airfare_index",
                "coverage_percent",
                "quality_status",
              ]}
              headers={[
                "Date",
                "Index",
                "Coverage %",
                "Quality",
              ]}
              rows={records}
            />
          </>
        )}
    </div>
  );
}

/* ============================== WEEKLY PAGE ============================== */

function WeeklyIndex() {
  const {
    loading,
    error,
    data,
    retry,
  } = useApiData(api.weekly, []);

  const records = data?.records || [];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 22,
            fontWeight: 700,
            color: C.ink,
            margin: 0,
          }}
        >
          Weekly Index
        </h1>

        <p
          style={{
            color: C.sub,
            fontSize: 13,
            marginTop: 4,
          }}
        >
          GET /api/weekly
        </p>
      </div>

      {loading && <LoadingState />}

      {error && (
        <ErrorState
          message={error}
          onRetry={retry}
        />
      )}

      {!loading &&
        !error &&
        records.length === 0 && (
          <EmptyState />
        )}

      {!loading &&
        !error &&
        records.length > 0 && (
          <>
            <Card>
              <ResponsiveContainer
                width="100%"
                height={260}
              >
                <BarChart
                  data={records}
                  margin={{
                    top: 4,
                    right: 8,
                    left: -8,
                    bottom: 0,
                  }}
                >
                  <CartesianGrid
                    stroke={C.line}
                    vertical={false}
                  />

                  <XAxis
                    dataKey="week"
                    tick={{
                      fontFamily: FONT_MONO,
                      fontSize: 10,
                      fill: C.sub,
                    }}
                    axisLine={{
                      stroke: C.line,
                    }}
                    tickLine={false}
                    minTickGap={20}
                  />

                  <YAxis
                    tick={{
                      fontFamily: FONT_MONO,
                      fontSize: 10,
                      fill: C.sub,
                    }}
                    axisLine={false}
                    tickLine={false}
                    width={36}
                  />

                  <ReferenceLine
                    y={100}
                    stroke={C.sub}
                    strokeDasharray="4 4"
                  />

                  <Tooltip
                    content={
                      <TrendTooltip xKey="week" />
                    }
                  />

                  <Bar
                    dataKey="airfare_index"
                    fill={C.blue}
                    radius={[
                      3,
                      3,
                      0,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <RecordsTable
              columns={[
                "week",
                "airfare_index",
                "week_on_week_change_percent",
              ]}
              headers={[
                "Week",
                "Index",
                "Week-on-Week Change",
              ]}
              rows={records}
              changeCol="week_on_week_change_percent"
            />
          </>
        )}
    </div>
  );
}

/* ============================== MONTHLY PAGE ============================== */

function MonthlyIndex() {
  const {
    loading,
    error,
    data,
    retry,
  } = useApiData(api.monthly, []);

  const records = data?.records || [];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 22,
            fontWeight: 700,
            color: C.ink,
            margin: 0,
          }}
        >
          Monthly Index
        </h1>

        <p
          style={{
            color: C.sub,
            fontSize: 13,
            marginTop: 4,
          }}
        >
          GET /api/monthly
        </p>
      </div>

      {loading && <LoadingState />}

      {error && (
        <ErrorState
          message={error}
          onRetry={retry}
        />
      )}

      {!loading &&
        !error &&
        records.length === 0 && (
          <EmptyState />
        )}

      {!loading &&
        !error &&
        records.length > 0 && (
          <>
            <Card>
              <ResponsiveContainer
                width="100%"
                height={260}
              >
                <BarChart
                  data={records}
                  margin={{
                    top: 4,
                    right: 8,
                    left: -8,
                    bottom: 0,
                  }}
                >
                  <CartesianGrid
                    stroke={C.line}
                    vertical={false}
                  />

                  <XAxis
                    dataKey="month"
                    tick={{
                      fontFamily: FONT_MONO,
                      fontSize: 10,
                      fill: C.sub,
                    }}
                    axisLine={{
                      stroke: C.line,
                    }}
                    tickLine={false}
                  />

                  <YAxis
                    tick={{
                      fontFamily: FONT_MONO,
                      fontSize: 10,
                      fill: C.sub,
                    }}
                    axisLine={false}
                    tickLine={false}
                    width={36}
                  />

                  <ReferenceLine
                    y={100}
                    stroke={C.sub}
                    strokeDasharray="4 4"
                  />

                  <Tooltip
                    content={
                      <TrendTooltip xKey="month" />
                    }
                  />

                  <Bar
                    dataKey="airfare_index"
                    fill={C.navy}
                    radius={[
                      3,
                      3,
                      0,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <RecordsTable
              columns={[
                "month",
                "airfare_index",
                "month_on_month_change_percent",
              ]}
              headers={[
                "Month",
                "Index",
                "Month-on-Month Change",
              ]}
              rows={records}
              changeCol="month_on_month_change_percent"
            />
          </>
        )}
    </div>
  );
}

/* ============================== ROUTES PAGE ============================== */

function RoutesExplorer() {
  const {
    loading: loadingAll,
    error: errorAll,
    data: allData,
    retry: retryAll,
  } = useApiData(
    () => api.routes(),
    []
  );

  const allRecords = allData?.records || [];

  const routeOptions = useMemo(
    () =>
      [
        ...new Set(
          allRecords.map(
            (r) => r.route
          )
        ),
      ].sort(),
    [allRecords]
  );

  const [selected, setSelected] =
    useState(null);

  useEffect(() => {
    if (
      !selected &&
      routeOptions.length
    ) {
      setSelected(routeOptions[0]);
    }
  }, [routeOptions, selected]);

  const {
    loading,
    error,
    data,
    retry,
  } = useApiData(
    () =>
      selected
        ? api.routes(selected)
        : Promise.resolve({
            records: [],
          }),
    [selected]
  );

  const records = data?.records || [];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <div>
        <h1
          style={{
            fontFamily: FONT_HEAD,
            fontSize: 22,
            fontWeight: 700,
            color: C.ink,
            margin: 0,
          }}
        >
          Route-wise Index
        </h1>

        <p
          style={{
            color: C.sub,
            fontSize: 13,
            marginTop: 4,
          }}
        >
          GET /api/routes?route=...
        </p>
      </div>

      {loadingAll && (
        <LoadingState label="Discovering available routes..." />
      )}

      {errorAll && (
        <ErrorState
          message={errorAll}
          onRetry={retryAll}
        />
      )}

      {!loadingAll && !errorAll && (
        <Card>
          <label
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 4,
              fontSize: 12,
              color: C.sub,
              fontWeight: 500,
              maxWidth: 260,
            }}
          >
            Route

            <select
              value={selected || ""}
              onChange={(e) =>
                setSelected(
                  e.target.value
                )
              }
              style={{
                fontFamily: FONT_BODY,
                fontSize: 13,
                padding: "8px 10px",
                borderRadius: 4,
                border: `1px solid ${C.line}`,
              }}
            >
              {routeOptions.length ===
                0 && (
                <option value="">
                  No routes found in database
                </option>
              )}

              {routeOptions.map((r) => (
                <option
                  key={r}
                  value={r}
                >
                  {r}
                </option>
              ))}
            </select>
          </label>
        </Card>
      )}

      {!loadingAll &&
        !errorAll &&
        selected && (
          <>
            {loading && (
              <LoadingState
                label={`Loading ${selected}...`}
              />
            )}

            {error && (
              <ErrorState
                message={error}
                onRetry={retry}
              />
            )}

            {!loading &&
              !error &&
              records.length === 0 && (
                <EmptyState />
              )}

            {!loading &&
              !error &&
              records.length > 0 && (
                <>
                  <Card>
                    <h3
                      style={{
                        fontFamily: FONT_HEAD,
                        fontSize: 15,
                        fontWeight: 600,
                        margin:
                          "0 0 12px",
                      }}
                    >
                      {selected}
                    </h3>

                    <ResponsiveContainer
                      width="100%"
                      height={240}
                    >
                      <LineChart
                        data={records}
                        margin={{
                          top: 4,
                          right: 8,
                          left: -8,
                          bottom: 0,
                        }}
                      >
                        <CartesianGrid
                          stroke={C.line}
                          vertical={false}
                        />

                        <XAxis
                          dataKey="date"
                          tick={{
                            fontFamily:
                              FONT_MONO,
                            fontSize: 10,
                            fill: C.sub,
                          }}
                          axisLine={{
                            stroke: C.line,
                          }}
                          tickLine={false}
                          minTickGap={30}
                        />

                        <YAxis
                          tick={{
                            fontFamily:
                              FONT_MONO,
                            fontSize: 10,
                            fill: C.sub,
                          }}
                          axisLine={false}
                          tickLine={false}
                          width={36}
                        />

                        <ReferenceLine
                          y={100}
                          stroke={C.sub}
                          strokeDasharray="4 4"
                        />

                        <Tooltip
                          content={
                            <TrendTooltip
                              yKey="route_wise_airfare_index"
                            />
                          }
                        />

                        <Line
                          type="monotone"
                          dataKey="route_wise_airfare_index"
                          stroke={C.blue}
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Card>

                  <RecordsTable
                    columns={[
                      "date",
                      "route",
                      "route_wise_airfare_index",
                    ]}
                    headers={[
                      "Date",
                      "Route",
                      "Route Index",
                    ]}
                    rows={records}
                  />
                </>
              )}
          </>
        )}
    </div>
  );
}

/* ============================== SHARED TABLE ============================== */

function RecordsTable({
  columns,
  headers,
  rows,
  changeCol,
}) {
  return (
    <Card
      style={{
        padding: 0,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          overflowX: "auto",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse:
              "collapse",
            fontFamily: FONT_BODY,
            fontSize: 13,
            minWidth: 420,
          }}
        >
          <thead>
            <tr>
              {headers.map((h) => (
                <th
                  key={h}
                  style={{
                    textAlign: "left",
                    padding:
                      "10px 20px",
                    color: C.sub,
                    fontWeight: 600,
                    fontSize: 11,
                    letterSpacing: 0.4,
                    textTransform:
                      "uppercase",
                    borderBottom: `1px solid ${C.line}`,
                    whiteSpace:
                      "nowrap",
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                style={{
                  borderBottom: `1px solid ${C.line}`,
                }}
              >
                {columns.map((c) => (
                  <td
                    key={c}
                    style={{
                      padding:
                        "10px 20px",
                      fontFamily:
                        c ===
                          "quality_status" ||
                        c === "route"
                          ? FONT_BODY
                          : FONT_MONO,
                    }}
                  >
                    {c === changeCol ? (
                      <ChangeTag
                        value={row[c]}
                      />
                    ) : c ===
                      "quality_status" ? (
                      <Pill
                        tone={qualityTone(
                          row[c]
                        )}
                      >
                        {row[c]}
                      </Pill>
                    ) : (
                      row[c] ?? "—"
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

/* ============================== NAV / LAYOUT ============================== */

const NAV = [
  {
    key: "overview",
    label: "Overview",
    icon: LayoutDashboard,
  },
  {
    key: "daily",
    label: "Daily History",
    icon: CalendarDays,
  },
  {
    key: "weekly",
    label: "Weekly Index",
    icon: BarChart3,
  },
  {
    key: "monthly",
    label: "Monthly Index",
    icon: BarChart3,
  },
  {
    key: "routes",
    label: "Route-wise Index",
    icon: RouteIcon,
  },
];

/* ============================== APP ============================== */

export default function App() {
  const [page, setPage] =
    useState("overview");

  const {
    status,
    check,
  } = useBackendStatus();

  const statusMeta = {
    checking: {
      color: C.amber,
      label: "CHECKING...",
    },
    online: {
      color: C.green,
      label: "BACKEND ONLINE",
    },
    offline: {
      color: C.red,
      label: "BACKEND OFFLINE",
    },
  }[status];

  return (
    <div
      style={{
        fontFamily: FONT_BODY,
        background: C.paper,
        minHeight: "100vh",
        color: C.ink,
        display: "flex",
        width: "100%",
      }}
    >
      <aside
        style={{
          width: 210,
          background: C.navy,
          flexShrink: 0,
          padding: "20px 14px",
          display: "flex",
          flexDirection: "column",
          gap: 24,
        }}
        className="ai-sidebar"
      >
        <div>
          <div
            style={{
              fontFamily: FONT_HEAD,
              fontWeight: 700,
              fontSize: 16,
              color: "#fff",
            }}
          >
            AIRINDEX
          </div>

          <div
            style={{
              fontSize: 9.5,
              color: "#8CA3CC",
              letterSpacing: 0.4,
            }}
          >
            BACKEND-INTEGRATED BUILD
          </div>
        </div>

        <nav
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 2,
          }}
        >
          {NAV.map((n) => {
            const Icon = n.icon;
            const activeItem =
              page === n.key;

            return (
              <button
                key={n.key}
                onClick={() =>
                  setPage(n.key)
                }
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "9px 10px",
                  borderRadius: 5,
                  background: activeItem
                    ? "rgba(255,255,255,0.08)"
                    : "transparent",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  color: activeItem
                    ? "#fff"
                    : "#AFC1E0",
                  fontSize: 13,
                  fontWeight: activeItem
                    ? 600
                    : 500,
                  borderLeft:
                    activeItem
                      ? "2px solid #7FA6F5"
                      : "2px solid transparent",
                }}
              >
                <Icon size={15} />
                {n.label}
              </button>
            );
          })}
        </nav>

        <div
          style={{
            marginTop: "auto",
            fontSize: 10.5,
            color: "#5E75A3",
            lineHeight: 1.5,
          }}
        >
          SIH26056 — Real API integration.
          <br />
          No mock data on this build.
        </div>
      </aside>

      <div
        style={{
          flex: 1,
          minWidth: 0,
        }}
      >
        <header
          style={{
            height: 56,
            borderBottom: `1px solid ${C.line}`,
            background: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent:
              "space-between",
            padding: "0 20px",
            flexWrap: "wrap",
            gap: 8,
          }}
        >
          <span
            style={{
              fontFamily: FONT_HEAD,
              fontWeight: 600,
              fontSize: 15,
            }}
          >
            {
              NAV.find(
                (n) => n.key === page
              )?.label
            }
          </span>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
            }}
          >
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                fontSize: 11,
                fontFamily: FONT_MONO,
                fontWeight: 600,
                color: statusMeta.color,
              }}
            >
              <CircleDot size={11} />
              {statusMeta.label}
            </span>

            <button
              onClick={check}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                background: C.paper,
                border: `1px solid ${C.line}`,
                borderRadius: 4,
                padding: "6px 12px",
                cursor: "pointer",
                fontSize: 12,
                fontFamily: FONT_MONO,
                fontWeight: 600,
              }}
            >
              <RefreshCw size={13} />
              Recheck
            </button>
          </div>
        </header>

        {status === "offline" && (
          <div
            style={{
              background: C.redBg,
              borderBottom:
                "1px solid #F3C6CF",
              padding: "8px 20px",
              fontSize: 12,
              color: C.red,
              fontFamily: FONT_MONO,
            }}
          >
            Backend not reachable at{" "}
            {API_BASE} — start it with:
            python -m uvicorn main:app
            --reload
          </div>
        )}

        <div
          style={{
            padding: 24,
            maxWidth: 1000,
            margin: "0 auto",
          }}
        >
          {page === "overview" && (
            <Overview />
          )}

          {page === "daily" && (
            <DailyHistory />
          )}

          {page === "weekly" && (
            <WeeklyIndex />
          )}

          {page === "monthly" && (
            <MonthlyIndex />
          )}

          {page === "routes" && (
            <RoutesExplorer />
          )}
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

        * {
          box-sizing: border-box;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        @media (max-width: 767px) {
          .ai-sidebar {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}
