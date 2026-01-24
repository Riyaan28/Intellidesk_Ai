/**
 * UrgencyBadge Component
 * Displays severity level with color coding
 */

import React from "react";
import { AlertCircle, AlertTriangle, Info, CheckCircle } from "lucide-react";

const severityConfig = {
  P1: {
    label: "Critical",
    color: "bg-red-100 text-red-800 border-red-200",
    icon: AlertCircle,
    dotColor: "bg-red-500",
  },
  P2: {
    label: "High",
    color: "bg-orange-100 text-orange-800 border-orange-200",
    icon: AlertTriangle,
    dotColor: "bg-orange-500",
  },
  P3: {
    label: "Medium",
    color: "bg-blue-100 text-blue-800 border-blue-200",
    icon: Info,
    dotColor: "bg-blue-500",
  },
  P4: {
    label: "Low",
    color: "bg-green-100 text-green-800 border-green-200",
    icon: CheckCircle,
    dotColor: "bg-green-500",
  },
};

export default function UrgencyBadge({
  severity,
  showLabel = true,
  size = "md",
}) {
  const config = severityConfig[severity] || severityConfig.P3;
  const Icon = config.icon;

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-sm",
    lg: "px-3 py-1.5 text-base",
  };

  const iconSizes = {
    sm: 12,
    md: 14,
    lg: 16,
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium border ${config.color} ${sizeClasses[size]}`}
    >
      <Icon size={iconSizes[size]} />
      {showLabel && (
        <>
          <span>{severity}</span>
          <span className="font-normal">·</span>
          <span>{config.label}</span>
        </>
      )}
    </span>
  );
}
