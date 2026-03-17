"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { Calendar } from "lucide-react";

interface Event {
  id: number;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  location: string | null;
  team_id: number | null;
}

export function EventsSection({ apiBase, className = "" }: { apiBase: string; className?: string }) {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${apiBase}/api/events`)
      .then((r) => r.json())
      .then((data) => {
        const sorted = data.sort((a: Event, b: Event) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
        setEvents(sorted.slice(0, 5));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [apiBase]);

  if (loading) {
    return (
      <section className={`rounded-xl border border-slate-700 bg-slate-800/50 p-6 ${className}`}>
        <h2 className="text-lg font-semibold text-white mb-4">Upcoming events</h2>
        <div className="text-slate-400">Loading...</div>
      </section>
    );
  }

  return (
    <section className={`rounded-xl border border-slate-700 bg-slate-800/50 overflow-hidden ${className}`}>
      <div className="px-6 py-4 border-b border-slate-700">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Calendar className="w-5 h-5 text-emerald-400" /> Upcoming events
        </h2>
      </div>
      <ul className="divide-y divide-slate-700">
        {events.map((e) => (
          <li key={e.id} className="px-6 py-3">
            <p className="text-white font-medium">{e.title}</p>
            <p className="text-slate-400 text-sm">
              {format(new Date(e.start_time), "MMM d, HH:mm")} – {format(new Date(e.end_time), "HH:mm")}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
