import { Route, Routes, useLocation } from "react-router-dom";
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";
import Home from "./pages/Home";
import B2BPage from "./pages/B2BPage";
import IntelligencePage from "./pages/IntelligencePage";

const titles: Record<string, string> = {
  "/": "Overview",
  "/b2b": "B2B Lead Generation Agent",
  "/intelligence": "Competitive Intelligence Agent",
};

export default function App() {
  const loc = useLocation();
  const title = titles[loc.pathname] ?? "ARIGRA";
  return (
    <div className="min-h-screen" style={{ background: "var(--color-bg)" }}>
      <Sidebar />
      <Header title={title} />
      <main
        style={{
          marginLeft: 220,
          marginTop: 56,
          padding: 24,
        }}
      >
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/b2b" element={<B2BPage />} />
            <Route path="/intelligence" element={<IntelligencePage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
