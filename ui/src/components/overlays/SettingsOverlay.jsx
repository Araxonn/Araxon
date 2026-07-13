import React, { useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../ui/dialog'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Slider } from '../ui/slider'
import { Switch } from '../ui/switch'

const SettingsOverlay = () => {
  const { settingsOpen, setSettingsOpen, addNotification } = useAppStore()
  const { sendSettings } = useWebSocket()

  const [settings, setSettings] = useState({
    whisper_model: 'base',
    tts_voice: 'af',
    tts_speed: 1.0,
    mic_enabled: true,
    preferred_backend: 'groq',
    groq_api_key: '',
    ollama_url: '',
    temperature: 0.7,
    max_tokens: 2000,
    wake_word: 'araxon',
    auto_sleep_timeout: 300,
    clap_detection: true,
    wake_confirmation_phrase: '',
    agent_mode: 'auto',
    max_steps: 10,
    narrate_steps: true,
    step_delay: 1,
    theme: 'dark',
    font_size: 'medium',
    notifications_enabled: true,
    auto_scroll: true,
  })

  const handleSaveSettings = () => {
    sendSettings(settings)
    addNotification({
      id: Math.random(),
      type: 'success',
      title: 'Settings Saved',
      message: 'All settings have been updated',
    })
    setSettingsOpen(false)
  }

  const updateSetting = (key, value) => {
    setSettings({ ...settings, [key]: value })
  }

  return (
    <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
      <DialogContent className="max-w-md max-h-96 overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>Configure Araxon behavior and features</DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="Voice" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="Voice" className="text-xs">Voice</TabsTrigger>
            <TabsTrigger value="AI" className="text-xs">AI</TabsTrigger>
            <TabsTrigger value="Wake" className="text-xs">Wake</TabsTrigger>
            <TabsTrigger value="Agent" className="text-xs">Agent</TabsTrigger>
            <TabsTrigger value="UI" className="text-xs">UI</TabsTrigger>
          </TabsList>

          {/* Voice Tab */}
          <TabsContent value="Voice" className="space-y-4 mt-4">
            <div>
              <Label className="text-xs">Whisper Model</Label>
              <Select value={settings.whisper_model} onValueChange={(v) => updateSetting('whisper_model', v)}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tiny">Tiny</SelectItem>
                  <SelectItem value="base">Base</SelectItem>
                  <SelectItem value="small">Small</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">TTS Voice</Label>
              <Select value={settings.tts_voice} onValueChange={(v) => updateSetting('tts_voice', v)}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="af">AF (Female)</SelectItem>
                  <SelectItem value="am">AM (Male)</SelectItem>
                  <SelectItem value="bf">BF (Female)</SelectItem>
                  <SelectItem value="bm">BM (Male)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs flex items-center justify-between mb-2">
                TTS Speed: <span className="text-arx-cyan">{settings.tts_speed.toFixed(1)}x</span>
              </Label>
              <Slider
                value={[settings.tts_speed]}
                onValueChange={(v) => updateSetting('tts_speed', v[0])}
                min={0.5}
                max={2}
                step={0.1}
              />
            </div>
          </TabsContent>

          {/* AI Tab */}
          <TabsContent value="AI" className="space-y-4 mt-4">
            <div>
              <Label className="text-xs">Backend</Label>
              <Select value={settings.preferred_backend} onValueChange={(v) => updateSetting('preferred_backend', v)}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="groq">Groq</SelectItem>
                  <SelectItem value="ollama">Ollama</SelectItem>
                  <SelectItem value="auto">Auto</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">Groq API Key</Label>
              <Input
                type="password"
                value={settings.groq_api_key}
                onChange={(e) => updateSetting('groq_api_key', e.target.value)}
                className="h-8 text-xs"
              />
            </div>
            <div>
              <Label className="text-xs flex items-center justify-between mb-2">
                Temperature: <span className="text-arx-cyan">{settings.temperature.toFixed(2)}</span>
              </Label>
              <Slider
                value={[settings.temperature]}
                onValueChange={(v) => updateSetting('temperature', v[0])}
                min={0}
                max={1}
                step={0.1}
              />
            </div>
          </TabsContent>

          {/* Wake Tab */}
          <TabsContent value="Wake" className="space-y-4 mt-4">
            <div>
              <Label className="text-xs">Wake Word</Label>
              <Input
                value={settings.wake_word}
                onChange={(e) => updateSetting('wake_word', e.target.value)}
                className="h-8 text-xs"
              />
            </div>
            <div>
              <Label className="text-xs flex items-center justify-between">
                Clap Detection
                <Switch
                  checked={settings.clap_detection}
                  onCheckedChange={(v) => updateSetting('clap_detection', v)}
                />
              </Label>
            </div>
          </TabsContent>

          {/* Agent Tab */}
          <TabsContent value="Agent" className="space-y-4 mt-4">
            <div>
              <Label className="text-xs">Agent Mode</Label>
              <Select value={settings.agent_mode} onValueChange={(v) => updateSetting('agent_mode', v)}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="graph">Graph</SelectItem>
                  <SelectItem value="plan">Plan</SelectItem>
                  <SelectItem value="auto">Auto</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs flex items-center justify-between">
                Narrate Steps
                <Switch
                  checked={settings.narrate_steps}
                  onCheckedChange={(v) => updateSetting('narrate_steps', v)}
                />
              </Label>
            </div>
          </TabsContent>

          {/* UI Tab */}
          <TabsContent value="UI" className="space-y-4 mt-4">
            <div>
              <Label className="text-xs">Font Size</Label>
              <Select value={settings.font_size} onValueChange={(v) => updateSetting('font_size', v)}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="small">Small</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="large">Large</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs flex items-center justify-between">
                Notifications
                <Switch
                  checked={settings.notifications_enabled}
                  onCheckedChange={(v) => updateSetting('notifications_enabled', v)}
                />
              </Label>
            </div>
            <div>
              <Label className="text-xs flex items-center justify-between">
                Auto Scroll
                <Switch
                  checked={settings.auto_scroll}
                  onCheckedChange={(v) => updateSetting('auto_scroll', v)}
                />
              </Label>
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => setSettingsOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSaveSettings}>
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default SettingsOverlay
