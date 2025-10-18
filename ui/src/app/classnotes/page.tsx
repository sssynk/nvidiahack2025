"use client";

import React from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { marked } from "marked";
import katex from "katex";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  UploadCloud,
  FileText,
  Sparkles,
  Loader2,
  MessageSquare,
  PlayCircle,
  Settings,
  Plus,
} from "lucide-react";

// API base
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

// ---------------------------------------------
// Types & Demo Data
// ---------------------------------------------

type Stage = "onboarding" | "upload" | "processing" | "dashboard";

type TranscriptChunk = {
  ts: string; // timestamp
  text: string;
};

type Session = {
  id: string;
  title: string;
  date: string; // ISO or human
  summary: {
    keyPoints: string[];
    actionItems: string[];
    vocab?: string[];
  };
  transcript: TranscriptChunk[];
};

type ClassInfo = {
  id: string;
  name: string;
  code: string;
  instructor: string;
  lastUpdated: string;
  color: string; // Tailwind color class for accent dot
  sessions: Session[];
  sessionsCount?: number;
};

const demoClasses: ClassInfo[] = [
  {
    id: "demo",
    name: "Sample Class",
    code: "DEMO 101",
    instructor: "Demo Instructor",
    lastUpdated: "Today",
    color: "bg-emerald-500",
    sessions: [
      {
        id: "demo-s1",
        title: "Demo Session",
        date: new Date().toLocaleDateString(),
        summary: { keyPoints: [], actionItems: [], vocab: [] },
        transcript: [
          { ts: "00:00", text: "Welcome to the demo transcript." },
          { ts: "00:05", text: "Once you upload, real data will appear." },
        ],
      },
    ],
  },
];

// ---------------------------------------------
// Helpers
// ---------------------------------------------

function classNames(...arr: Array<string | undefined | false>) {
  return arr.filter(Boolean).join(" ");
}

function getSelectedClass(classes: ClassInfo[], id: string | null) {
  if (!id) return classes[0];
  return classes.find((c) => c.id === id) ?? classes[0];
}

// Map server classes metadata to UI structure (sessions loaded separately)
function mapServerClassesToUI(list: unknown[]): ClassInfo[] {
  return (list || []).map((item, idx) => {
    const c = item as Record<string, unknown>;
    const lastSessionAt = c.last_session_at as string | undefined;
    const updatedAt = c.updated_at as string | undefined;
    const last = lastSessionAt ? new Date(lastSessionAt).toLocaleDateString() : (updatedAt ? new Date(updatedAt).toLocaleDateString() : "");
    return {
      id: c.class_id as string,
      name: (c.name || c.code || c.class_id) as string,
      code: (c.code || c.class_id) as string,
      instructor: "",
      lastUpdated: last || "",
      color: (c.color as string) || (idx % 3 === 0 ? "bg-emerald-500" : idx % 3 === 1 ? "bg-blue-500" : "bg-amber-500"),
      sessions: [],
      sessionsCount: Number(c.sessions_count || 0),
    } as ClassInfo;
  });
}

function preprocessMath(md: string): string {
  let out = md;
  // Convert [ ... ] that likely contain LaTeX into \[ ... \]
  out = out.replace(/\[([\s\S]+?)\](?!\()/g, (m, inner) => {
    // Only treat as math if it contains a LaTeX command (e.g., \int, \frac, \sum, \text, \left)
    if (/\\(int|iint|sum|frac|lim|text|left|right|cdot|nabla|partial)/.test(inner)) {
      return `\\[${inner}\\]`;
    }
    return m;
  });
  // Convert ( ... ) that likely contain LaTeX into \( ... \)
  out = out.replace(/\(([^)]*\\[a-zA-Z][^)]*)\)/g, (m, inner) => {
    return `\\(${inner}\\)`;
  });
  return out;
}

function renderMarkdownWithMath(md: string): string {
  const pre = preprocessMath(md);
  const html = marked(pre) as string;
  // Replace inline math \( ... \)
  const inlineProcessed = html.replace(/\\\((.+?)\\\)/g, (_, expr) => {
    try {
      return katex.renderToString(expr, { throwOnError: false });
    } catch {
      return expr;
    }
  });
  // Replace block math \[ ... \]
  const blockProcessed = inlineProcessed.replace(/\\\[([\s\S]+?)\\\]/g, (_, expr) => {
    try {
      return `<div class=\"katex-display\">${katex.renderToString(expr, { displayMode: true, throwOnError: false })}</div>`;
    } catch {
      return expr;
    }
  });
  return blockProcessed;
}

// ---------------------------------------------
// Main Component
// ---------------------------------------------

export default function ClassNotesDemo() {
  const router = useRouter();
  const initialClassFromQuery: string | null = null;
  const [stage, setStage] = useState<Stage>("upload");
  const [progress, setProgress] = useState(0);
  const [uploadName, setUploadName] = useState<string | null>(null);
  const [uploadClassId, setUploadClassId] = useState<string | null>(null);
  const [uploadSessionTitle, setUploadSessionTitle] = useState<string>("");

  // API state
  const [classesUI, setClassesUI] = useState<ClassInfo[]>(demoClasses);
  const [selectedClassId, setSelectedClassId] = useState<string | null>(initialClassFromQuery || (demoClasses[0]?.id ?? null));
  const [selectedClassInfo, setSelectedClassInfo] = useState<Record<string, unknown> | null>(null);

  const selectedClass = useMemo(() => getSelectedClass(classesUI, selectedClassId), [classesUI, selectedClassId]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  // When server class info arrives or changes, set default selected session
  useEffect(() => {
    const sessions = (selectedClassInfo?.sessions as Array<{ session_id: string }>) || [];
    if (!sessions.length) {
      setSelectedSessionId(null);
      return;
    }
    if (!selectedSessionId || !sessions.find((s) => s.session_id === selectedSessionId)) {
      setSelectedSessionId(sessions[0].session_id);
    }
  }, [selectedClassInfo, selectedSessionId]);

  // Load classes from API
  async function refreshClasses(selectId?: string): Promise<string | null> {
    try {
      const res = await fetch(`${API_BASE}/api/classes`);
      const data = await res.json() as { classes?: unknown[] };
      if (data && data.classes) {
        const mapped = mapServerClassesToUI(data.classes);
        if (!mapped.length) {
          setClassesUI([]);
          setSelectedClassId(null);
          setStage("onboarding");
          return null;
        } else {
          setClassesUI(mapped);
          const firstId = selectId || (mapped[0]?.id ?? null);
          if (firstId) setSelectedClassId(firstId);
          setStage("dashboard");
          return firstId || null;
        }
      }
    } catch {
      // keep demo
      return null;
    }
    return null;
  }

  // Load single class detail
  async function loadClassInfo(classId: string) {
    try {
      const res = await fetch(`${API_BASE}/api/class/${encodeURIComponent(classId)}`);
      const data = await res.json() as { class?: Record<string, unknown> };
      if (data && data.class) setSelectedClassInfo(data.class);
    } catch {
      setSelectedClassInfo(null);
    }
  }

  useEffect(() => {
    (async () => {
      const urlParam = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('classId') : null;
      const id = await refreshClasses(urlParam || undefined);
      if (urlParam) {
        setSelectedClassId(urlParam);
        await loadClassInfo(urlParam);
      } else if (id) {
        await loadClassInfo(id);
      }
    })();
  }, []);

  useEffect(() => {
    if (selectedClassId) {
      // push classId to query param without full page reload
      const params = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '');
      params.set("classId", selectedClassId);
      router.replace(`?${params.toString()}`);
      loadClassInfo(selectedClassId);
    }
  }, [selectedClassId, router]);

  // Upload handler
  async function handleUpload(file: File) {
    setUploadName(file?.name || null);
    setStage("processing");
    setProgress(0);

    const form = new FormData();
    form.append("file", file);
    form.append("language_code", "en-US");
    const cid = uploadClassId || selectedClassId || classesUI[0]?.id || "";
    if (!cid) {
      setStage("onboarding");
      return;
    }
    form.append("class_id", cid);
    if (uploadSessionTitle.trim()) form.append("session_title", uploadSessionTitle.trim());

    try {
      const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      // Refresh and select new class and session
      const classId = data.class_id as string;
      const newSessionId = (data.session_id as string) || null;
      await refreshClasses(classId);
      setSelectedClassId(classId);
      await loadClassInfo(classId);
      if (newSessionId) setSelectedSessionId(newSessionId);
      setStage("dashboard");
    } catch (err) {
      console.error(err);
      setStage("upload");
    }
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-background to-muted/40">
      <TopNav
        onReset={() => {
          setStage("upload");
          setProgress(0);
          setUploadName(null);
        }}
        onGoDashboard={() => {
          setStage("dashboard");
          if (selectedClassId) void loadClassInfo(selectedClassId);
        }}
      />

      <main className="mx-auto max-w-[1400px] px-4 pb-10 pt-6">
        <AnimatePresence mode="popLayout">
          {stage === "onboarding" && (
            <motion.div
              key="onboarding"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.25 }}
            >
              <OnboardingScreen
                onCreated={async () => {
                  await refreshClasses();
                  setStage("upload");
                }}
              />
            </motion.div>
          )}

          {stage === "upload" && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.25 }}
            >
              <UploadScreen
                classes={classesUI}
                selectedClassId={uploadClassId || selectedClassId}
                onSelectClass={setUploadClassId}
                sessionTitle={uploadSessionTitle}
                onSessionTitle={setUploadSessionTitle}
                onUpload={(file) => {
                  if (file) handleUpload(file);
                }}
                onCreateClass={() => setStage("onboarding")}
              />
            </motion.div>
          )}

          {stage === "processing" && (
            <motion.div
              key="processing"
              initial={{ opacity: 0, x: 60 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -60 }}
              transition={{ duration: 0.35 }}
            >
              <ProcessingScreen fileName={uploadName ?? "lecture.mp4"} progress={progress} />
            </motion.div>
          )}

          {stage === "dashboard" && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 28 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -28 }}
              transition={{ duration: 0.35 }}
              className="grid grid-cols-1 gap-4 lg:grid-cols-[280px_1fr_380px]"
            >
              <Sidebar
                classes={classesUI}
                selectedId={selectedClassId}
                onSelect={setSelectedClassId}
                onNewUpload={() => setStage("upload")}
                onAddClass={() => setStage("onboarding")}
              />

              <ClassDetail
                classInfo={selectedClass}
                serverClass={selectedClassInfo}
                selectedSessionId={selectedSessionId}
                onSelectSession={setSelectedSessionId}
                onUploadEmpty={() => {
                  setUploadClassId(selectedClassId);
                  setStage("upload");
                }}
                onUploadForClass={() => {
                  setUploadClassId(selectedClassId);
                  setStage("upload");
                }}
              />

              <ChatbotPanel classInfo={selectedClass} classId={selectedClassId} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

// ---------------------------------------------
// Top Navigation
// ---------------------------------------------

function TopNav({ onReset, onGoDashboard }: { onReset: () => void; onGoDashboard: () => void }) {
  return (
    <div className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between px-4 py-3">
        <button className="flex items-center gap-2" onClick={onGoDashboard} title="Go to dashboard">
          <Image src="/nvidialogo.png" alt="NVIDIA" width={120} height={24} priority />
        </button>
        <div className="flex items-center gap-2">
          <a href="/settings" className="hidden sm:inline-flex">
            <Button variant="outline" size="sm">
              <Settings className="mr-2 h-4 w-4" /> Settings
            </Button>
          </a>
          <Button variant="outline" size="sm" onClick={onGoDashboard}>
            Dashboard
          </Button>
          <Button size="sm" className="bg-black text-white hover:bg-black/90" onClick={onReset}>
            <Plus className="mr-2 h-4 w-4" /> New upload
          </Button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------
// Upload Screen
// ---------------------------------------------

function UploadScreen({
  classes,
  selectedClassId,
  onSelectClass,
  sessionTitle,
  onSessionTitle,
  onUpload,
  onCreateClass,
}: {
  classes: ClassInfo[];
  selectedClassId: string | null | undefined;
  onSelectClass: (id: string | null) => void;
  sessionTitle: string;
  onSessionTitle: (t: string) => void;
  onUpload: (file: File | null) => void;
  onCreateClass: () => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  return (
    <div className="mx-auto grid max-w-4xl gap-6">

      <Card className="overflow-hidden border-2 border-dashed">
        <CardContent className="p-0">
          <div
            className="relative grid place-items-center p-10 sm:p-14"
            onClick={() => inputRef.current?.click()}
          >
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
            <div className="flex max-w-xl flex-col items-center text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
                <UploadCloud className="h-7 w-7 text-primary" />
              </div>
              <div className="text-lg font-medium">Drop a video here, or click to browse</div>
              <p className="mt-1 text-sm text-muted-foreground">.mp4, .mov up to 2 GB</p>
              <div className="mt-6 grid w-full gap-3 text-left">
                <div className="flex items-center gap-3">
                  <label className="w-[120px] text-sm text-muted-foreground">Class</label>
                  <select
                    className="h-9 flex-1 rounded-md border bg-background px-3 text-sm"
                    value={selectedClassId || ''}
                    onChange={(e) => onSelectClass(e.target.value || null)}
                  >
                    <option value="">Select a class…</option>
                    {classes.map((c) => (
                      <option key={c.id} value={c.id}>{c.code} — {c.name}</option>
                    ))}
                  </select>
                  <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); onCreateClass(); }}>+ New class</Button>
                </div>
                <div className="flex items-center gap-3">
                  <label className="w-[120px] text-sm text-muted-foreground">Session title</label>
                  <Input
                    placeholder="e.g. Week 3 - Linear Regression"
                    value={sessionTitle}
                    onChange={(e) => onSessionTitle(e.target.value)}
                  />
                </div>
              </div>
              <div className="mt-6 flex items-center gap-3">
                <Button onClick={() => inputRef.current?.click()}>
                  <PlayCircle className="mr-2 h-4 w-4" /> Choose a video
                </Button>
              </div>
              <input
                ref={inputRef}
                type="file"
                accept="video/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0] || null;
                  onUpload(file);
                }}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ---------------------------------------------
// Onboarding Screen (Create Classes)
// ---------------------------------------------

function OnboardingScreen({ onCreated }: { onCreated: () => void }) {
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [color, setColor] = useState("bg-emerald-500");
  const [saving, setSaving] = useState(false);

  async function createClass() {
    const form = new FormData();
    form.append("name", name || code || "Untitled Class");
    if (code) form.append("code", code);
    form.append("color", color);
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/api/classes`, { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      onCreated();
    } catch {
      // no-op
    } finally {
      setSaving(false);
    }
  }

  const colors = [
    "bg-emerald-500",
    "bg-blue-500",
    "bg-amber-500",
    "bg-purple-500",
    "bg-rose-500",
  ];

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Welcome! Let’s set up your classes</CardTitle>
          <CardDescription>You need at least one class before uploading lectures.</CardDescription>
        </CardHeader>
        <Separator />
        <CardContent className="space-y-4 pt-4">
          <div className="flex items-center gap-3">
            <label className="w-[140px] text-sm text-muted-foreground">Class name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. CS 229 - Machine Learning" />
          </div>
          <div className="flex items-center gap-3">
            <label className="w-[140px] text-sm text-muted-foreground">Code (optional)</label>
            <Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="e.g. CS229" />
          </div>
          <div className="flex items-center gap-3">
            <label className="w-[140px] text-sm text-muted-foreground">Color</label>
            <div className="flex items-center gap-2">
              {colors.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className={`h-6 w-6 rounded-full ${c} ring-2 ${color === c ? 'ring-foreground' : 'ring-transparent'}`}
                  title={c}
                />
              ))}
            </div>
          </div>
        </CardContent>
        <Separator />
        <div className="flex items-center justify-end gap-2 p-4">
          <Button onClick={createClass} disabled={saving || (!name && !code)}>
            <Plus className="mr-2 h-4 w-4" /> Create class
          </Button>
        </div>
      </Card>
    </div>
  );
}

// ---------------------------------------------
// Processing Screen
// ---------------------------------------------

function ProcessingScreen({ fileName, progress }: { fileName: string; progress: number }) {
  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-primary" /> Processing your upload
          </CardTitle>
          <CardDescription>{fileName}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              We’re extracting audio, sending to ASR, and generating an AI summary.
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Do not close this page.
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ---------------------------------------------
// Sidebar (Classes List)
// ---------------------------------------------

function Sidebar({
  classes,
  selectedId,
  onSelect,
  onNewUpload,
  onAddClass,
}: {
  classes: ClassInfo[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onNewUpload: () => void;
  onAddClass: () => void;
}) {
  return (
    <Card className="h-[72vh] lg:h-[78vh]">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-base">
          <span className="flex items-center gap-2"><FileText className="h-4 w-4" /> Classes</span>
          <div className="flex items-center gap-1">
            <Button size="icon" variant="ghost" onClick={onNewUpload} title="New Upload">
              <UploadCloud className="h-4 w-4" />
            </Button>
            <Button size="icon" variant="ghost" onClick={onAddClass} title="Add Class">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <Separator />
      <ScrollArea className="h-[calc(72vh-5rem)] lg:h-[calc(78vh-5rem)]">
        <div className="p-2">
          {classes.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelect(c.id)}
              className={classNames(
                "w-full rounded-xl p-3 text-left transition",
                selectedId === c.id ? "bg-primary/10 ring-1 ring-primary/30" : "hover:bg-muted"
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={classNames("h-2 w-2 rounded-full", c.color)} />
                  <div className="font-medium">{c.code}</div>
                </div>
                <Badge variant={selectedId === c.id ? "default" : "secondary"}>{(c.sessionsCount ?? c.sessions.length) || 0} session{((c.sessionsCount ?? c.sessions.length) || 0) !== 1 ? 's' : ''}</Badge>
              </div>
              <div className="mt-1 text-sm text-muted-foreground">{c.name}</div>
              <div className="mt-1 text-xs text-muted-foreground">Updated {c.lastUpdated}</div>
            </button>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
}

// ---------------------------------------------
// Class Detail (Summary + Transcript)
// ---------------------------------------------

interface SessionData {
  session_id: string;
  title: string;
  created_at: string;
  content: string;
  summary?: string;
  insights?: {
    most_important?: string;
    small_details?: string;
    action_items?: string;
    questions?: string;
  } | null;
}

function ClassDetail({
  classInfo,
  serverClass,
  selectedSessionId,
  onSelectSession,
  onUploadEmpty,
  onUploadForClass,
}: {
  classInfo: ClassInfo;
  serverClass: Record<string, unknown> | null;
  selectedSessionId: string | null;
  onSelectSession: (id: string) => void;
  onUploadEmpty: () => void;
  onUploadForClass: () => void;
}) {
  const sessions = useMemo(() => {
    return (serverClass?.sessions as SessionData[]) || [];
  }, [serverClass?.sessions]);
  
  const session = useMemo(() => {
    if (!sessions.length) return null;
    if (!selectedSessionId) return sessions[0];
    return sessions.find((s) => s.session_id === selectedSessionId) ?? sessions[0];
  }, [sessions, selectedSessionId]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <CardTitle className="text-xl">{classInfo.code} • {classInfo.name}</CardTitle>
              {session && (
                <CardDescription>
                  {session.title} — <span className="text-foreground/80">{new Date(session.created_at).toLocaleString()}</span>
                </CardDescription>
              )}
            </div>
            <div className="flex items-center gap-2">
              {sessions.length > 0 ? (
                <select
                  className="h-9 rounded-md border bg-background px-3 text-sm"
                  value={session?.session_id || ''}
                  onChange={(e) => onSelectSession(e.target.value)}
                >
                  {sessions.map((s) => (
                    <option key={s.session_id} value={s.session_id}>
                      {new Date(s.created_at).toLocaleDateString()} • {s.title}
                    </option>
                  ))}
                </select>
              ) : null}
              <Button variant="ghost" size="sm" onClick={onUploadForClass} title="Upload new lecture">
                <UploadCloud className="mr-2 h-4 w-4" /> Upload new lecture
              </Button>
            </div>
          </div>
        </CardHeader>
        <Separator />
        <CardContent>
          {!sessions.length ? (
              <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">No lectures yet for this class.</div>
              <Button onClick={onUploadEmpty}><UploadCloud className="mr-2 h-4 w-4" /> Upload a lecture</Button>
            </div>
          ) : (
          <>
            {session?.insights && (session.insights.most_important || session.insights.small_details || session.insights.action_items || session.insights.questions) ? (
              <div className="mb-4 overflow-x-auto">
                <div className="flex gap-3 pr-6">
                  {session.insights.most_important ? (
                    <div className="min-w-[260px] flex-1 rounded-xl border bg-muted/40 p-3">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium"><Sparkles className="h-4 w-4 text-primary" /> Most important</div>
                      <div className="prose prose-sm max-w-none [&_ul]:list-disc [&_ul]:pl-4" dangerouslySetInnerHTML={{ __html: renderMarkdownWithMath(session.insights.most_important) }} />
                    </div>
                  ) : null}
                  {session.insights.small_details ? (
                    <div className="min-w-[260px] flex-1 rounded-xl border bg-muted/40 p-3">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium"><FileText className="h-4 w-4 text-amber-500" /> Small details</div>
                      <div className="prose prose-sm max-w-none [&_ul]:list-disc [&_ul]:pl-4" dangerouslySetInnerHTML={{ __html: renderMarkdownWithMath(session.insights.small_details) }} />
                    </div>
                  ) : null}
                  {session.insights.action_items ? (
                    <div className="min-w-[260px] flex-1 rounded-xl border bg-muted/40 p-3">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium"><Settings className="h-4 w-4 text-emerald-600" /> Action items</div>
                      <div className="prose prose-sm max-w-none [&_ul]:list-disc [&_ul]:pl-4" dangerouslySetInnerHTML={{ __html: renderMarkdownWithMath(session.insights.action_items) }} />
                    </div>
                  ) : null}
                  {session.insights.questions ? (
                    <div className="min-w-[260px] flex-1 rounded-xl border bg-muted/40 p-3">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium"><MessageSquare className="h-4 w-4 text-blue-600" /> Questions to ask</div>
                      <div className="prose prose-sm max-w-none whitespace-pre-wrap">{session.insights.questions}</div>
                    </div>
                  ) : null}
                </div>
              </div>
            ) : null}

            <Tabs defaultValue="summary" className="w-full">
            <TabsList>
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="transcript">Transcript</TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="mt-4">
              {session?.summary ? (
                <div 
                  className="text-sm leading-relaxed [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:my-3 [&_li]:my-1 [&_p]:my-3 [&_strong]:font-semibold" 
                  dangerouslySetInnerHTML={{ __html: renderMarkdownWithMath(session.summary) }} 
                />
              ) : (
                <div className="text-sm text-muted-foreground">No summary yet for this session.</div>
              )}
            </TabsContent>

            <TabsContent value="transcript" className="mt-4">
              <ScrollArea className="h-[48vh]">
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{session?.content || ''}</div>
              </ScrollArea>
            </TabsContent>
            </Tabs>
          </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ---------------------------------------------
// Chatbot Panel (wired to API)
// ---------------------------------------------

function ChatbotPanel({ classInfo, classId }: { classInfo: ClassInfo; classId: string | null }) {
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  // Clear messages when class changes
  useEffect(() => {
    setMessages([]);
  }, [classId]);

  async function sendMessage() {
    if (!classId || !input.trim() || sending) return;
    const question = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }, { role: "assistant", text: "" }]);
    setSending(true);

    try {
      const form = new FormData();
      form.append("question", question);
      const res = await fetch(`${API_BASE}/api/chat/${encodeURIComponent(classId)}`, { method: "POST", body: form });
      if (!res.ok || !res.body) {
        const err = await res.text();
        throw new Error(err);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let started = false;
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        // strip wrapper {"ok": true, "answer": " ... "}
        if (!started) {
          const idx = buffer.indexOf('"answer": "');
          if (idx >= 0) {
            buffer = buffer.slice(idx + '"answer": "'.length);
            started = true;
          } else {
            continue;
          }
        }
        // remove trailing '"}' if present and clean up escaped characters
        let clean = buffer.replace(/"}\s*$/, "");
        // Unescape JSON escaped characters
        clean = clean.replace(/\\n/g, '\n').replace(/\\"/g, '"').replace(/\\\\/g, '\\');
        setMessages((m) => {
          const copy = m.slice();
          copy[copy.length - 1] = { role: "assistant", text: clean };
          return copy;
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${errorMessage}` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <Card className="flex h-[72vh] flex-col lg:h-[78vh]">
      <CardHeader className="flex-shrink-0 pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <MessageSquare className="h-4 w-4" /> Ask your notes
        </CardTitle>
        <CardDescription>
          Connected to <span className="font-medium">{classInfo.code}</span>
        </CardDescription>
      </CardHeader>
      <Separator />
      <CardContent className="flex min-h-0 flex-1 flex-col gap-3 pt-4">
        <div className="flex-1 min-h-0 overflow-y-auto rounded-lg border p-3">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground/50">
              Chatting with {classInfo.code}
            </div>
          ) : (
            <div className="space-y-4 pr-4">
              {messages.map((m, i) => (
                <div key={i} className={classNames("flex gap-3", m.role === "user" ? "justify-end" : "justify-start")}>
                  {m.role === "assistant" && (
                    <Avatar className="h-6 w-6 flex-shrink-0 self-start">
                      <AvatarFallback>AI</AvatarFallback>
                    </Avatar>
                  )}
                  <div
                    className={classNames(
                      "max-w-[80%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap break-words",
                      m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                    )}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex-shrink-0 rounded-lg border bg-muted/40 p-3">
          <div className="text-xs text-muted-foreground">
            Ask about the transcript. Responses stream in real time.
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Input
              placeholder={classId ? "Ask about the transcript…" : "Select a class first"}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!classId || sending}
              onKeyDown={(e) => {
                if (e.key === "Enter") sendMessage();
              }}
            />
            <Button onClick={sendMessage} disabled={!classId || sending}>Send</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
