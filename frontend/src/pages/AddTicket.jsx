/**
 * Add Ticket Page
 * Manual ticket creation form
 */

import React, { useState } from "react";
import { Mail, Send, Plus, Trash2, CheckCircle } from "lucide-react";
import { processEmail } from "../services/api";

export default function AddTicket() {
  const [tickets, setTickets] = useState([
    { id: 1, subject: "", body: "", sender: "" },
  ]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  const addTicket = () => {
    const newId = Math.max(...tickets.map((t) => t.id), 0) + 1;
    setTickets([...tickets, { id: newId, subject: "", body: "", sender: "" }]);
  };

  const removeTicket = (id) => {
    if (tickets.length > 1) {
      setTickets(tickets.filter((t) => t.id !== id));
    }
  };

  const updateTicket = (id, field, value) => {
    setTickets(
      tickets.map((t) => (t.id === id ? { ...t, [field]: value } : t)),
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setResults([]);
    setShowResults(false);

    try {
      const processedResults = [];

      for (const ticket of tickets) {
        if (ticket.subject && ticket.body && ticket.sender) {
          try {
            const result = await processEmail({
              subject: ticket.subject,
              body: ticket.body,
              sender: ticket.sender,
            });
            processedResults.push({
              ...ticket,
              success: true,
              ticket_id: result.ticket_id,
              category: result.classification.category,
              confidence: result.classification.confidence,
              severity: result.urgency.severity,
              method_used: result.classification.method_used,
            });
          } catch (error) {
            processedResults.push({
              ...ticket,
              success: false,
              error: error.message,
            });
          }
        }
      }

      setResults(processedResults);
      setShowResults(true);

      // Reset form after successful submission
      if (processedResults.every((r) => r.success)) {
        setTimeout(() => {
          setTickets([{ id: 1, subject: "", body: "", sender: "" }]);
          setShowResults(false);
        }, 3000);
      }
    } catch (error) {
      console.error("Failed to process tickets:", error);
    } finally {
      setProcessing(false);
    }
  };

  const isFormValid = tickets.every((t) => t.subject && t.body && t.sender);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Plus className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Add Ticket</h1>
                <p className="text-xs text-gray-500">
                  Manually create support tickets
                </p>
              </div>
            </div>

            <button
              onClick={() => (window.location.href = "/")}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success Message */}
        {showResults && results.every((r) => r.success) && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
            <CheckCircle className="text-green-600" size={20} />
            <div>
              <p className="text-sm font-medium text-green-900">
                Successfully processed {results.length} ticket(s)!
              </p>
              <p className="text-xs text-green-700 mt-1">
                Redirecting to dashboard...
              </p>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {tickets.map((ticket, index) => (
            <div key={ticket.id} className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Mail size={20} />
                  Ticket #{index + 1}
                </h3>
                {tickets.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeTicket(ticket.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>

              <div className="space-y-4">
                {/* Sender Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sender Email *
                  </label>
                  <input
                    type="email"
                    value={ticket.sender}
                    onChange={(e) =>
                      updateTicket(ticket.id, "sender", e.target.value)
                    }
                    placeholder="customer@company.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>

                {/* Subject */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Subject *
                  </label>
                  <input
                    type="text"
                    value={ticket.subject}
                    onChange={(e) =>
                      updateTicket(ticket.id, "subject", e.target.value)
                    }
                    placeholder="Brief description of the issue"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>

                {/* Body */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Message Body *
                  </label>
                  <textarea
                    value={ticket.body}
                    onChange={(e) =>
                      updateTicket(ticket.id, "body", e.target.value)
                    }
                    placeholder="Detailed description of the issue..."
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Provide as much detail as possible for better classification
                  </p>
                </div>
              </div>
            </div>
          ))}

          {/* Add More Button */}
          <button
            type="button"
            onClick={addTicket}
            className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-primary-500 hover:text-primary-600 transition-colors flex items-center justify-center gap-2"
          >
            <Plus size={20} />
            Add Another Ticket
          </button>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!isFormValid || processing}
            className="w-full btn-primary py-3 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {processing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Processing {tickets.length} ticket(s)...
              </>
            ) : (
              <>
                <Send size={20} />
                Submit {tickets.length} Ticket{tickets.length > 1 ? "s" : ""}
              </>
            )}
          </button>
        </form>

        {/* Results */}
        {showResults && results.length > 0 && (
          <div className="mt-8 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Processing Results
            </h2>
            {results.map((result, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border ${
                  result.success
                    ? "bg-green-50 border-green-200"
                    : "bg-red-50 border-red-200"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">
                      {result.subject}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      From: {result.sender}
                    </p>
                    {result.success ? (
                      <div className="mt-2 space-y-1 text-sm">
                        <p className="text-green-900">
                          ✓ Ticket ID:{" "}
                          <span className="font-mono">{result.ticket_id}</span>
                        </p>
                        <p className="text-green-800">
                          Category: {result.category} (
                          {Math.round(result.confidence * 100)}% confidence)
                        </p>
                        <p className="text-green-800">
                          Priority: {result.severity}
                        </p>
                        <p className="text-green-700 text-xs">
                          Method: {result.method_used}
                        </p>
                      </div>
                    ) : (
                      <p className="mt-2 text-sm text-red-600">
                        ✗ Error: {result.error}
                      </p>
                    )}
                  </div>
                  <div className="ml-4">
                    {result.success ? (
                      <CheckCircle className="text-green-600" size={24} />
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-red-600 flex items-center justify-center text-white text-xs font-bold">
                        !
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
