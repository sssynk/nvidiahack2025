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
  const [apiKeysAvailable, setApiKeysAvailable] = useState({
    nvidia: false,
    openai: false,
    groq: false,
  });

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
        
        // Get API key availability
        if (data?.api_keys_available) {
          setApiKeysAvailable({
            nvidia: data.api_keys_available.nvidia || false,
            openai: data.api_keys_available.openai || false,
            groq: data.api_keys_available.groq || false,
          });
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
                <RadioGroupItem id="asr-free" value="free" disabled={!apiKeysAvailable.nvidia} />
                <Label 
                  htmlFor="asr-free"
                  className={!apiKeysAvailable.nvidia ? "text-muted-foreground/50" : ""}
                >
                  Free (slow) — NVIDIA Riva
                  {!apiKeysAvailable.nvidia && <span className="ml-2 text-xs text-destructive">⚠️ NVIDIA API key missing</span>}
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="asr-fast" value="fast" disabled={!apiKeysAvailable.groq} />
                <Label 
                  htmlFor="asr-fast"
                  className={!apiKeysAvailable.groq ? "text-muted-foreground/50" : ""}
                >
                  Fast (paid) — Groq Whisper
                  {!apiKeysAvailable.groq && <span className="ml-2 text-xs text-destructive">⚠️ GROQ API key missing</span>}
                </Label>
              </div>
            </RadioGroup>
            <div className="mt-2 text-xs text-muted-foreground">
              ASR is only needed for video/audio transcription. Documents (PDF/DOCX) do not require ASR.
            </div>
          </div>

          <div>
            <div className="mb-2 font-medium">LLM provider</div>
            <RadioGroup value={llmProvider} onValueChange={(v) => setLlmProvider((v as "nvidia" | "groq" | "openai") || "nvidia")}
              className="grid gap-2">
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="llm-nvidia" value="nvidia" disabled={!apiKeysAvailable.nvidia} />
                <Label 
                  htmlFor="llm-nvidia" 
                  className={!apiKeysAvailable.nvidia ? "text-muted-foreground/50" : ""}
                >
                  NVIDIA — Nemotron (free tier)
                  {!apiKeysAvailable.nvidia && <span className="ml-2 text-xs text-destructive">⚠️ API key missing</span>}
                </Label>
              </div>
              <div className="flex flex-col gap-1">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem id="llm-openai" value="openai" disabled={!apiKeysAvailable.openai} />
                  <Label 
                    htmlFor="llm-openai"
                    className={!apiKeysAvailable.openai ? "text-muted-foreground/50" : ""}
                  >
                    OpenAI — GPT-4o/GPT-4o-mini
                    {apiKeysAvailable.openai && <span className="ml-2 text-xs text-green-600">✓ Configured</span>}
                    {!apiKeysAvailable.openai && <span className="ml-2 text-xs text-destructive">⚠️ API key missing</span>}
                  </Label>
                </div>
                {llmProvider === "openai" && apiKeysAvailable.openai && !apiKeysAvailable.nvidia && !apiKeysAvailable.groq && (
                  <div className="ml-6 text-xs text-amber-600">
                    ⚠️ Note: OpenAI only supports documents (PDF/DOCX). Videos require NVIDIA or Groq for transcription.
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem id="llm-groq" value="groq" disabled={!apiKeysAvailable.groq} />
                <Label 
                  htmlFor="llm-groq"
                  className={!apiKeysAvailable.groq ? "text-muted-foreground/50" : ""}
                >
                  Groq — openai/gpt-oss-20b
                  {!apiKeysAvailable.groq && <span className="ml-2 text-xs text-destructive">⚠️ API key missing</span>}
                </Label>
              </div>
            </RadioGroup>
            <div className="mt-2 text-xs text-muted-foreground">
              Set API keys as environment variables on the server to enable providers.
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


