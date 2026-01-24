import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import Dashboard from "./pages/Dashboard";
import DashboardNew from "./pages/DashboardNew";
import TicketDetail from "./pages/TicketDetail";
import TicketDetailNew from "./pages/TicketDetailNew";
import AddTicket from "./pages/AddTicket";
import ResolveTicket from "./pages/ResolveTicket";

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardNew />} />
          <Route path="/add-ticket" element={<AddTicket />} />
          <Route path="/ticket/:ticketId" element={<TicketDetailNew />} />
          <Route path="/resolve/:ticketId" element={<ResolveTicket />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
