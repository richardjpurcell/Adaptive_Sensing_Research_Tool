"use client";

import { useEffect, useRef, useState } from "react";
import { API, postJSON, getJSON } from "@/lib/api";

type InitRunResp = { run_id: string; t: number; dt_seconds: number; horizon_steps: number };
type EnvRow = { env_id: string; H: number; W: number; cell_size: number; crs_code: string };
type FireRow = { fire_id: string; env_id: string; model: string; n_ignitions: number };

function toSeconds(amount: number, unit: "sec"|"min"|"hour"|"day") {
  return unit === "sec" ? amount :
         unit === "min" ? amount * 60 :
         unit === "hour" ? amount * 3600 :
         amount * 86400;
}

export default function RunPage() {
  // dropdown data
  const [envs, setEnvs] = useState<EnvRow[]>([]);
  const [fires, setFires] = useState<FireRow[]>([]);

  // selected ids
  const [envId, setEnvId] = useState("");
  const [fireId, setFireId] = useState("");

  // timing/model controls
  const [amount, setAmount] = useState(1);
  const [unit, setUnit] = useState<"sec"|"min"|"hour"|"day">("hour");
  const [horizon, setHorizon] = useState(24);
  const [spread, setSpread] = useState(0.3);

  // run state
  const [runId, setRunId] = useState<string | null>(null);
  const [t, setT] = useState(0);           // what we are viewing
  const [tLatest, setTLatest] = useState(0); // newest available in Zarr
  const [dtSec, setDtSec] = useState(3600);
  const [Tmax, setTmax] = useState(24);

  // playback
  const [playing, setPlaying] = useState(false);
  const playTimerRef = useRef<number | null>(null);
  const pollTimerRef = useRef<number | null>(null);

  // fetch dropdown data on mount
  useEffect(() => {
    getJSON<EnvRow[]>("/manifests/environments").then(setEnvs).catch(console.error);
    getJSON<FireRow[]>("/manifests/fires").then(setFires).catch(console.error);
  }, []);

  // filter fires to those matching selected env (nice-to-have)
  const filteredFires = fireId && envId
    ? fires.filter(f => f.env_id === envId)
    : fires;

  async function initRun() {
    const dt_seconds = toSeconds(amount, unit);
    const r = await postJSON<InitRunResp>("/runs/init", {
      env_id: envId,
      fire_id: fireId,
      run_name: "demo",
      dt_seconds,
      horizon_steps: horizon,
      spread_prob: spread,
    });
    setRunId(r.run_id);
    setT(0);
    setTLatest(0);
    setDtSec(r.dt_seconds);
    setTmax(r.horizon_steps);
    setPlaying(false);
    // start polling latest so slider stays fresh even if we only scrub
    startLatestPolling(r.run_id);
  }

  async function stepOnce() {
    if (!runId) return;
    const r = await postJSON<{ run_id: string; t: number; done: boolean }>(`/runs/${runId}/step`, {});
    setTLatest(r.t);
    setT(r.t);              // snap viewer to the newest frame
    if (r.done) setPlaying(false);
  }

  function onPlay() { if (runId) setPlaying(true); }
  function onPause() { setPlaying(false); }

  // drive simulation when playing
  useEffect(() => {
    if (!playing || !runId) {
      if (playTimerRef.current) { window.clearInterval(playTimerRef.current); playTimerRef.current = null; }
      return;
    }
    playTimerRef.current = window.setInterval(() => {
      stepOnce().catch(err => { console.error(err); setPlaying(false); });
    }, 250) as unknown as number; // ~4 FPS
    return () => {
      if (playTimerRef.current) window.clearInterval(playTimerRef.current);
      playTimerRef.current = null;
    };
  }, [playing, runId]);

  // poll /latest so the slider max stays up-to-date even when paused
  function startLatestPolling(id: string) {
    if (pollTimerRef.current) window.clearInterval(pollTimerRef.current);
    pollTimerRef.current = window.setInterval(() => {
      getJSON<{ run_id: string; t_latest: number }>(`/runs/${id}/latest`)
        .then(({ t_latest }) => setTLatest(t_latest))
        .catch(() => {});
    }, 800) as unknown as number;
  }
  useEffect(() => {
    return () => { if (pollTimerRef.current) window.clearInterval(pollTimerRef.current); };
  }, []);

  // image URLs — add cache-buster param tied to t
  const statePng = runId ? `${API}/runs/${runId}/t/${t}/state.png?r=${t}` : "";
  const beliefPng = runId ? `${API}/runs/${runId}/t/${t}/belief.png?vmin=0&vmax=1&cmap=viridis&r=${t}` : "";
  const legendPng = runId ? `${API}/runs/${runId}/legend/belief.png` : "";

  return (
    <section className="space-y-3">
      <h1 className="text-xl font-semibold">Run (simulate forward)</h1>

      {/* IDs via dropdowns */}
      <div className="grid md:grid-cols-2 gap-2">
        <label>
          Environment
          <select value={envId} onChange={e=>setEnvId(e.target.value)}>
            <option value="">-- select environment --</option>
            {envs.map(e => (
              <option key={e.env_id} value={e.env_id}>
                {e.env_id} ({e.H}×{e.W}, {e.cell_size}m)
              </option>
            ))}
          </select>
        </label>

        <label>
          Fire
          <select value={fireId} onChange={e=>setFireId(e.target.value)} disabled={!envId && filteredFires.length>0}>
            <option value="">-- select fire --</option>
            {(envId ? fires.filter(f => f.env_id === envId) : fires).map(f => (
              <option key={f.fire_id} value={f.fire_id}>
                {f.fire_id} (ign: {f.n_ignitions})
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* timing & model */}
      <div className="grid md:grid-cols-3 gap-2">
        <label>time step
          <div className="flex gap-2">
            <input type="number" min={1} value={amount} onChange={e=>setAmount(+e.target.value)} style={{width:90}} />
            <select value={unit} onChange={e=>setUnit(e.target.value as any)}>
              <option value="sec">sec</option>
              <option value="min">min</option>
              <option value="hour">hour</option>
              <option value="day">day</option>
            </select>
          </div>
        </label>

        <label>horizon (steps)
          <input type="number" min={1} value={horizon} onChange={e=>setHorizon(+e.target.value)} />
        </label>

        <label>spread q
          <input type="range" min={0} max={1} step={0.01} value={spread} onChange={e=>setSpread(+e.target.value)} />
          <span className="text-sm ml-2">{spread.toFixed(2)}</span>
        </label>
      </div>

      {/* controls */}
      <div className="space-x-2">
        <button onClick={initRun} disabled={!envId || !fireId}>Initialize Run</button>
        <button onClick={stepOnce} disabled={!runId}>Step</button>
        {!playing ? (
          <button onClick={onPlay} disabled={!runId}>Play</button>
        ) : (
          <button onClick={onPause}>Pause</button>
        )}
      </div>

      {/* status + slider */}
      {runId && (
        <>
          <p className="text-sm">
            run_id: <code>{runId}</code> &nbsp;
            viewing t=<code>{t}</code> / latest <code>{tLatest}</code> (horizon {Tmax-1}) &nbsp;
            Δt=<code>{dtSec}</code>s
          </p>
          <div className="flex items-center gap-3">
            <label className="text-sm">Scrub:</label>
            <input
              type="range"
              min={0}
              max={Math.max(0, tLatest)}
              value={t}
              onChange={(e)=>setT(parseInt(e.target.value, 10))}
              style={{width: 320}}
            />
          </div>
        </>
      )}

      {/* images */}
      {runId && (
        <div className="grid md:grid-cols-3 gap-3 items-start">
          <div>
            <h3 className="font-medium mb-1">Hidden state (t={t})</h3>
            <img src={statePng} alt="Hidden state" />
          </div>
          <div>
            <h3 className="font-medium mb-1">Belief (t={t})</h3>
            <img src={beliefPng} alt="Belief" />
          </div>
          <div>
            <h3 className="font-medium mb-1">Legend</h3>
            <img src={legendPng} alt="Legend" />
          </div>
        </div>
      )}
    </section>
  );
}
