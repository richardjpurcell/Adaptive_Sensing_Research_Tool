import "../styles/styles.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">
        <nav className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-5 py-3 flex flex-wrap gap-2 text-sm">
            <a href="/environment" className="px-4 py-2 rounded-xl border bg-white">Environment</a>
            <a href="/fire" className="px-4 py-2 rounded-xl border bg-white">Fire</a>
            <a href="/sensors" className="px-4 py-2 rounded-xl border bg-white">Sensors</a>
            <a href="/run" className="px-4 py-2 rounded-xl border bg-white">Run</a>
            <a href="/replay" className="px-4 py-2 rounded-xl border bg-white">Replay / PT</a>
            <a href="/analysis" className="px-4 py-2 rounded-xl border bg-white">Analysis</a>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-5 py-6">{children}</main>
      </body>
    </html>
  );
}
