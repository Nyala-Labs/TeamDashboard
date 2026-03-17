"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { Calendar, Target } from "lucide-react";

interface TimelineItem {
  id: string;
  type: string;
  title: string;
  start: string;
  end: string | null;
  team_id: number;
  team_name: string;
  status?: string;
  progress?: number;
}

interface TimelineData {
  teams: Record<number, string>;
  items: TimelineItem[];
}

export function TimelineSection({ apiBase }: { apiBase: string }) {
  const [data, setData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterTeam, setFilterTeam] = useState<number | "">("");

  useEffect(() => {
    const params = new URLSearchParams();
    if (filterTeam) params.set("team_id", String(filterTeam));
    fetch(`${apiBase}/api/timeline?${params}`)
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [apiBase, filterTeam]);

  if (loading || !data) {
    return (
      <section className="rounded-xl border border-slate-700 bg-slate-800/50 p-8">
        <h2 className="text-lg font-semibold text-white mb-4">Timeline</h2>
        <div className="text-slate-400">Loading...</div>
      </section>
    );
  }

  const teams = Object.entries(data.teams).map(([id, name]) => ({ id: Number(id), name }));
  const items = data.items;

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-800/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Timeline</h2>
        <select
          value={filterTeam}
          onChange={(e) => setFilterTeam(e.target.value === "" ? "" : Number(e.target.value))}
          className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white"
        >
          <option value="">All teams</option>
          {teams.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </div>
      <div className="p-6 overflow-x-auto">
        <div className="space-y-3 min-w-[400px]">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center gap-4 p-3 rounded-lg bg-slate-700/30 border border-slate-600/50"
            >
              {item.type === "task" ? (
                <Target className="w-5 h-5 text-amber-400 flex-shrink-0" />
              ) : (
                <Calendar className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium">{item.title}</p>
                <p className="text-slate-400 text-sm">
                  {item.team_name} • {format(new Date(item.start), "MMM d, yyyy HH:mm")}
                </p>
              </div>
              {item.status && (
                <span className="text-xs px-2 py-1 rounded bg-slate-600 text-slate-300">{item.status}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
