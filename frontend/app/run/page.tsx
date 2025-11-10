"use client";
import { useEffect, useState } from "react";

type Manifest = { file: string; name?: string; id?: string };
export default function RunPage() {
  const [apiStatus, setApiStatus] = useState("checking…");
  const [manifests, setManifests] = useState<Manifest[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health/").then(r=>r.json())
      .then(j => setApiStatus(`${j.status} (${j.version})`))
      .catch(() => setApiStatus("unreachable"));

    fetch("http://127.0.0.1:8000/manifests/list").then(r=>r.json())
      .then(j => setManifests(j.manifests || []))
      .catch(() => setManifests([]));
  }, []);

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold">Run</h1>

      <div className="border rounded-xl bg-white px-4 py-3 text-sm">
        <b>API:</b> {apiStatus}
      </div>

      <div className="border rounded-xl bg-white px-4 py-3">
        <h2 className="font-semibold mb-2">Available Manifests</h2>
        <ul className="list-disc pl-5 text-sm">
          {manifests.map(m => (
            <li key={m.file}>
              <code>{m.file}</code>
              {m.name ? <> — <b>{m.name}</b></> : null}
              {m.id ? <> (<code>{m.id}</code>)</> : null}
            </li>
          ))}
          {manifests.length === 0 && <li>No manifests found (run seed_demo.py)</li>}
        </ul>
      </div>
    </section>
  );
}
