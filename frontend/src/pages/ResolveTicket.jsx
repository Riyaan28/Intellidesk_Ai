/**
 * ResolveTicket Page
 * Manual ticket resolution - write and send reply email
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Mail,
  Send,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Zap,
} from "lucide-react";
import { getTicket, resolveTicketWithEmail } from "../services/api";
import UrgencyBadge from "../components/UrgencyBadge";

export default function ResolveTicket() {
  const { ticketId } = useParams();
  const navigate = useNavigate();

  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [autoSent, setAutoSent] = useState(false);
  const [llmGenerated, setLlmGenerated] = useState(false);

  useEffect(() => {
    loadTicket();
  }, [ticketId]);

  const loadTicket = async () => {
    try {
      setLoading(true);
      const data = await getTicket(ticketId);
      setTicket(data);

      // Fetch perfect LLM-generated reply
      try {
        const llmResponse = await fetch(
          `http://localhost:8000/api/tickets/${ticketId}/perfect-reply`,
        );
        if (llmResponse.ok) {
          const llmData = await llmResponse.json();
          setReplyText(llmData.reply_text);
          setLlmGenerated(true);

          // Check if it was auto-sent (confidence > 90%)
          if (llmData.auto_sent) {
            setAutoSent(true);
            setSuccess(true);
            // Redirect after showing success
            setTimeout(() => {
              navigate("/");
            }, 3000);
          }
        } else {
          // Fallback to basic template
          setReplyText(
            `Dear ${data.sender.split("@")[0]},\n\nThank you for contacting us.\n\n[Your resolution here]\n\nBest regards,\nSupport Team`,
          );
        }
      } catch (err) {
        console.error("Failed to fetch LLM reply:", err);
        // Fallback template
        setReplyText(
          `Dear ${data.sender.split("@")[0]},\n\nThank you for contacting us.\n\n[Your resolution here]\n\nBest regards,\nSupport Team`,
        );
      }
    } catch (error) {
      console.error("Failed to load ticket:", error);
      setError("Failed to load ticket details");
    } finally {
      setLoading(false);
    }
  };

  const handleSendResolution = async () => {
    if (!replyText.trim()) {
      setError("Please write a reply message");
      return;
    }

    try {
      setSending(true);
      setError(null);

      // Send resolution email and mark ticket as resolved
      await resolveTicketWithEmail(ticketId, {
        reply_text: replyText,
        recipient: ticket.sender,
      });

      setSuccess(true);

      // Show success message and redirect after 2 seconds
      setTimeout(() => {
        navigate("/");
      }, 2000);
    } catch (error) {
      console.error("Failed to send resolution:", error);
      setError(
        error.response?.data?.detail ||
          "Failed to send email. Please try again.",
      );
      setSending(false);
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
          <AlertCircle size={48} className="text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Ticket not found</p>
          <button onClick={() => navigate("/")} className="btn-primary mt-4">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          {autoSent ? (
            <>
              <div className="relative">
                <Zap
                  size={64}
                  className="text-yellow-500 mx-auto mb-4 animate-pulse"
                />
                <Sparkles
                  size={32}
                  className="text-yellow-400 absolute top-0 right-1/3 animate-ping"
                />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Auto-Sent Successfully! ⚡
              </h2>
              <p className="text-gray-600 mb-2">
                High confidence (&gt;90%) detected - email automatically sent to{" "}
                {ticket.sender}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Ticket marked as resolved and response delivered instantly.
              </p>
            </>
          ) : (
            <>
              <CheckCircle size={64} className="text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Resolution Sent Successfully!
              </h2>
              <p className="text-gray-600 mb-4">
                Email sent to {ticket.sender} and ticket marked as resolved.
              </p>
            </>
          )}
          <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

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
                <h1 className="text-xl font-bold text-gray-900">
                  Resolve Ticket
                </h1>
                <p className="text-sm text-gray-500">
                  Write and send resolution email
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Ticket Details */}
          <div className="lg:col-span-1">
            <div className="card">
              <h2 className="font-semibold text-gray-900 mb-4">
                Ticket Details
              </h2>

              <div className="space-y-4">
                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Ticket ID
                  </span>
                  <p className="text-sm font-mono text-gray-900 mt-1">
                    {ticket.ticket_id}
                  </p>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Severity
                  </span>
                  <div className="mt-1">
                    <UrgencyBadge severity={ticket.severity} size="sm" />
                  </div>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Category
                  </span>
                  <p className="text-sm text-gray-900 mt-1">
                    {ticket.category}
                  </p>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    From
                  </span>
                  <p className="text-sm text-gray-900 mt-1 break-all">
                    {ticket.sender}
                  </p>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Subject
                  </span>
                  <p className="text-sm text-gray-900 mt-1">{ticket.subject}</p>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-600">
                    Original Message
                  </span>
                  <div className="mt-1 p-3 bg-gray-50 rounded-lg max-h-64 overflow-y-auto">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {ticket.body}
                    </p>
                  </div>
                </div>

                {ticket.urgency_signals &&
                  ticket.urgency_signals.length > 0 && (
                    <div>
                      <span className="text-xs font-medium text-gray-600">
                        Urgency Signals
                      </span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {ticket.urgency_signals
                          .slice(0, 3)
                          .map((signal, idx) => (
                            <span
                              key={idx}
                              className="text-xs badge bg-red-100 text-red-800"
                            >
                              {signal}
                            </span>
                          ))}
                      </div>
                    </div>
                  )}
              </div>
            </div>
          </div>

          {/* Right: Resolution Form */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Mail size={20} className="text-primary-600" />
                <h2 className="font-semibold text-gray-900">
                  Compose Resolution Email
                </h2>
              </div>

              {/* Recipient (read-only) */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  To:
                </label>
                <div className="px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg">
                  <span className="text-sm text-gray-900">{ticket.sender}</span>
                </div>
              </div>

              {/* Reply Text Area */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Your Reply: *
                  </label>
                  {llmGenerated && (
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                      <Sparkles size={12} />
                      AI Generated
                    </span>
                  )}
                </div>
                <textarea
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Write your resolution email here..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows={16}
                  disabled={sending}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {replyText.length} characters
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                  <AlertCircle
                    size={20}
                    className="text-red-600 flex-shrink-0 mt-0.5"
                  />
                  <div>
                    <p className="text-sm font-medium text-red-800">Error</p>
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                <button
                  onClick={handleSendResolution}
                  disabled={sending || !replyText.trim()}
                  className={`btn-primary flex items-center gap-2 ${
                    sending || !replyText.trim()
                      ? "opacity-50 cursor-not-allowed"
                      : ""
                  }`}
                >
                  {sending ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send size={18} />
                      Send & Resolve Ticket
                    </>
                  )}
                </button>

                <button
                  onClick={() => navigate("/")}
                  disabled={sending}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>

              {/* Helper Text */}
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-800">
                  💡 <strong>Note:</strong> When you click "Send & Resolve
                  Ticket", the system will:
                  <br />• Send this email to {ticket.sender}
                  <br />• Mark the ticket status as "Resolved"
                  <br />• Record the resolution timestamp
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
