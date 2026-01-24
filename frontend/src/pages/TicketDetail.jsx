/**
 * TicketDetail Page
 * Detailed view of a single ticket
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Mail,
  User,
  Clock,
  Building2,
  Tag,
  MessageSquare,
} from "lucide-react";
import { getTicket, updateTicketStatus, addTicketNote } from "../services/api";
import UrgencyBadge from "../components/UrgencyBadge";
import ResponsePreview from "../components/ResponsePreview";

export default function TicketDetail() {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState("");
  const [timeRemaining, setTimeRemaining] = useState(0);

  useEffect(() => {
    loadTicket();
  }, [ticketId]);

  // Real-time SLA countdown
  useEffect(() => {
    if (!ticket) return;

    const updateTimer = () => {
      const remaining = new Date(ticket.sla_deadline) - new Date();
      setTimeRemaining(remaining);
    };

    updateTimer(); // Initial update
    const interval = setInterval(updateTimer, 1000); // Update every second

    return () => clearInterval(interval);
  }, [ticket]);

  const loadTicket = async () => {
    try {
      setLoading(true);
      const data = await getTicket(ticketId);
      setTicket(data);
    } catch (error) {
      console.error("Failed to load ticket:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      await updateTicketStatus(ticketId, newStatus);
      await loadTicket();
    } catch (error) {
      console.error("Failed to update status:", error);
    }
  };

  const handleAddNote = async () => {
    if (!note.trim()) return;

    try {
      await addTicketNote(ticketId, note);
      setNote("");
      await loadTicket();
    } catch (error) {
      console.error("Failed to add note:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ticket...</p>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Ticket not found</p>
        </div>
      </div>
    );
  }

  const hoursRemaining = Math.floor(timeRemaining / (1000 * 60 * 60));
  const minutesRemaining = Math.floor(
    (timeRemaining % (1000 * 60 * 60)) / (1000 * 60),
  );
  const isBreached = timeRemaining < 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate("/")}
                className="text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft size={20} />
              </button>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  {ticket.ticket_id}
                </h1>
                <p className="text-xs text-gray-500">{ticket.subject}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <UrgencyBadge severity={ticket.severity} />
              <select
                value={ticket.status}
                onChange={(e) => handleStatusUpdate(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm font-medium"
              >
                <option value="New">New</option>
                <option value="In Progress">In Progress</option>
                <option value="Waiting on Customer">Waiting on Customer</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="col-span-2 space-y-6">
            {/* AI Classification */}
            <div className="card bg-gradient-to-r from-purple-50 to-blue-50">
              <h2 className="font-semibold text-gray-900 mb-4">
                🤖 AI Reasoning Overlay
              </h2>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Category
                  </span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="badge bg-purple-100 text-purple-800">
                      {ticket.category}
                    </span>
                    <span className="text-xs text-gray-500">
                      {Math.round(ticket.classification_confidence * 100)}%
                      confidence
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Severity
                  </span>
                  <div className="flex items-center gap-2 mt-1">
                    <UrgencyBadge severity={ticket.severity} size="sm" />
                    {hoursRemaining > 0 && (
                      <span className="text-xs text-gray-500">
                        {hoursRemaining}h remaining
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {ticket.classification_reasoning && (
                <div className="mt-3 p-3 bg-white rounded-lg">
                  <span className="text-xs font-medium text-gray-600">
                    Reasoning:
                  </span>
                  <p className="text-sm text-gray-700 mt-1">
                    {ticket.classification_reasoning}
                  </p>
                </div>
              )}

              {ticket.urgency_signals && ticket.urgency_signals.length > 0 && (
                <div className="mt-3">
                  <span className="text-xs font-medium text-gray-600">
                    Urgency Signals:
                  </span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {ticket.urgency_signals.map((signal, idx) => (
                      <span key={idx} className="badge bg-red-100 text-red-800">
                        {signal}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Escalation Alert */}
              {ticket.is_escalated && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className="text-red-600 font-bold text-sm">
                      ⚠️ AUTO-ESCALATED
                    </span>
                  </div>
                  {ticket.escalation_reason && (
                    <p className="text-xs text-red-700 mt-1">
                      {ticket.escalation_reason}
                    </p>
                  )}
                  {ticket.followup_count > 0 && (
                    <p className="text-xs text-red-600 mt-1">
                      Follow-up #{ticket.followup_count}
                    </p>
                  )}
                </div>
              )}

              {/* Follow-up indicator (non-escalated) */}
              {!ticket.is_escalated && ticket.followup_count > 0 && (
                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className="text-yellow-700 font-medium text-sm">
                      🔔 Follow-up #{ticket.followup_count}
                    </span>
                  </div>
                  <p className="text-xs text-yellow-600 mt-1">
                    Customer has reached out {ticket.followup_count} time(s).
                    Next follow-up will trigger auto-escalation.
                  </p>
                </div>
              )}
            </div>

            {/* Response Preview */}
            <ResponsePreview ticket={ticket} />

            {/* Similar Tickets */}
            {ticket.similar_tickets && ticket.similar_tickets.length > 0 && (
              <div className="card">
                <h2 className="font-semibold text-gray-900 mb-4">
                  📊 Similar Resolved Tickets
                </h2>
                <div className="space-y-3">
                  {ticket.similar_tickets.map((similar, idx) => (
                    <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-900">
                          {similar.subject}
                        </span>
                        <span className="text-xs text-gray-500">
                          {Math.round(similar.similarity * 100)}% match
                        </span>
                      </div>
                      {similar.resolution && (
                        <p className="text-xs text-gray-600 line-clamp-2">
                          {similar.resolution}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Internal Notes */}
            <div className="card">
              <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <MessageSquare size={18} />
                Internal Notes
              </h2>

              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add internal note..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none"
                rows={3}
              />

              <button
                onClick={handleAddNote}
                className="btn-primary mt-2"
                disabled={!note.trim()}
              >
                Add Note
              </button>

              {ticket.internal_notes && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                    {ticket.internal_notes}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Customer Info */}
            <div className="card">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Building2 size={18} />
                Customer Info
              </h3>

              <div className="space-y-3">
                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Company
                  </span>
                  <p className="text-sm text-gray-900">
                    {ticket.customer_company || "N/A"}
                  </p>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Tier
                  </span>
                  <p className="text-sm">
                    <span
                      className={`badge ${
                        ticket.customer_tier === "Gold"
                          ? "bg-yellow-100 text-yellow-800"
                          : ticket.customer_tier === "Silver"
                            ? "bg-gray-100 text-gray-800"
                            : "bg-orange-100 text-orange-800"
                      }`}
                    >
                      {ticket.customer_tier || "N/A"}
                    </span>
                  </p>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Contact
                  </span>
                  <p className="text-sm text-gray-900">{ticket.sender}</p>
                </div>
              </div>
            </div>

            {/* Ticket Metadata */}
            <div className="card">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Tag size={18} />
                Metadata
              </h3>

              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Created
                  </span>
                  <p className="text-gray-900">
                    {new Date(ticket.created_at).toLocaleString()}
                  </p>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    SLA Deadline
                  </span>
                  <p
                    className={`font-medium ${
                      isBreached
                        ? "text-red-600"
                        : hoursRemaining < 1
                          ? "text-orange-600"
                          : "text-gray-900"
                    }`}
                  >
                    {new Date(ticket.sla_deadline).toLocaleString()}
                  </p>
                  <p
                    className={`text-xs mt-1 font-semibold ${
                      isBreached
                        ? "text-red-600"
                        : hoursRemaining < 1
                          ? "text-orange-600"
                          : "text-green-600"
                    }`}
                  >
                    {isBreached
                      ? "⚠️ SLA BREACHED"
                      : hoursRemaining > 0
                        ? `✓ ${hoursRemaining}h ${minutesRemaining}m remaining`
                        : `✓ ${minutesRemaining}m remaining`}
                  </p>
                </div>

                {ticket.thread_count > 0 && (
                  <div>
                    <span className="text-xs font-medium text-gray-600">
                      Thread
                    </span>
                    <p className="text-gray-900">
                      {ticket.thread_count} related emails
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
