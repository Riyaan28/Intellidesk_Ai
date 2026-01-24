/**
 * TicketCard Component
 * Displays ticket information in card format
 */

import React from "react";
import { formatDistanceToNow } from "date-fns";
import { Clock, User, Mail, TrendingUp } from "lucide-react";
import UrgencyBadge from "./UrgencyBadge";

export default function TicketCard({ ticket, onClick }) {
  const timeRemaining = new Date(ticket.sla_deadline) - new Date();
  const hoursRemaining = Math.floor(timeRemaining / (1000 * 60 * 60));
  const isUrgent = hoursRemaining < 1;

  return (
    <div
      className="card hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onClick && onClick(ticket)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-gray-500">
              {ticket.ticket_id}
            </span>
            <UrgencyBadge severity={ticket.severity} size="sm" />
            {ticket.is_escalated && (
              <span className="text-xs font-bold text-red-600 bg-red-100 px-2 py-0.5 rounded">
                ⚠️ ESCALATED
              </span>
            )}
            {!ticket.is_escalated && ticket.followup_count > 0 && (
              <span className="text-xs font-medium text-yellow-700 bg-yellow-100 px-2 py-0.5 rounded">
                🔔 Follow-up #{ticket.followup_count}
              </span>
            )}
          </div>
          <h3 className="text-base font-semibold text-gray-900 line-clamp-2">
            {ticket.subject}
          </h3>
        </div>
      </div>

      {/* Body Preview */}
      <p className="text-sm text-gray-600 line-clamp-2 mb-3">{ticket.body}</p>

      {/* Metadata */}
      <div className="space-y-2">
        {/* Category & Confidence */}
        <div className="flex items-center gap-2 text-xs">
          <span className="badge bg-purple-100 text-purple-800">
            {ticket.category}
          </span>
          <div className="flex items-center gap-1 text-gray-500">
            <TrendingUp size={12} />
            <span>
              {Math.round(ticket.classification_confidence * 100)}% confidence
            </span>
          </div>
        </div>

        {/* Sender & Time */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Mail size={12} />
            <span>{ticket.sender}</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock size={12} />
            <span>
              {formatDistanceToNow(new Date(ticket.created_at), {
                addSuffix: true,
              })}
            </span>
          </div>
        </div>

        {/* SLA Countdown */}
        <div
          className={`flex items-center gap-1 text-xs font-medium ${
            isUrgent ? "text-red-600" : "text-gray-600"
          }`}
        >
          <Clock size={12} />
          <span>
            {hoursRemaining > 0
              ? `${hoursRemaining}h remaining`
              : "SLA BREACHED"}
          </span>
        </div>
      </div>

      {/* Status Badge */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <span
          className={`badge ${
            ticket.status === "New"
              ? "bg-blue-100 text-blue-800"
              : ticket.status === "In Progress"
                ? "bg-yellow-100 text-yellow-800"
                : ticket.status === "Resolved"
                  ? "bg-green-100 text-green-800"
                  : "bg-gray-100 text-gray-800"
          }`}
        >
          {ticket.status}
        </span>

        {ticket.auto_sent && (
          <span className="badge bg-indigo-100 text-indigo-800 ml-2">
            🤖 Auto-responded
          </span>
        )}
      </div>
    </div>
  );
}
