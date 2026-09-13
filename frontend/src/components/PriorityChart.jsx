import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const COLORS = { HIGH: "#dc2626", MEDIUM: "#d97706", LOW: "#94a3b8" };

export default function PriorityChart({ distribution }) {
  const data = [
    { priority: "HIGH", count: distribution?.HIGH ?? 0 },
    { priority: "MEDIUM", count: distribution?.MEDIUM ?? 0 },
    { priority: "LOW", count: distribution?.LOW ?? 0 },
  ];

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: -12, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
        <XAxis dataKey="priority" tick={{ fontSize: 12.5, fill: "#475569" }} axisLine={{ stroke: "#e2e8f0" }} tickLine={false} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#475569" }} axisLine={false} tickLine={false} />
        <Tooltip
          cursor={{ fill: "#f1f5f9" }}
          contentStyle={{ borderRadius: 8, borderColor: "#e2e8f0", fontSize: 13 }}
        />
        <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={64}>
          {data.map((d) => (
            <Cell key={d.priority} fill={COLORS[d.priority]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
