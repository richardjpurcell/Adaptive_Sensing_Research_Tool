// frontend/app/replay/page.tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { API, getJSON } from "@/lib/api";

type RunMeta = { run_id: string; H: number; W: number; T: number };

export default function ReplayPage() {
  const [runs, setRuns] = useState<string[]>([]);
  const [runId, setRunId] = useState<string>("");
  const [meta, setMeta] = useState<RunMeta | null>(null);
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    getJSON<string[]>("/runs/list").then(setRuns).catch(console.error);
  }, []);

  async function loadMeta(id: string) {
    setRunId(id);
    setMeta(null);
    setPlaying(false);
    if (!id) return;
    const m = await getJSON<RunMeta>(`/runs/${id}/meta`);
    setMeta(m);
    setT(Math.max(0, m.T - 1)); // start at latest
  }

  // simple playback (scrub only; no simulation)
  useEffect(() => {
    if (!playing || !meta) {
      if (timerRef.current) { window.clearInterval(timerRef.current); timerRef.current = null; }
      return;
    }
    timerRef.current = window.setInterval(() => {
      setT(prev => {
        const next = prev + 1;
        if (next >= meta.T) {
          setPlaying(false);
          return prev;
        }
        return next;
      });
    }, 250) as unknown as number;
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      timerRef.current = null;
    };
  }, [playing, meta]);

  const stateUrl = runId ? `${API}/runs/${runId}/t/${t}/state.png?r=${t}` : "";
  const beliefUrl = runId ? `${API}/runs/${runId}/t/${t}/belief.png?vmin=0&vmax=1&cmap=viridis&r=${t}` : "";
  const legendUrl = runId ? `${API}/runs/${runId}/legend/belief.png` : "";

  return (
    <section className="space-y-3">
      <h1 className="text-xl font-semibold">Replay / Physical Twin</h1>
      <div className="flex items-center gap-2">
        <label className="text-sm">Run:</label>
        <select value={runId} onChange={(e)=>loadMeta(e.target.value)}>
          <option value="">-- select a run --</option>
          {runs.map(r => <option key={r} value={r}>{r}</option>)}
        </select>
        <button onClick={()=>setPlaying(p=>!p)} disabled={!meta}>
          {playing ? "Pause" : "Play"}
        </button>
      </div>

      {meta && (
        <>
          <div className="flex items-center gap-3">
            <label className="text-sm">t = {t} / {meta.T-1}</label>
            <input type="range" min={0} max={Math.max(0, meta.T-1)} value={t}
                   onChange={(e)=>setT(parseInt(e.target.value,10))} style={{width: 320}} />
          </div>

          <div className="grid md:grid-cols-3 gap-3 items-start">
            <div>
              <h3 className="font-medium mb-1">Hidden state</h3>
              <img src={stateUrl} alt="Hidden state" />
            </div>
            <div>
              <h3 className="font-medium mb-1">Belief</h3>
              <img src={beliefUrl} alt="Belief" />
            </div>
            <div>
              <h3 className="font-medium mb-1">Legend</h3>
              <img src={legendUrl} alt="Legend" />
            </div>
          </div>
        </>
      )}
    </section>
  );
}
