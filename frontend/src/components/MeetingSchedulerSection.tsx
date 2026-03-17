"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { Vote, CheckCircle, Loader2 } from "lucide-react";

interface Poll {
  id: number;
  team_id: number;
  title: string;
  week_start: string;
  week_end: string;
  winning_slot_start: string | null;
  is_scheduled: boolean;
  created_at: string;
}

interface SlotWithVotes {
  slot_start: string;
  slot_end: string;
  votes: number;
}

export function MeetingSchedulerSection({ apiBase }: { apiBase: string }) {
  const [polls, setPolls] = useState<Poll[]>([]);
  const [teams, setTeams] = useState<{ id: number; name: string }[]>([]);
  const [selectedPoll, setSelectedPoll] = useState<number | null>(null);
  const [slots, setSlots] = useState<SlotWithVotes[]>([]);
  const [loading, setLoading] = useState(true);
  const [finalizing, setFinalizing] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch(`${apiBase}/api/meetings/polls`).then((r) => r.json()),
      fetch(`${apiBase}/api/teams`).then((r) => r.json()),
    ])
      .then(([p, t]) => {
        setPolls(p);
        setTeams(t);
        if (p.length && !selectedPoll) setSelectedPoll(p[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [apiBase]);

  useEffect(() => {
    if (!selectedPoll) return;
    fetch(`${apiBase}/api/meetings/polls/${selectedPoll}/slots`)
      .then((r) => r.json())
      .then(setSlots)
      .catch(console.error);
  }, [apiBase, selectedPoll]);

  const poll = polls.find((p) => p.id === selectedPoll);
  const getTeam = (id: number) => teams.find((t) => t.id === id)?.name ?? "";

  const finalizePoll = async () => {
    if (!selectedPoll) return;
    setFinalizing(true);
    try {
      await fetch(`${apiBase}/api/meetings/polls/${selectedPoll}/finalize`, { method: "POST" });
      const updated = await fetch(`${apiBase}/api/meetings/polls`).then((r) => r.json());
      setPolls(updated);
      const p = updated.find((x: Poll) => x.id === selectedPoll);
      if (p) setSelectedPoll(p.id);
    } catch (e) {
      console.error(e);
    } finally {
      setFinalizing(false);
    }
  };

  if (loading) {
    return (
      <section className="rounded-xl border border-slate-700 bg-slate-800/50 p-8">
        <h2 className="text-lg font-semibold text-white mb-4">Meeting Scheduler</h2>
        <div className="text-slate-400">Loading...</div>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-800/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Vote className="w-5 h-5 text-amber-400" /> Meeting Scheduler
        </h2>
        <div className="flex gap-2">
          <select
            value={selectedPoll ?? ""}
            onChange={(e) => setSelectedPoll(Number(e.target.value))}
            className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white"
          >
            {polls.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title} ({getTeam(p.team_id)})
              </option>
            ))}
          </select>
          {poll && !poll.is_scheduled && slots.length > 0 && (
            <button
              onClick={finalizePoll}
              disabled={finalizing}
              className="flex items-center gap-1 bg-amber-500 text-black px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-amber-400 disabled:opacity-50"
            >
              {finalizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
              Finalize & schedule
            </button>
          )}
        </div>
      </div>
      <div className="p-6">
        {poll?.is_scheduled && poll.winning_slot_start && (
          <div className="mb-4 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
            <p className="text-emerald-400 font-medium">Meeting scheduled</p>
            <p className="text-white">{format(new Date(poll.winning_slot_start), "EEEE, MMM d, yyyy 'at' HH:mm")}</p>
            <p className="text-slate-400 text-sm">Synced to Google Calendar</p>
          </div>
        )}
        <p className="text-slate-400 text-sm mb-4">
          Vote on 30-min slots. The slot with the highest votes wins (earliest on tie). Finalize to auto-schedule on
          Google Calendar.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 max-h-48 overflow-y-auto">
          {slots.map((s) => (
            <div
              key={s.slot_start}
              className="flex justify-between items-center p-2 rounded-lg bg-slate-700/50 border border-slate-600"
            >
              <span className="text-white text-sm truncate">
                {format(new Date(s.slot_start), "MMM d HH:mm")}
              </span>
              <span className="text-amber-400 font-semibold text-sm">{s.votes}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
