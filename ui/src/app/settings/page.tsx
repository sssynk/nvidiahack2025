"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Moon, Sun, ArrowLeft } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [asrMode, setAsrMode] = useState<"free" | "fast">("free");
  const [llmProvider, setLlmProvider] = useState<"nvidia" | "groq" | "openai">("nvidia");
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check if dark mode is active on mount
    setIsDark(document.documentElement.classList.contains('dark'));
  }, []);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/settings`);
        const data = await res.json();
        const mode = (data?.settings?.asr_mode as string | undefined)?.toLowerCase() || "free";
        setAsrMode(mode === "fast" ? "fast" : "free");
        const prov = (data?.settings?.llm_provider as string | undefined)?.toLowerCase() || "nvidia";
        if (prov === "openai") {
          setLlmProvider("openai");
        } else if (prov === "groq") {
          setLlmProvider("groq");
        } else {
          setLlmProvider("nvidia");
        }
      } catch {
        // keep default
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const toggleTheme = () => {
    const html = document.documentElement;
    if (html.classList.contains('dark')) {
      html.classList.remove('dark');
      setIsDark(false);
      localStorage.setItem('theme', 'light');
    } else {
      html.classList.add('dark');
      setIsDark(true);
      localStorage.setItem('theme', 'dark');
    }
  };

  async function save() {
    setSaving(true);
    try {
      const form = new FormData();
      form.append("asr_mode", asrMode);
      form.append("llm_provider", llmProvider);
      const res = await fetch(`${API_BASE}/api/settings`, { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
    } catch {
      // no-op UI for now
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-4">
      <div className="mb-4 flex items-center justify-between">
        <a href="/classnotes">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
          </Button>
        </a>
        <Button 
          variant="outline" 
          size="icon" 
          onClick={toggleTheme}
          title={isDark ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>Configure your transcription and AI options.</CardDescription>
        </CardHeader>
        <Separator />
        <CardContent className="space-y-6 pt-4">
          <div>
            <div className="mb-2 font-medium">ASR mode</div>
            <RadioGroup value={asrMode} onValueChange={(v) => setAsrMode((v as "free" | "fast") || "free")}
              className="grid gap-2">
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="asr-free" value="free" />
                <Label htmlFor="asr-free">Free (slow) — NVIDIA Riva (lower quality and slower)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="asr-fast" value="fast" />
                <Label htmlFor="asr-fast">Fast (paid) — Groq Whisper (higher quality and faster)</Label>
              </div>
            </RadioGroup>
            <div className="mt-2 text-xs text-muted-foreground">
              Fast mode uses Groq Whisper and requires GROQ_API_KEY env configured server-side.
            </div>
          </div>

          <div>
            <div className="mb-2 font-medium">LLM provider</div>
            <RadioGroup value={llmProvider} onValueChange={(v) => setLlmProvider((v as "nvidia" | "groq" | "openai") || "nvidia")}
              className="grid gap-2">
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="llm-nvidia" value="nvidia" />
                <Label htmlFor="llm-nvidia">NVIDIA — Nemotron (free tier)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="llm-openai" value="openai" />
                <Label htmlFor="llm-openai">OpenAI — GPT-4o/GPT-4o-mini</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="llm-groq" value="groq" />
                <Label htmlFor="llm-groq">Groq — openai/gpt-oss-20b</Label>
              </div>
            </RadioGroup>
            <div className="mt-2 text-xs text-muted-foreground">
              OpenAI requires OPENAI_API_KEY env. Groq requires GROQ_API_KEY env. Configure server-side.
            </div>
          </div>

          <div className="flex items-center justify-end gap-2">
            <Button onClick={save} disabled={saving || loading}>Save</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


