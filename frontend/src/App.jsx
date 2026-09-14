import { BrowserRouter, Link, NavLink, Route, Routes } from "react-router-dom";
import "./index.css";
import CaseDetail from "./pages/CaseDetail";
import CasesPage from "./pages/CasesPage";
import Dashboard from "./pages/Dashboard";
import TenderDetail from "./pages/TenderDetail";
import VendorDetail from "./pages/VendorDetail";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="topbar">
          <Link to="/" className="brand">
            <span className="brand-mark">PL</span>
            <span className="brand-name">ProcureLens</span>
          </Link>
          <div className="topbar-sub">Procurement Investigation Support</div>
          <nav className="topnav">
            <NavLink to="/" end className={({ isActive }) => `topnav-link${isActive ? " active" : ""}`}>
              Dashboard
            </NavLink>
            <NavLink to="/cases" className={({ isActive }) => `topnav-link${isActive ? " active" : ""}`}>
              Cases
            </NavLink>
          </nav>
        </header>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/cases/:caseId" element={<CaseDetail />} />
            <Route path="/vendors/:vendorId" element={<VendorDetail />} />
            <Route path="/tenders/:tenderId" element={<TenderDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
