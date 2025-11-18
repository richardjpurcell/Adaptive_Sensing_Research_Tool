// frontend/app/environment/page.tsx
"use client";

import { useState } from "react";
import { API, postJSON } from "@/lib/api";

type NewEnvReq = {
  grid: { H: number; W: number; cell_size: number; crs_code: string };
  seed: number;
};
type NewEnvResp = { env_id: string };

export default function EnvironmentPage() {
  const [H, setH] = useState(64);
  const [W, setW] = useState(96);
  const [cellSize, setCellSize] = useState(250);
  const [crs, setCrs] = useState("EPSG:32612");
  const [seed, setSeed] = useState(0);
  const [envId, setEnvId] = useState<string | null>(null);
  const [beliefUrl, setBeliefUrl] = useState<string | null>(null);

  async function createEnv() {
    const body: NewEnvReq = { grid: { H, W, cell_size: cellSize, crs_code: crs }, seed };
    const r = await postJSON<NewEnvResp>("/manifests/environment", body);
    setEnvId(r.env_id);
    setBeliefUrl(null);
  }

  function previewBelief() {
    if (!envId) return;
    // We can POST to /preview/belief.png, but easiest for <img> is to use a small proxy route or a form submit.
    // Simpler: use fetch with a Blob URL:
    fetch(`${API}/preview/belief.png`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ env_id: envId, prior: "uniform", prior_strength: 1.0 }),
    })
      .then(r => r.blob())
      .then(b => setBeliefUrl(URL.createObjectURL(b)));
  }

  return (
    <section className="space-y-3">
      <h1 className="text-xl font-semibold">Environment Designer</h1>
      <div className="grid grid-cols-2 gap-2">
        <label>H <input type="number" value={H} onChange={e=>setH(+e.target.value)} /></label>
        <label>W <input type="number" value={W} onChange={e=>setW(+e.target.value)} /></label>
        <label>Cell size (m) <input type="number" value={cellSize} onChange={e=>setCellSize(+e.target.value)} /></label>
        <label>CRS <input value={crs} onChange={e=>setCrs(e.target.value)} /></label>
        <label>Seed <input type="number" value={seed} onChange={e=>setSeed(+e.target.value)} /></label>
      </div>

      <div className="space-x-2">
        <button onClick={createEnv}>Save Environment</button>
        <button onClick={previewBelief} disabled={!envId}>Preview Belief</button>
      </div>

      {envId && <p className="text-sm">env_id: <code>{envId}</code></p>}
      {beliefUrl && (
        <div className="mt-2">
          <img src={beliefUrl} alt="Initial belief preview" />
        </div>
      )}
    </section>
  );
}
