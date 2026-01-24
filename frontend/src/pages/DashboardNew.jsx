/**
 * Enhanced Dashboard Page
 * Beautiful UI with animations, modern design, and comprehensive statistics
 */

import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  Mail,
  Clock,
  CheckCircle,
  BarChart3,
  AlertCircle,
  Plus,
  PieChart,
  Zap,
  Users,
  Activity,
  Target,
  Filter,
  Search,
  RefreshCw,
} from "lucide-react";
import { getDashboardStats, getTickets } from "../services/api";
import TicketCard from "../components/TicketCard";
import UrgencyBadge from "../components/UrgencyBadge";
import { useNavigate } from "react-router-dom";

// Helper function to format response time
const formatResponseTime = (seconds) => {
  if (!seconds || seconds <= 0) return "N/A";

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

export default function DashboardNew() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async (showRefresh = false) => {
    try {
      if (showRefresh) setRefreshing(true);
      else setLoading(true);

      const [dashStats, ticketsData] = await Promise.all([
        getDashboardStats(),
        getTickets({ page: 1, page_size: 50 }),
      ]);

      setStats(dashStats);
      setTickets(ticketsData.tickets);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
        <div className="text-center">
          <div className="relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 border-4 border-primary-200 rounded-full animate-ping"></div>
            <div className="absolute inset-0 border-4 border-t-primary-600 border-r-purple-600 rounded-full animate-spin"></div>
            <div
              className="absolute inset-2 border-4 border-b-pink-500 rounded-full animate-spin"
              style={{ animationDirection: "reverse", animationDuration: "1s" }}
            ></div>
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            Loading IntelliDesk AI
          </h2>
          <p className="text-gray-600">Preparing your dashboard...</p>
        </div>
      </div>
    );
  }

  const filteredTickets = tickets.filter((ticket) => {
    const matchesFilter = filter === "all" || ticket.severity === filter;
    const matchesSearch =
      !searchTerm ||
      ticket.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.body.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.ticket_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Enhanced Header */}
      <div className="bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Title */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-14 h-14 bg-gradient-to-br from-primary-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg transform hover:rotate-12 transition-all duration-300">
                  <Zap className="text-white" size={28} />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-primary-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  IntelliDesk AI
                </h1>
                <p className="text-sm text-gray-600 font-medium">
                  ⚡ The Perfect Response, Every Time
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => loadDashboard(true)}
                disabled={refreshing}
                className="p-2.5 hover:bg-gray-100 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                title="Refresh"
              >
                <RefreshCw
                  size={20}
                  className={`text-gray-600 ${refreshing ? "animate-spin" : ""}`}
                />
              </button>
              <button
                onClick={() => navigate("/add-ticket")}
                className="px-6 py-2.5 bg-gradient-to-r from-primary-500 to-purple-600 hover:from-primary-600 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
              >
                <Plus size={20} />
                New Ticket
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards with Animations */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Mail}
            label="Today's Tickets"
            value={stats?.total_tickets_today || 0}
            change="+12%"
            changePositive={true}
            gradient="from-blue-500 to-cyan-500"
            delay="0"
          />
          <StatCard
            icon={Clock}
            label="Avg Response Time"
            value={formatResponseTime(stats?.avg_response_time || 0)}
            change="-23%"
            changePositive={true}
            gradient="from-purple-500 to-pink-500"
            delay="100"
          />
          <StatCard
            icon={CheckCircle}
            label="SLA Compliance"
            value={`${Math.round(stats?.sla_compliance_rate || 0)}%`}
            change="+5%"
            changePositive={true}
            gradient="from-green-500 to-emerald-500"
            delay="200"
          />
          <StatCard
            icon={TrendingUp}
            label="Auto-Response Rate"
            value={`${Math.round(stats?.auto_response_rate || 0)}%`}
            change="+8%"
            changePositive={true}
            gradient="from-orange-500 to-red-500"
            delay="300"
          />
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Category Distribution */}
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden transform hover:scale-[1.02] transition-all duration-300">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-500 p-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-lg rounded-xl flex items-center justify-center">
                  <PieChart size={24} className="text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    Category Distribution
                  </h2>
                  <p className="text-white/80 text-sm">
                    Email classification breakdown
                  </p>
                </div>
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {stats?.top_categories?.map((cat, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    style={{
                      animation: `slideInLeft 0.5s ease-out ${idx * 100}ms both`,
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-lg flex items-center justify-center text-white font-bold">
                        {idx + 1}
                      </div>
                      <span className="text-sm font-semibold text-gray-900">
                        {cat.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-1000"
                          style={{
                            width: `${(cat.count / (stats.total_tickets_today || 1)) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-sm font-bold text-gray-900 w-8 text-right">
                        {cat.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Severity Distribution */}
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden transform hover:scale-[1.02] transition-all duration-300">
            <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-lg rounded-xl flex items-center justify-center">
                  <Target size={24} className="text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    Severity Overview
                  </h2>
                  <p className="text-white/80 text-sm">Priority distribution</p>
                </div>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(stats?.severity_distribution || {}).map(
                  ([severity, count], idx) => (
                    <div
                      key={severity}
                      className={`p-4 rounded-xl border-2 transition-all hover:scale-105 ${
                        severity === "P1"
                          ? "bg-red-50 border-red-200 hover:border-red-400"
                          : severity === "P2"
                            ? "bg-orange-50 border-orange-200 hover:border-orange-400"
                            : severity === "P3"
                              ? "bg-yellow-50 border-yellow-200 hover:border-yellow-400"
                              : "bg-blue-50 border-blue-200 hover:border-blue-400"
                      }`}
                      style={{
                        animation: `fadeInUp 0.5s ease-out ${idx * 100}ms both`,
                      }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <UrgencyBadge severity={severity} size="sm" />
                        <span
                          className={`text-2xl font-black ${
                            severity === "P1"
                              ? "text-red-600"
                              : severity === "P2"
                                ? "text-orange-600"
                                : severity === "P3"
                                  ? "text-yellow-600"
                                  : "text-blue-600"
                          }`}
                        >
                          {count}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600 font-medium">
                        {Math.round((count / tickets.length) * 100)}% of total
                      </div>
                    </div>
                  ),
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search
                size={20}
                className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
              />
              <input
                type="text"
                placeholder="Search tickets by ID, subject, or content..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-400 focus:ring-4 focus:ring-primary-100 transition-all outline-none"
              />
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2 overflow-x-auto">
              <Filter size={20} className="text-gray-600 flex-shrink-0" />
              <button
                onClick={() => setFilter("all")}
                className={`px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
                  filter === "all"
                    ? "bg-gradient-to-r from-primary-500 to-purple-600 text-white shadow-lg"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                All ({tickets.length})
              </button>
              {Object.entries(stats?.severity_distribution || {}).map(
                ([severity, count]) => (
                  <button
                    key={severity}
                    onClick={() => setFilter(severity)}
                    className={`px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
                      filter === severity
                        ? "bg-gradient-to-r from-primary-500 to-purple-600 text-white shadow-lg"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {severity} ({count})
                  </button>
                ),
              )}
            </div>
          </div>
        </div>

        {/* Tickets Grid */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Activity size={28} />
              Active Tickets
              <span className="text-lg font-normal text-gray-500">
                ({filteredTickets.length}{" "}
                {filteredTickets.length === 1 ? "ticket" : "tickets"})
              </span>
            </h2>
          </div>

          {filteredTickets.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTickets.map((ticket, idx) => (
                <div
                  key={ticket.ticket_id}
                  style={{
                    animation: `fadeInUp 0.5s ease-out ${idx * 50}ms both`,
                  }}
                >
                  <TicketCard
                    ticket={ticket}
                    onClick={(t) => navigate(`/ticket/${t.ticket_id}`)}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle size={40} className="text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No tickets found
              </h3>
              <p className="text-gray-600 mb-6">
                {searchTerm
                  ? `No tickets match your search "${searchTerm}"`
                  : filter !== "all"
                    ? `No ${filter} tickets found`
                    : "Start by creating your first ticket"}
              </p>
              {!searchTerm && filter === "all" && (
                <button
                  onClick={() => navigate("/add-ticket")}
                  className="px-6 py-3 bg-gradient-to-r from-primary-500 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all inline-flex items-center gap-2"
                >
                  <Plus size={20} />
                  Create First Ticket
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Custom Animations */}
      <style>{`
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
      `}</style>
    </div>
  );
}

// Enhanced Stat Card Component
function StatCard({
  icon: Icon,
  label,
  value,
  change,
  changePositive,
  gradient,
  delay,
}) {
  return (
    <div
      className="bg-white rounded-2xl shadow-lg overflow-hidden transform hover:scale-105 hover:shadow-xl transition-all duration-300 cursor-pointer"
      style={{
        animation: `scaleIn 0.5s ease-out ${delay}ms both`,
      }}
    >
      <div className={`bg-gradient-to-br ${gradient} p-6`}>
        <div className="flex items-center justify-between">
          <div className="w-14 h-14 bg-white/20 backdrop-blur-lg rounded-xl flex items-center justify-center">
            <Icon size={28} className="text-white" />
          </div>
          <div
            className={`text-sm font-bold px-3 py-1 rounded-full ${
              changePositive
                ? "bg-white/20 text-white"
                : "bg-red-500/20 text-white"
            }`}
          >
            {change}
          </div>
        </div>
      </div>
      <div className="p-6">
        <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
        <p className="text-3xl font-black text-gray-900">{value}</p>
      </div>
    </div>
  );
}
