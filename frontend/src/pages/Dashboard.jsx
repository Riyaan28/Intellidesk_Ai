/**
 * Dashboard Page
 * Main dashboard showing tickets, stats, and analytics
 */

import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  Mail,
  Clock,
  CheckCircle,
  BarChart3,
  AlertCircle,
} from "lucide-react";
import { getDashboardStats, getTickets } from "../services/api";
import TicketCard from "../components/TicketCard";
import UrgencyBadge from "../components/UrgencyBadge";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const [dashStats, ticketsData] = await Promise.all([
        getDashboardStats(),
        getTickets({ page: 1, page_size: 20 }),
      ]);

      setStats(dashStats);
      setTickets(ticketsData.tickets);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const filteredTickets =
    filter === "all" ? tickets : tickets.filter((t) => t.severity === filter);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Mail className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  IntelliDesk AI
                </h1>
                <p className="text-xs text-gray-500">
                  The Perfect Response, Every Time
                </p>
              </div>
            </div>

            <button onClick={loadDashboard} className="btn-primary">
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Mail}
            label="Today's Tickets"
            value={stats?.total_tickets_today || 0}
            change="+12%"
            changePositive={true}
          />
          <StatCard
            icon={Clock}
            label="Avg Response Time"
            value={`${Math.round(stats?.avg_response_time || 0)}s`}
            change="-23%"
            changePositive={true}
          />
          <StatCard
            icon={CheckCircle}
            label="SLA Compliance"
            value={`${Math.round(stats?.sla_compliance_rate || 0)}%`}
            change="+5%"
            changePositive={true}
          />
          <StatCard
            icon={TrendingUp}
            label="Auto-Response Rate"
            value={`${Math.round(stats?.auto_response_rate || 0)}%`}
            change="+8%"
            changePositive={true}
          />
        </div>

        {/* Category Distribution */}
        <div className="card mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 size={20} />
            Top Categories
          </h2>
          <div className="space-y-3">
            {stats?.top_categories?.map((cat, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{cat.category}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{
                        width: `${(cat.count / stats.total_tickets_today) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-8 text-right">
                    {cat.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Severity Filter */}
        <div className="mb-6">
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setFilter("all")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === "all"
                  ? "bg-primary-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              }`}
            >
              All Tickets ({tickets.length})
            </button>
            {Object.entries(stats?.severity_distribution || {}).map(
              ([severity, count]) => (
                <button
                  key={severity}
                  onClick={() => setFilter(severity)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === severity
                      ? "bg-primary-600 text-white"
                      : "bg-white text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <UrgencyBadge
                    severity={severity}
                    showLabel={false}
                    size="sm"
                  />
                  <span className="ml-2">
                    {severity} ({count})
                  </span>
                </button>
              ),
            )}
          </div>
        </div>

        {/* Tickets Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredTickets.map((ticket) => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              onClick={setSelectedTicket}
            />
          ))}
        </div>

        {filteredTickets.length === 0 && (
          <div className="text-center py-12 card">
            <AlertCircle size={48} className="text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No tickets found
            </h3>
            <p className="text-gray-600">
              {filter === "all"
                ? "No tickets have been created yet."
                : `No ${filter} priority tickets.`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, change, changePositive }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <Icon size={24} className="text-gray-400" />
        <span
          className={`text-xs font-medium ${
            changePositive ? "text-green-600" : "text-red-600"
          }`}
        >
          {change}
        </span>
      </div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );
}
