import { create } from 'zustand'

export const useAppStore = create((set, get) => ({
  araxonState: 'listening',
  activeMode: 'Assist Mode',
  activeNav: 'Dashboard',
  activeTab: 'Commands',
  activePanel: 'orb',
  executionProgress: 0,

  transcript: [],
  agentSteps: [],
  waveformLevels: [],

  systemStats: {
    cpu: 0,
    ram: 0,
    gpu: 0,
    net: 0,
    disk: 0,
    battery: 100,
  },
  statsHistory: {
    cpu: [],
    ram: [],
    gpu: [],
    net: [],
    disk: [],
    battery: [],
  },

  systemInfo: {},
  codeFile: {
    name: '',
    content: '',
    language: 'js',
  },
  codeSuggestions: [],
  ingestedFiles: [],
  automationProcesses: [],

  connected: false,
  micEnabled: true,
  voiceEnabled: true,
  isFullscreen: false,
  isMuted: false,

  notifications: [],
  settingsOpen: false,
  memoryPanelOpen: false,
  createRoutineOpen: false,
  commandStreamExpanded: false,

  logsOutput: [],
  memoryStats: {
    total: 0,
    files: 0,
    session_turns: 0,
    recent: [],
  },

  setAraxonState: (state) => set({ araxonState: state }),
  setActiveMode: (mode) => set({ activeMode: mode }),
  setActiveNav: (nav) => set({ activeNav: nav }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setActivePanel: (panel) => set({ activePanel: panel }),
  setExecutionProgress: (progress) => set({ executionProgress: progress }),

  resetLiveData: () =>
    set({
      transcript: [],
      agentSteps: [],
      logsOutput: [],
      codeSuggestions: [],
      codeFile: { name: '', content: '', language: 'js' },
      executionProgress: 0,
    }),

  appendTranscript: (entry) =>
    set((state) => ({
      transcript: [...state.transcript, entry],
    })),

  setAgentSteps: (steps) => set({ agentSteps: steps }),
  updateAgentStep: (stepIndex, updates) =>
    set((state) => {
      const newSteps = [...state.agentSteps]
      while (newSteps.length <= stepIndex) {
        newSteps.push({
          title: `Step ${newSteps.length + 1}`,
          status: 'pending',
          percent: 0,
        })
      }
      newSteps[stepIndex] = { ...newSteps[stepIndex], ...updates }
      return { agentSteps: newSteps }
    }),

  setWaveformLevels: (levels) => set({ waveformLevels: levels }),

  setSystemStats: (stats) => set({ systemStats: stats }),

  appendStatsHistory: (stat, value) =>
    set((state) => ({
      statsHistory: {
        ...state.statsHistory,
        [stat]: [...(state.statsHistory[stat] || []).slice(-19), value],
      },
    })),

  setSystemInfo: (info) => set({ systemInfo: info }),

  setCodeFile: (file) => set({ codeFile: file }),
  appendCodeSuggestion: (suggestion) =>
    set((state) => ({
      codeSuggestions: [...state.codeSuggestions, suggestion],
    })),
  clearCodeSuggestions: () => set({ codeSuggestions: [] }),
  setIngestedFiles: (files) => set({ ingestedFiles: files }),
  setAutomationProcesses: (processes) => set({ automationProcesses: processes }),

  setConnected: (connected) => set({ connected }),
  toggleMic: () =>
    set((state) => ({
      micEnabled: !state.micEnabled,
    })),
  toggleVoice: () =>
    set((state) => ({
      voiceEnabled: !state.voiceEnabled,
    })),
  toggleMute: () =>
    set((state) => ({
      isMuted: !state.isMuted,
    })),
  toggleFullscreen: () =>
    set((state) => ({
      isFullscreen: !state.isFullscreen,
    })),

  addNotification: (notification) =>
    set((state) => {
      const newNotifs = [...state.notifications, notification]
      if (newNotifs.length > 5) {
        newNotifs.shift()
      }
      return { notifications: newNotifs }
    }),
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  setSettingsOpen: (open) => set({ settingsOpen: open }),
  setMemoryPanelOpen: (open) => set({ memoryPanelOpen: open }),
  setCreateRoutineOpen: (open) => set({ createRoutineOpen: open }),
  toggleCommandStream: () =>
    set((state) => ({
      commandStreamExpanded: !state.commandStreamExpanded,
    })),

  appendLogLine: (log) =>
    set((state) => ({
      logsOutput: [...state.logsOutput.slice(-49), log],
    })),
  clearLogs: () => set({ logsOutput: [] }),

  setMemoryStats: (stats) => set({ memoryStats: stats }),
  clearTranscript: () => set({ transcript: [] }),
}))
