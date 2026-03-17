"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { CheckCircle2, Circle, Loader2, Plus } from "lucide-react";

interface Task {
  id: number;
  team_id: number;
  assignee_id: number | null;
  title: string;
  description: string | null;
  status: string;
  progress: number;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

interface User {
  id: number;
  name: string;
  email: string;
  team_id: number;
}

export function TasksSection({ apiBase }: { apiBase: string }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [teams, setTeams] = useState<{ id: number; name: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterTeam, setFilterTeam] = useState<number | "">("");
  const [newTitle, setNewTitle] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch(`${apiBase}/api/tasks`).then((r) => r.json()),
      fetch(`${apiBase}/api/users`).then((r) => r.json()),
      fetch(`${apiBase}/api/teams`).then((r) => r.json()),
    ])
      .then(([t, u, te]) => {
        setTasks(t);
        setUsers(u);
        setTeams(te);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [apiBase]);

  const filtered = filterTeam ? tasks.filter((t) => t.team_id === filterTeam) : tasks;
  const getUser = (id: number | null) => users.find((u) => u.id === id)?.name ?? "—";

  const updateProgress = async (task: Task, progress: number) => {
    await fetch(`${apiBase}/api/tasks/${task.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ progress, status: progress >= 100 ? "DONE" : "IN_PROGRESS" }),
    });
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, progress, status: progress >= 100 ? "DONE" : "IN_PROGRESS" } : t))
    );
  };

  const createTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !filterTeam) return;
    const res = await fetch(`${apiBase}/api/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: newTitle.trim(),
        team_id: filterTeam,
        status: "TODO",
        progress: 0,
      }),
    });
    const created = await res.json();
    setTasks((prev) => [created, ...prev]);
    setNewTitle("");
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-6 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-amber-400" />
      </div>
    );
  }

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-800/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Tasks</h2>
        <div className="flex gap-2">
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
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-1 bg-amber-500 text-black px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-amber-400"
          >
            <Plus className="w-4 h-4" /> Add task
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={createTask} className="px-6 py-3 bg-slate-700/30 flex gap-2">
          <input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Task title"
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
          />
          <select
            value={filterTeam}
            onChange={(e) => setFilterTeam(e.target.value === "" ? "" : Number(e.target.value))}
            required
            className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
          >
            <option value="">Select team</option>
            {teams.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
          <button type="submit" className="bg-amber-500 text-black px-4 py-2 rounded-lg font-medium">
            Create
          </button>
        </form>
      )}

      <ul className="divide-y divide-slate-700 max-h-[400px] overflow-y-auto">
        {filtered.map((task) => (
          <li key={task.id} className="px-6 py-3 hover:bg-slate-700/30 flex items-center gap-4">
            <button
              onClick={() => updateProgress(task, task.status === "DONE" ? 0 : 100)}
              className="text-slate-400 hover:text-amber-400"
            >
              {task.status === "DONE" ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              ) : (
                <Circle className="w-5 h-5" />
              )}
            </button>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">{task.title}</p>
              <p className="text-slate-400 text-sm">
                {getUser(task.assignee_id)} • {task.due_date ? format(new Date(task.due_date), "MMM d") : "No due date"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min="0"
                max="100"
                value={task.progress}
                onChange={(e) => updateProgress(task, Number(e.target.value))}
                className="w-24 accent-amber-500"
              />
              <span className="text-slate-400 text-sm w-8">{task.progress}%</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
