import { lazy, Suspense, useEffect, useState } from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';
import { AppProvider, useApp } from './state';
// The 3-D constellation pulls in three.js; load it on demand so other pages stay light.
const ExplorePage = lazy(() => import('./pages/Explore'));
import CatalogPage from './pages/Catalog';
import IncidentPage from './pages/Incident';
import InsightsPage from './pages/Insights';
import AboutPage from './pages/About';

// ?embed=1 (e.g. inside the research portfolio): the host page carries the attribution, so drop the footer.
const EMBED = new URLSearchParams(window.location.search).get('embed') === '1';

function Shell() {
  const { data, error } = useApp();
  return (
    <div className={`shell${EMBED ? ' embed' : ''}`}>
      <a className="skip" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <NavLink to="/" className="brand" aria-label="AI Incident Atlas home">
          <span className="logo" aria-hidden="true">✦</span>
          <span>
            <span className="brand-title">AI Incident Atlas</span>
            <span className="brand-sub">
              {data ? `${data.nodes.length.toLocaleString()} real-world AI incidents` : 'Real-world AI incidents'} · evidence-grounded atlas
            </span>
          </span>
        </NavLink>
        <nav aria-label="Main">
          <NavLink to="/" end>
            Constellation
          </NavLink>
          <NavLink to="/catalog">Catalog</NavLink>
          <NavLink to="/insights">Insights</NavLink>
          <NavLink to="/about">About</NavLink>
        </nav>
        <ThemeToggle />
      </header>
      <main id="main">
        {error ? (
          <div className="page">
            <p role="alert">Could not load the atlas data: {error}</p>
          </div>
        ) : !data ? (
          <div className="loading" role="status">
            Loading {''}incidents…
          </div>
        ) : (
          <Routes>
            <Route path="/" element={<Suspense fallback={<div className="loading" role="status">Loading the constellation…</div>}><ExplorePage /></Suspense>} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/incident/:id" element={<IncidentPage />} />
            <Route path="/insights" element={<InsightsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<div className="page">Page not found.</div>} />
          </Routes>
        )}
      </main>
      {!EMBED && <footer className="footer">
        Incident data: <a href="https://incidentdatabase.ai">AI Incident Database</a> (Responsible AI Collaborative), CC BY-SA 4.0.
        Derived data CC BY-SA 4.0; code MIT. Report excerpts © their publishers. <NavLink to="/about">Methodology &amp; licensing</NavLink>
      </footer>}
    </div>
  );
}

function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    try { return (localStorage.getItem('atlas-theme') as 'dark' | 'light') || 'dark'; } catch { return 'dark'; }
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('atlas-theme', theme); } catch { /* storage unavailable */ }
  }, [theme]);
  return (
    <button type="button" className="theme-toggle" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}>
      {theme === 'dark' ? '☀' : '☾'}
    </button>
  );
}

export default function App() {
  return (
    <AppProvider>
      <Shell />
    </AppProvider>
  );
}
