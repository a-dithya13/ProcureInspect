import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import "./index.css";
import CaseDetail from "./pages/CaseDetail";
import Dashboard from "./pages/Dashboard";
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
        </header>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cases/:caseId" element={<CaseDetail />} />
            <Route path="/vendors/:vendorId" element={<VendorDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
