"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { isSupabaseConfigured, supabase } from "@/lib/supabaseClient";

type ColumnKey = "backlog" | "in_progress" | "done";

type Idea = {
  id: string;
  board_id: string;
  column: ColumnKey;
  title: string;
  detail: string | null;
  created_at: string;
  updated_at: string | null;
};

const columns: Array<{ key: ColumnKey; label: string; helper: string }> = [
  {
    key: "backlog",
    label: "Backlog",
    helper: "Capture raw ideas without judgment.",
  },
  {
    key: "in_progress",
    label: "In Progress",
    helper: "Focus on the ideas that matter most.",
  },
  {
    key: "done",
    label: "Done",
    helper: "Ship and document outcomes.",
  },
];

const generateBoardId = () =>
  Math.random().toString(36).replace(/[^a-z0-9]/g, "").slice(0, 6);

const boardStorageKey = "ideaboard.boardId";

function IdeaBoardPage() {
  const [boardId, setBoardId] = useState(() => {
    if (typeof window === "undefined") return "";
    const stored = localStorage.getItem(boardStorageKey);
    if (stored) return stored;
    const next = generateBoardId();
    localStorage.setItem(boardStorageKey, next);
    return next;
  });
  const [boardInput, setBoardInput] = useState(() => {
    if (typeof window === "undefined") return "";
    return localStorage.getItem(boardStorageKey) ?? "";
  });
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [realtimeStatus, setRealtimeStatus] = useState("disconnected");
  const [drafts, setDrafts] = useState<Record<ColumnKey, { title: string; detail: string }>>({
    backlog: { title: "", detail: "" },
    in_progress: { title: "", detail: "" },
    done: { title: "", detail: "" },
  });

  const ideasByColumn = useMemo(() => {
    return columns.reduce((acc, column) => {
      acc[column.key] = ideas.filter((idea) => idea.column === column.key);
      return acc;
    }, {} as Record<ColumnKey, Idea[]>);
  }, [ideas]);

  useEffect(() => {
    if (!boardId || !supabase) return;
    const client = supabase;

    const run = async () => {
      setLoading(true);
      const { data, error } = await client
        .from("ideas")
        .select("*")
        .eq("board_id", boardId)
        .order("created_at", { ascending: true });

      if (error) {
        setStatus(error.message);
        setLoading(false);
        return;
      }

      setIdeas((data ?? []) as Idea[]);
      setLoading(false);
    };

    run();

    const channel = client
      .channel(`ideas:${boardId}`)
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "ideas", filter: `board_id=eq.${boardId}` },
        (payload) => {
          if (payload.eventType === "DELETE") {
            const removed = payload.old as Idea;
            setIdeas((prev) => prev.filter((idea) => idea.id !== removed.id));
            return;
          }

          const updated = payload.new as Idea;
          setIdeas((prev) => {
            const exists = prev.some((idea) => idea.id === updated.id);
            if (exists) {
              return prev.map((idea) => (idea.id === updated.id ? updated : idea));
            }
            return [...prev, updated];
          });
        }
      )
      .subscribe((state) => {
        setRealtimeStatus(state);
      });

    return () => {
      client.removeChannel(channel);
    };
  }, [boardId]);

  useEffect(() => {
    if (!boardId) return;
    localStorage.setItem(boardStorageKey, boardId);
  }, [boardId]);

  const handleJoinBoard = () => {
    const cleaned = boardInput.trim().toLowerCase();
    if (!cleaned) {
      setStatus("Enter a board code to join.");
      setTimeout(() => setStatus(null), 2000);
      return;
    }
    if (cleaned === boardId) {
      setStatus("You are already on this board.");
      setTimeout(() => setStatus(null), 2000);
      return;
    }
    setBoardId(cleaned);
    setStatus(`Joined board ${cleaned}.`);
    setTimeout(() => setStatus(null), 2000);
  };

  const handleCreateBoard = () => {
    const next = generateBoardId();
    setBoardId(next);
    setBoardInput(next);
    setStatus("Created a new board.");
    setTimeout(() => setStatus(null), 2000);
  };

  const handleCopyBoard = async () => {
    if (!boardId) return;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(boardId);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = boardId;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      setStatus("Board code copied.");
    } catch {
      setStatus("Copy failed. Select the code and copy manually.");
    }
    setTimeout(() => setStatus(null), 2000);
  };

  const addIdea = async (column: ColumnKey) => {
    if (!supabase || !boardId) {
      setStatus("Supabase is not configured yet. Add your keys to .env.local.");
      setTimeout(() => setStatus(null), 2500);
      return;
    }
    const client = supabase;
    const draft = drafts[column];
    if (!draft.title.trim()) return;

    setStatus("Saving idea...");
    const { data, error } = await client
      .from("ideas")
      .insert({
        board_id: boardId,
        column,
        title: draft.title.trim(),
        detail: draft.detail.trim() || null,
      })
      .select("*")
      .single();

    if (error) {
      setStatus(error.message);
      return;
    }

    if (data) {
      setIdeas((prev) => [...prev, data as Idea]);
    }

    setDrafts((prev) => ({
      ...prev,
      [column]: { title: "", detail: "" },
    }));
    setStatus(null);
  };

  const moveIdea = async (idea: Idea, direction: "left" | "right") => {
    if (!supabase) return;
    const client = supabase;
    const columnIndex = columns.findIndex((col) => col.key === idea.column);
    const nextIndex = direction === "left" ? columnIndex - 1 : columnIndex + 1;
    const nextColumn = columns[nextIndex]?.key;
    if (!nextColumn) return;

    const { error } = await client
      .from("ideas")
      .update({ column: nextColumn })
      .eq("id", idea.id);

    if (error) {
      setStatus(error.message);
    }
  };

  const updateIdea = async (idea: Idea, title: string, detail: string) => {
    if (!supabase) return;
    const client = supabase;
    const { error } = await client
      .from("ideas")
      .update({ title: title.trim(), detail: detail.trim() || null })
      .eq("id", idea.id);

    if (error) {
      setStatus(error.message);
    }
  };

  const deleteIdea = async (idea: Idea) => {
    if (!supabase) return;
    const client = supabase;
    const { error } = await client.from("ideas").delete().eq("id", idea.id);
    if (error) {
      setStatus(error.message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-12">
        <header className="flex flex-col gap-6 rounded-3xl border border-white/10 bg-slate-900/60 p-8 shadow-lg shadow-slate-950/40">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                IdeaBoard
              </p>
              <h1 className="mt-3 text-3xl font-semibold text-white sm:text-4xl">
                Collaborate in real time with a lightweight idea board.
              </h1>
              <p className="mt-3 max-w-2xl text-sm text-slate-300 sm:text-base">
                Share a board code with 2–3 teammates, drop ideas, and pick up where
                you left off.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-right">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Realtime
              </p>
              <p className="mt-1 text-sm font-medium text-emerald-300">
                {isSupabaseConfigured ? realtimeStatus : "not configured"}
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-slate-950/60 p-5">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex-1">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                  Board code
                </p>
                <p className="mt-2 text-lg font-semibold text-white">{boardId || "—"}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleCopyBoard}
                  className="rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:border-white/40"
                >
                  Copy
                </button>
                <button
                  onClick={handleCreateBoard}
                  className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
                >
                  New board
                </button>
              </div>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                value={boardInput}
                onChange={(event) => setBoardInput(event.target.value)}
                placeholder="Enter a board code to join"
                className="flex-1 rounded-xl border border-white/10 bg-slate-950/80 px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-white/40 focus:outline-none"
              />
              <button
                onClick={handleJoinBoard}
                className="rounded-xl border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:border-white/40"
              >
                Join board
              </button>
            </div>
            {status ? (
              <p className="text-xs text-amber-200">{status}</p>
            ) : null}
          </div>
        </header>

        {!isSupabaseConfigured ? (
          <section className="rounded-3xl border border-amber-400/30 bg-amber-500/10 p-6 text-sm text-amber-100">
            <h2 className="text-lg font-semibold text-amber-50">Finish setup</h2>
            <p className="mt-2 text-amber-100">
              Add your Supabase keys in <code className="text-amber-50">.env.local</code> to enable
              realtime collaboration. A sample file is included in the project.
            </p>
          </section>
        ) : null}

        <section className="grid gap-6 lg:grid-cols-3">
          {columns.map((column, columnIndex) => (
            <div
              key={column.key}
              className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-slate-900/50 p-5"
            >
              <div>
                <h3 className="text-lg font-semibold text-white">{column.label}</h3>
                <p className="text-xs text-slate-400">{column.helper}</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <input
                  value={drafts[column.key].title}
                  onChange={(event) =>
                    setDrafts((prev) => ({
                      ...prev,
                      [column.key]: {
                        ...prev[column.key],
                        title: event.target.value,
                      },
                    }))
                  }
                  placeholder="Idea title"
                  className="w-full rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:border-white/40 focus:outline-none"
                />
                <textarea
                  value={drafts[column.key].detail}
                  onChange={(event) =>
                    setDrafts((prev) => ({
                      ...prev,
                      [column.key]: {
                        ...prev[column.key],
                        detail: event.target.value,
                      },
                    }))
                  }
                  placeholder="Optional details"
                  rows={3}
                  className="mt-3 w-full resize-none rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:border-white/40 focus:outline-none"
                />
                <button
                  onClick={() => addIdea(column.key)}
                  disabled={!isSupabaseConfigured}
                  className="mt-3 w-full rounded-xl bg-emerald-400/90 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
                >
                  Add idea
                </button>
              </div>

              <div className="flex flex-1 flex-col gap-3">
                {loading ? (
                  <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-400">
                    Loading ideas...
                  </div>
                ) : null}
                {ideasByColumn[column.key]?.length ? (
                  ideasByColumn[column.key].map((idea) => (
                    <IdeaCard
                      key={idea.id}
                      idea={idea}
                      columnIndex={columnIndex}
                      onMove={moveIdea}
                      onUpdate={updateIdea}
                      onDelete={deleteIdea}
                    />
                  ))
                ) : !loading ? (
                  <div className="rounded-2xl border border-dashed border-white/10 bg-slate-950/40 p-4 text-xs text-slate-500">
                    No ideas here yet.
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}

const Home = dynamic(() => Promise.resolve(IdeaBoardPage), { ssr: false });

export default Home;

function IdeaCard({
  idea,
  columnIndex,
  onMove,
  onUpdate,
  onDelete,
}: {
  idea: Idea;
  columnIndex: number;
  onMove: (idea: Idea, direction: "left" | "right") => void;
  onUpdate: (idea: Idea, title: string, detail: string) => void;
  onDelete: (idea: Idea) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(idea.title);
  const [detail, setDetail] = useState(idea.detail ?? "");

  const startEditing = () => {
    setTitle(idea.title);
    setDetail(idea.detail ?? "");
    setEditing(true);
  };

  const handleSave = async () => {
    await onUpdate(idea, title, detail);
    setEditing(false);
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 shadow-sm shadow-slate-950/30">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          {editing ? (
            <>
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                className="w-full rounded-lg border border-white/10 bg-slate-950/80 px-2 py-1 text-sm text-white focus:border-white/40 focus:outline-none"
              />
              <textarea
                value={detail}
                onChange={(event) => setDetail(event.target.value)}
                rows={3}
                className="mt-2 w-full resize-none rounded-lg border border-white/10 bg-slate-950/80 px-2 py-1 text-xs text-white focus:border-white/40 focus:outline-none"
              />
            </>
          ) : (
            <>
              <p className="text-sm font-semibold text-white">{idea.title}</p>
              {idea.detail ? (
                <p className="mt-2 text-xs text-slate-300">{idea.detail}</p>
              ) : null}
            </>
          )}
        </div>
        <div className="flex flex-col gap-2">
          <button
            onClick={() => onMove(idea, "left")}
            disabled={columnIndex === 0}
            className="rounded-full border border-white/10 px-2 py-1 text-xs text-white/80 transition hover:border-white/40 disabled:cursor-not-allowed disabled:opacity-40"
          >
            ←
          </button>
          <button
            onClick={() => onMove(idea, "right")}
            disabled={columnIndex === columns.length - 1}
            className="rounded-full border border-white/10 px-2 py-1 text-xs text-white/80 transition hover:border-white/40 disabled:cursor-not-allowed disabled:opacity-40"
          >
            →
          </button>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {editing ? (
          <button
            onClick={handleSave}
            className="rounded-full bg-emerald-300/90 px-3 py-1 text-xs font-semibold text-slate-900"
          >
            Save
          </button>
        ) : (
          <button
            onClick={startEditing}
            className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/80"
          >
            Edit
          </button>
        )}
        {editing ? (
          <button
            onClick={() => setEditing(false)}
            className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/60"
          >
            Cancel
          </button>
        ) : null}
        <button
          onClick={() => onDelete(idea)}
          className="rounded-full border border-red-400/40 px-3 py-1 text-xs text-red-200"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
