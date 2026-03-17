"use client";

import { TasksSection } from "@/components/TasksSection";
import { TimelineSection } from "@/components/TimelineSection";
import { RecognitionSection } from "@/components/RecognitionSection";
import { EventsSection } from "@/components/EventsSection";
import { MeetingSchedulerSection } from "@/components/MeetingSchedulerSection";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DashboardPage() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/50 sticky top-0 z-10 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-xl font-semibold text-amber-400">Nyala Labs</h1>
          <p className="text-sm text-slate-400">Team Dashboard</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <TasksSection apiBase={API_BASE} />
          </div>
          <div>
            <RecognitionSection apiBase={API_BASE} />
            <EventsSection apiBase={API_BASE} className="mt-8" />
          </div>
        </div>

        <TimelineSection apiBase={API_BASE} />
        <MeetingSchedulerSection apiBase={API_BASE} />
      </div>
    </main>
  );
}
