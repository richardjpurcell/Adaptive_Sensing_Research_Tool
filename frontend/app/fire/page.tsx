// frontend/app/fire/page.tsx
"use client";

import { useEffect, useState } from "react";
import { postJSON, getJSON } from "@/lib/api";

type EnvRow = { env_id: string; H: number; W: number; cell_size: number; crs_code: string };
type NewFireResp = { fire_id: string };

export default function FirePage() {
  // dropdown data
  const [envs, setEnvs] = useState<EnvRow[]>([]);
  const [envId, setEnvId] = useState("");

  // selected env dims
  const [H, setH] = useState<number | null>(null);
  const [W, setW] = useState<number | null>(null);

  // ignition + fire config
  const [row, setRow] = useState(0);
  const [col, setCol] = useState(0);
  const [seed, setSeed] = useState(0);
  const [model, setModel] = useState("E2_base");

  const [fireId, setFireId] = useState<string | null>(null);
  const canSave = !!envId;

  // Load environments for dropdown
  useEffect(() => {
    getJSON<EnvRow[]>("/manifests/environments")
      .then((rows) => {
        setEnvs(rows);
        // pick first by default
        if (rows.length && !envId) {
          setEnvId(rows[0].env_id);
          setH(rows[0].H); setW(rows[0].W);
          setRow(Math.floor(rows[0].H / 2));
          setCol(Math.floor(rows[0].W / 2));
        }
      })
      .catch(console.error);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // When env changes, update H/W and clamp/center ignition
  useEffect(() => {
    const sel = envs.find((e) => e.env_id === envId);
    if (!sel) return;
    setH(sel.H); setW(sel.W);
    // center by default
    setRow((r) => clampOrDefault(r, sel.H));
    setCol((c) => clampOrDefault(c, sel.W));
  }, [envId, envs]);

  function clampOrDefault(v: number, max: number) {
    if (Number.isFinite(v) && v >= 0 && v < max) return v;
    return Math.floor(max / 2);
  }

  async function createFire() {
    if (!envId) return;
    // clamp once more for safety
    const r = clampOrDefault(row, H ?? row);
    const c = clampOrDefault(col, W ?? col);
    const body = {
      env_id: envId,
      ignitions: { type: "point", locations: [{ row: r, col: c }], t0: 0 },
      model,
      seed,
    };
    const resp = await postJSON<NewFireResp>("/manifests/fire", body);
    setFireId(resp.fire_id);
  }

  return (
    <section className="space-y-3">
      <h1 className="text-xl font-semibold">Fire Designer</h1>

      {/* Environment selection */}
      <div className="grid md:grid-cols-2 gap-2">
        <label>
          Environment
          <select value={envId} onChange={(e) => setEnvId(e.target.value)}>
            <option value="">-- select environment --</option>
            {envs.map((e) => (
              <option key={e.env_id} value={e.env_id}>
                {e.env_id} ({e.H}×{e.W}, {e.cell_size}m)
              </option>
            ))}
          </select>
        </label>

        <label>
          Model
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            <option value="E2_base">E2_base</option>
            {/* add richer models later */}
          </select>
        </label>
      </div>

      {/* Ignition + seed */}
      <div className="grid md:grid-cols-3 gap-2">
        <label>
          Ignition row
          <input
            type="number"
            value={row}
            min={0}
            max={(H ?? 1) - 1}
            onChange={(e) => setRow(clampOrDefault(+e.target.value, H ?? +e.target.value))}
          />
          {H !== null && <span className="text-xs ml-2">[0..{H - 1}]</span>}
        </label>

        <label>
          Ignition col
          <input
            type="number"
            value={col}
            min={0}
            max={(W ?? 1) - 1}
            onChange={(e) => setCol(clampOrDefault(+e.target.value, W ?? +e.target.value))}
          />
          {W !== null && <span className="text-xs ml-2">[0..{W - 1}]</span>}
        </label>

        <label>
          Seed
          <input type="number" value={seed} onChange={(e) => setSeed(+e.target.value)} />
        </label>
      </div>

      <div className="space-x-2">
        <button onClick={createFire} disabled={!canSave}>Save Fire</button>
      </div>

      {fireId && (
        <p className="text-sm">
          fire_id: <code>{fireId}</code>
          {H !== null && W !== null && (
            <> &nbsp; — grid {H}×{W}, ignition ({row},{col})</>
          )}
        </p>
      )}
    </section>
  );
}
