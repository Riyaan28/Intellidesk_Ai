/**
 * ResponsePreview Component
 * Shows AI-generated response alongside original email
 */

import React from "react";
import { Bot, User, CheckCircle, AlertCircle } from "lucide-react";

export default function ResponsePreview({ ticket }) {
  if (!ticket.ai_response_text) {
    return null;
  }

  const responseTypeConfig = {
    perfect_match: {
      label: "Perfect Match",
      color: "text-green-600",
      icon: CheckCircle,
    },
    partial_match: {
      label: "Partial Match",
      color: "text-blue-600",
      icon: AlertCircle,
    },
    resolution_based: {
      label: "Similar Tickets",
      color: "text-purple-600",
      icon: Bot,
    },
    acknowledgment: {
      label: "Acknowledgment",
      color: "text-gray-600",
      icon: Bot,
    },
  };

  const config =
    responseTypeConfig[ticket.ai_response_type] ||
    responseTypeConfig.acknowledgment;
  const Icon = config.icon;

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Original Email */}
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <User size={18} className="text-gray-600" />
          <h3 className="font-semibold text-gray-900">Customer Email</h3>
        </div>

        <div className="space-y-2">
          <div>
            <span className="text-xs font-medium text-gray-500">From:</span>
            <p className="text-sm text-gray-900">{ticket.sender}</p>
          </div>

          <div>
            <span className="text-xs font-medium text-gray-500">Subject:</span>
            <p className="text-sm text-gray-900">{ticket.subject}</p>
          </div>

          <div>
            <span className="text-xs font-medium text-gray-500">Message:</span>
            <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">
              {ticket.body}
            </p>
          </div>
        </div>
      </div>

      {/* AI Response */}
      <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Bot size={18} className="text-blue-600" />
            <h3 className="font-semibold text-gray-900">AI Response</h3>
          </div>

          <div className="flex items-center gap-2">
            <Icon size={16} className={config.color} />
            <span className={`text-xs font-medium ${config.color}`}>
              {config.label}
            </span>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="mb-3 p-2 bg-white rounded-lg">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-gray-600">
              AI Confidence
            </span>
            <span className="text-xs font-bold text-blue-600">
              {Math.round(ticket.ai_response_confidence * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div
              className="bg-blue-600 h-1.5 rounded-full transition-all"
              style={{ width: `${ticket.ai_response_confidence * 100}%` }}
            />
          </div>
        </div>

        {/* Response Text */}
        <div className="bg-white rounded-lg p-3">
          <p className="text-sm text-gray-700 whitespace-pre-wrap">
            {ticket.ai_response_text}
          </p>
        </div>

        {/* Auto-Send Status */}
        {ticket.auto_sent && (
          <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2">
              <CheckCircle size={14} className="text-green-600" />
              <span className="text-xs font-medium text-green-800">
                Auto-sent to customer (Confidence {">"}95% & Priority ≤P3)
              </span>
            </div>
          </div>
        )}

        {!ticket.auto_sent && ticket.ai_response_confidence >= 0.95 && (
          <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertCircle size={14} className="text-yellow-600" />
              <span className="text-xs font-medium text-yellow-800">
                Pending review before sending
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
