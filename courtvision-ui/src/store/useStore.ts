import { create } from 'zustand'
import { GameEvent, Player, PlayerStats } from '../data/mock'

export type TabType = 'video' | 'team' | 'reports'
export type UploadStatus = 'idle' | 'uploading' | 'processing' | 'done' | 'error'

export type TeamStats = {
    ball_acquisition_pct: number
    passes: number
    interceptions: number
}

export type PlayerExertion = {
    team: number
    distance_ft: number
}

export type ApiStats = {
    team_1: TeamStats
    team_2: TeamStats
    players?: Record<string, PlayerExertion>
}

interface StoreState {
    // App state
    processingComplete: boolean
    setProcessingComplete: (complete: boolean) => void
    currentTab: TabType
    setCurrentTab: (tab: TabType) => void

    // Upload / processing state
    uploadStatus: UploadStatus
    setUploadStatus: (status: UploadStatus) => void
    uploadError: string | null
    setUploadError: (error: string | null) => void

    // API results
    outputVideoUrl: string | null
    setOutputVideoUrl: (url: string | null) => void
    tacticalVideoUrl: string | null
    setTacticalVideoUrl: (url: string | null) => void
    apiStats: ApiStats | null
    setApiStats: (stats: ApiStats | null) => void

    // Data state
    events: GameEvent[]
    setEvents: (events: GameEvent[]) => void
    players: Player[]
    setPlayers: (players: Player[]) => void
    playerStats: PlayerStats[]

    // Selection state
    selectedPlayerId: string | null
    setSelectedPlayerId: (id: string | null) => void

    // Video state
    seekTime: number | null
    setSeekTime: (time: number | null) => void
}

export const useStore = create<StoreState>((set) => ({
    processingComplete: false,
    setProcessingComplete: (complete) => set({ processingComplete: complete }),

    currentTab: 'video',
    setCurrentTab: (tab) => set({ currentTab: tab }),

    uploadStatus: 'idle',
    setUploadStatus: (status) => set({ uploadStatus: status }),
    uploadError: null,
    setUploadError: (error) => set({ uploadError: error }),

    outputVideoUrl: null,
    setOutputVideoUrl: (url) => set({ outputVideoUrl: url }),
    tacticalVideoUrl: null,
    setTacticalVideoUrl: (url) => set({ tacticalVideoUrl: url }),
    apiStats: null,
    setApiStats: (stats) => set({ apiStats: stats }),

    events: [] as GameEvent[],
    setEvents: (events) => set({ events }),
    players: [] as Player[],
    setPlayers: (players) => set({ players }),
    playerStats: [] as PlayerStats[],

    selectedPlayerId: null,
    setSelectedPlayerId: (id) => set({ selectedPlayerId: id }),

    seekTime: null,
    setSeekTime: (time) => set({ seekTime: time }),
}))
