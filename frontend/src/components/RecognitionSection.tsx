"use client";

import { useEffect, useState } from "react";
import { Award } from "lucide-react";

interface Score {
  id: number;
  user_id: number;
  team_id: number;
  points: number;
  period_start: string;
  period_end: string;
}

interface User {
  id: number;
  name: string;
  email: string;
  team_id: number;
}

export function RecognitionSection({ apiBase }: { apiBase: string }) {
  const [scores, setScores] = useState<Score[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterTeam, setFilterTeam] = useState<number | "">("");
  const [teams, setTeams] = useState<{ id: number; name: string }[]>([]);

  useEffect(() => {
    Promise.all([
      fetch(`${apiBase}/api/recognition`).then((r) => r.json()),
      fetch(`${apiBase}/api/users`).then((r) => r.json()),
      fetch(`${apiBase}/api/teams`).then((r) => r.json()),
    ])
      .then(([s, u, t]) => {
        setScores(s);
        setUsers(u);
        setTeams(t);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [apiBase]);

  const getUser = (id: number) => users.find((u) => u.id === id)?.name ?? `User ${id}`;
  const filtered = filterTeam ? scores.filter((s) => s.team_id === filterTeam) : scores;
  const byUser = filtered.reduce<Record<number, number>>((acc, s) => {
    acc[s.user_id] = (acc[s.user_id] ?? 0) + s.points;
    return acc;
  }, {});
  const ranked = Object.entries(byUser)
    .map(([userId, pts]) => ({ userId: Number(userId), points: pts }))
    .sort((a, b) => b.points - a.points)
    .slice(0, 5);

  if (loading) {
    return (
      <section className="rounded-xl border border-slate-700 bg-slate-800/50 p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Recognition</h2>
        <div className="text-slate-400">Loading...</div>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-800/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-400" /> Recognition
        </h2>
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
      <div className="p-6">
        <p className="text-slate-400 text-xs mb-4">
          Automated & fair: +5 task completed, +1 progress update, +1 meeting vote
        </p>
        <ul className="space-y-2">
          {ranked.map((r, i) => (
            <li key={r.userId} className="flex items-center justify-between py-2">
              <span className="text-white">
                <span className="text-amber-400 font-mono w-6 inline-block">{i + 1}.</span> {getUser(r.userId)}
              </span>
              <span className="text-amber-400 font-semibold">{r.points} pts</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
