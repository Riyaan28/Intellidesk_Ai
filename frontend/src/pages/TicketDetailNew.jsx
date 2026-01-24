/**
 * Enhanced TicketDetail Page
 * Beautiful UI with animations, comprehensive ticket information, and AI insights
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Mail,
  User,
  Clock,
  Building2,
  Phone,
  MapPin,
  Tag,
  MessageSquare,
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  Zap,
  Eye,
  FileText,
  Target,
  Activity,
  Award,
  Link as LinkIcon,
} from "lucide-react";
import { getTicket, updateTicketStatus, addTicketNote } from "../services/api";
import UrgencyBadge from "../components/UrgencyBadge";
import ResponsePreview from "../components/ResponsePreview";

export default function TicketDetailNew() {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState("");
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [activeTab, setActiveTab] = useState("details");

  useEffect(() => {
    loadTicket();
  }, [ticketId]);

  // Real-time SLA countdown with animation
  useEffect(() => {
    if (!ticket) return;

    const updateTimer = () => {
      const remaining = new Date(ticket.sla_deadline) - new Date();
      setTimeRemaining(remaining);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 border-4 border-primary-200 rounded-full animate-ping"></div>
            <div className="absolute inset-0 border-4 border-t-primary-600 rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-600 font-medium">Loading ticket details...</p>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 font-medium">Ticket not found</p>
          <button onClick={() => navigate("/")} className="mt-4 btn-primary">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const hoursRemaining = Math.floor(timeRemaining / (1000 * 60 * 60));
  const minutesRemaining = Math.floor(
    (timeRemaining % (1000 * 60 * 60)) / (1000 * 60),
  );
  const isBreached = timeRemaining < 0;
  const isUrgent = hoursRemaining < 1 && !isBreached;

  // Calculate SLA progress percentage
  const totalSlaTime = ticket.sla_hours * 60 * 60 * 1000;
  const elapsed = new Date() - new Date(ticket.created_at);
  const slaProgress = Math.min(100, (elapsed / totalSlaTime) * 100);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Enhanced Header with Glassmorphism */}
      <div className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Left: Navigation & Title */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate("/")}
                className="p-2 hover:bg-gray-100 rounded-lg transition-all hover:scale-105 active:scale-95"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg transform hover:rotate-6 transition-transform">
                  <Mail className="text-white" size={24} />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    {ticket.ticket_id}
                    {ticket.is_escalated && (
                      <span className="text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded-full animate-pulse">
                        ESCALATED
                      </span>
                    )}
                  </h1>
                  <p className="text-sm text-gray-500 line-clamp-1">
                    {ticket.subject}
                  </p>
                </div>
              </div>
            </div>

            {/* Right: Status & Actions */}
            <div className="flex items-center gap-3">
              <UrgencyBadge severity={ticket.severity} />
              <select
                value={ticket.status}
                onChange={(e) => handleStatusUpdate(e.target.value)}
                className="px-4 py-2 rounded-lg border-2 border-gray-200 text-sm font-medium hover:border-primary-400 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="New">🆕 New</option>
                <option value="In Progress">⏳ In Progress</option>
                <option value="Waiting on Customer">
                  ⏸️ Waiting on Customer
                </option>
                <option value="Resolved">✅ Resolved</option>
                <option value="Closed">🔒 Closed</option>
              </select>
            </div>
          </div>

          {/* SLA Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-600">
                SLA Progress
              </span>
              <span
                className={`text-xs font-bold ${isBreached ? "text-red-600" : isUrgent ? "text-orange-600" : "text-green-600"}`}
              >
                {isBreached
                  ? "⚠️ BREACHED"
                  : `⏱️ ${hoursRemaining}h ${minutesRemaining}m remaining`}
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-1000 ease-out ${
                  isBreached
                    ? "bg-gradient-to-r from-red-500 to-red-600 animate-pulse"
                    : isUrgent
                      ? "bg-gradient-to-r from-orange-400 to-orange-500"
                      : "bg-gradient-to-r from-green-400 to-emerald-500"
                }`}
                style={{ width: `${Math.min(slaProgress, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column: Main Content (8 cols) */}
          <div className="col-span-8 space-y-6">
            {/* AI Reasoning Overlay Card */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden transform hover:shadow-xl transition-all duration-300">
              <div className="bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 p-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white/20 backdrop-blur-lg rounded-xl flex items-center justify-center">
                    <Zap className="text-white" size={24} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">
                      AI Reasoning Overlay
                    </h2>
                    <p className="text-white/80 text-sm">
                      Intelligent Classification & Analysis
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-4">
                {/* Classification Details */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-purple-50 rounded-xl border-2 border-purple-100 hover:border-purple-300 transition-colors">
                    <div className="flex items-center gap-2 mb-2">
                      <Tag size={16} className="text-purple-600" />
                      <span className="text-xs font-semibold text-purple-900 uppercase tracking-wide">
                        Category
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-purple-900">
                        {ticket.category}
                      </span>
                      <div className="flex items-center gap-1">
                        <TrendingUp size={14} className="text-purple-600" />
                        <span className="text-sm font-bold text-purple-600">
                          {Math.round(ticket.classification_confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <div
                    className={`p-4 rounded-xl border-2 transition-colors ${
                      ticket.severity === "P1"
                        ? "bg-red-50 border-red-100 hover:border-red-300"
                        : ticket.severity === "P2"
                          ? "bg-orange-50 border-orange-100 hover:border-orange-300"
                          : ticket.severity === "P3"
                            ? "bg-yellow-50 border-yellow-100 hover:border-yellow-300"
                            : "bg-blue-50 border-blue-100 hover:border-blue-300"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Target
                        size={16}
                        className={
                          ticket.severity === "P1"
                            ? "text-red-600"
                            : ticket.severity === "P2"
                              ? "text-orange-600"
                              : ticket.severity === "P3"
                                ? "text-yellow-600"
                                : "text-blue-600"
                        }
                      />
                      <span
                        className="text-xs font-semibold uppercase tracking-wide"
                        style={{
                          color:
                            ticket.severity === "P1"
                              ? "#DC2626"
                              : ticket.severity === "P2"
                                ? "#EA580C"
                                : ticket.severity === "P3"
                                  ? "#CA8A04"
                                  : "#2563EB",
                        }}
                      >
                        Severity
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span
                        className="text-lg font-bold"
                        style={{
                          color:
                            ticket.severity === "P1"
                              ? "#991B1B"
                              : ticket.severity === "P2"
                                ? "#9A3412"
                                : ticket.severity === "P3"
                                  ? "#854D0E"
                                  : "#1E40AF",
                        }}
                      >
                        {ticket.severity} - {ticket.severity_name}
                      </span>
                      <span
                        className="text-xs font-medium"
                        style={{
                          color:
                            ticket.severity === "P1"
                              ? "#DC2626"
                              : ticket.severity === "P2"
                                ? "#EA580C"
                                : ticket.severity === "P3"
                                  ? "#CA8A04"
                                  : "#2563EB",
                        }}
                      >
                        {ticket.sla_hours}h SLA
                      </span>
                    </div>
                  </div>
                </div>

                {/* AI Reasoning */}
                {ticket.classification_reasoning && (
                  <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
                    <div className="flex items-start gap-3">
                      <Activity
                        size={18}
                        className="text-indigo-600 mt-0.5 flex-shrink-0"
                      />
                      <div>
                        <p className="text-xs font-semibold text-indigo-900 uppercase tracking-wide mb-1">
                          AI Reasoning
                        </p>
                        <p className="text-sm text-gray-700">
                          {ticket.classification_reasoning}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Urgency Signals */}
                {ticket.urgency_signals &&
                  ticket.urgency_signals.length > 0 && (
                    <div className="p-4 bg-amber-50 rounded-xl border border-amber-100">
                      <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle size={18} className="text-amber-600" />
                        <span className="text-xs font-semibold text-amber-900 uppercase tracking-wide">
                          Detected Urgency Signals (
                          {ticket.urgency_signals.length})
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {ticket.urgency_signals
                          .slice(0, 6)
                          .map((signal, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1 bg-white text-amber-700 text-xs font-medium rounded-full border border-amber-200 hover:bg-amber-100 transition-colors animate-fadeIn"
                              style={{ animationDelay: `${idx * 100}ms` }}
                            >
                              {signal.replace(/_/g, " ")}
                            </span>
                          ))}
                      </div>
                    </div>
                  )}
              </div>
            </div>

            {/* Email Content Card */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="border-b border-gray-200 px-6 py-4 bg-gray-50">
                <div className="flex items-center gap-2">
                  <Mail size={20} className="text-gray-600" />
                  <h3 className="font-semibold text-gray-900">
                    Original Email
                  </h3>
                </div>
              </div>
              <div className="p-6">
                <h4 className="text-lg font-bold text-gray-900 mb-2">
                  {ticket.subject}
                </h4>
                <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                  {ticket.body}
                </div>
              </div>
            </div>

            {/* AI Response Preview */}
            {ticket.ai_response_text && (
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/20 backdrop-blur-lg rounded-lg flex items-center justify-center">
                      <MessageSquare className="text-white" size={20} />
                    </div>
                    <div>
                      <h3 className="font-bold text-white">
                        AI Generated Response
                      </h3>
                      <p className="text-white/80 text-sm">
                        Confidence:{" "}
                        {Math.round((ticket.ai_response_confidence || 0) * 100)}
                        %
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <ResponsePreview ticket={ticket} />
                </div>
              </div>
            )}

            {/* Thread & Deduplication */}
            {ticket.similar_tickets && ticket.similar_tickets.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="border-b border-gray-200 px-6 py-4 bg-gray-50">
                  <div className="flex items-center gap-2">
                    <LinkIcon size={20} className="text-gray-600" />
                    <h3 className="font-semibold text-gray-900">
                      Related Tickets
                    </h3>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">
                      {ticket.similar_tickets.length}
                    </span>
                  </div>
                </div>
                <div className="p-6 space-y-3">
                  {ticket.similar_tickets.map((similar, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all cursor-pointer"
                      onClick={() => navigate(`/ticket/${similar.ticket_id}`)}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-sm font-semibold text-gray-900">
                            {similar.ticket_id}
                          </p>
                          <p className="text-sm text-gray-600 line-clamp-1">
                            {similar.subject}
                          </p>
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(similar.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Customer Insights Sidebar (4 cols) */}
          <div className="col-span-4 space-y-6">
            {/* Customer Profile Card */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden sticky top-24">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-6">
                <div className="flex items-center gap-3">
                  <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center shadow-lg">
                    <User size={28} className="text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">
                      Customer Insights
                    </h3>
                    <p className="text-white/80 text-sm">
                      Profile & Account Details
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-4">
                {/* Contact Information */}
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <User size={18} className="text-gray-600 flex-shrink-0" />
                    <div>
                      <p className="text-xs text-gray-500 font-medium">
                        Contact Name
                      </p>
                      <p className="text-sm font-semibold text-gray-900">
                        {ticket.user_name ||
                          ticket.sender
                            ?.split("@")[0]
                            ?.replace(/[._]/g, " ")
                            ?.split(" ")
                            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                            .join(" ") ||
                          "N/A"}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <Mail size={18} className="text-gray-600 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-500 font-medium">Email</p>
                      <p className="text-sm font-semibold text-gray-900 truncate">
                        {ticket.sender}
                      </p>
                    </div>
                  </div>

                  {ticket.user_phone && (
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <Phone
                        size={18}
                        className="text-gray-600 flex-shrink-0"
                      />
                      <div>
                        <p className="text-xs text-gray-500 font-medium">
                          Phone
                        </p>
                        <p className="text-sm font-semibold text-gray-900">
                          {ticket.user_phone}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <Building2
                      size={18}
                      className="text-gray-600 flex-shrink-0"
                    />
                    <div>
                      <p className="text-xs text-gray-500 font-medium">
                        Company
                      </p>
                      <p className="text-sm font-semibold text-gray-900">
                        {ticket.customer_company ||
                          ticket.sender?.split("@")[1] ||
                          "N/A"}
                      </p>
                    </div>
                  </div>

                  {ticket.user_role && (
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <Award
                        size={18}
                        className="text-gray-600 flex-shrink-0"
                      />
                      <div>
                        <p className="text-xs text-gray-500 font-medium">
                          Role
                        </p>
                        <p className="text-sm font-semibold text-gray-900">
                          {ticket.user_role}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Account Tier */}
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg border-2 border-amber-200">
                    <div className="flex items-center gap-2">
                      <Award size={20} className="text-amber-600" />
                      <span className="text-sm font-medium text-gray-700">
                        Account Tier
                      </span>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold ${
                        ticket.customer_tier === "Gold"
                          ? "bg-gradient-to-r from-yellow-400 to-amber-500 text-white shadow-lg"
                          : ticket.customer_tier === "Silver"
                            ? "bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800"
                            : "bg-gradient-to-r from-orange-300 to-orange-400 text-white"
                      }`}
                    >
                      {ticket.customer_tier || "Standard"}
                    </span>
                  </div>
                </div>

                {/* Metadata */}
                <div className="pt-4 border-t border-gray-200 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Created</span>
                    <span className="font-medium text-gray-900">
                      {new Date(ticket.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">SLA Deadline</span>
                    <span
                      className={`font-bold ${isBreached ? "text-red-600" : "text-gray-900"}`}
                    >
                      {new Date(ticket.sla_deadline).toLocaleString()}
                    </span>
                  </div>
                  {ticket.thread_count > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Thread Count</span>
                      <span className="font-medium text-gray-900">
                        {ticket.thread_count}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Animations */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out forwards;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>
    </div>
  );
}
