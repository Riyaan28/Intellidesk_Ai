import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import TicketDetail from "./pages/TicketDetail";
import AddTicket from "./pages/AddTicket";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/add-ticket" element={<AddTicket />} />
        <Route path="/ticket/:ticketId" element={<TicketDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
