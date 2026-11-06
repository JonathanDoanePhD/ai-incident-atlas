import { NavLink, Route, Routes } from 'react-router-dom';
import { AppProvider, useApp } from './state';
import ExplorePage from './pages/Explore';
import CatalogPage from './pages/Catalog';
import IncidentPage from './pages/Incident';
import InsightsPage from './pages/Insights';
import AboutPage from './pages/About';

function Shell() {
  const { data, error } = useApp();
  return (
    <div className="shell">
      <a className="skip" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <NavLink to="/" className="brand" aria-label="AI Incident Atlas home">
          <span className="brand-mark" aria-hidden="true" />
          AI Incident Atlas
        </NavLink>
        <nav aria-label="Main">
          <NavLink to="/" end>
            Constellation
          </NavLink>
          <NavLink to="/catalog">Catalog</NavLink>
          <NavLink to="/insights">Insights</NavLink>
          <NavLink to="/about">About</NavLink>
        </nav>
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
            <Route path="/" element={<ExplorePage />} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/incident/:id" element={<IncidentPage />} />
            <Route path="/insights" element={<InsightsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="*" element={<div className="page">Page not found.</div>} />
          </Routes>
        )}
      </main>
      <footer className="footer">
        Incident data: <a href="https://incidentdatabase.ai">AI Incident Database</a> (Responsible AI Collaborative), CC BY-SA 4.0.
        Derived data CC BY-SA 4.0; code MIT. Report excerpts © their publishers. <NavLink to="/about">Methodology &amp; licensing</NavLink>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <Shell />
    </AppProvider>
  );
}
