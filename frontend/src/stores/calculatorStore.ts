/**
 * Zustand store for calculator state management
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type {
  ProjectDetails,
  CameraConfig,
  ServerConfig,
  CalculationResponse,
  Resolution,
  Codec,
  RaidType
} from '../services/api'

interface BrandingColors {
  primary_color: string
  secondary_color: string
  accent_color: string
}

interface BrandingConfig {
  company_name?: string
  logo_filename?: string
  logo_url?: string
  colors?: BrandingColors
  tagline?: string
  website?: string
}

interface CalculatorState {
  // Project details
  project: ProjectDetails
  setProject: (project: Partial<ProjectDetails>) => void

  // OEM Branding
  branding: BrandingConfig | null
  setBranding: (branding: Partial<BrandingConfig>) => void

  // Camera configuration
  cameraGroups: CameraConfig[]
  addCameraGroup: (group: CameraConfig) => void
  updateCameraGroup: (index: number, group: Partial<CameraConfig>) => void
  removeCameraGroup: (index: number) => void

  // Server configuration
  retentionDays: number
  setRetentionDays: (days: number) => void
  serverConfig: ServerConfig
  setServerConfig: (config: Partial<ServerConfig>) => void

  // Calculation results
  results: CalculationResponse | null
  setResults: (results: CalculationResponse | null) => void

  // Configuration data
  resolutions: Resolution[]
  setResolutions: (resolutions: Resolution[]) => void
  codecs: Codec[]
  setCodecs: (codecs: Codec[]) => void
  raidTypes: RaidType[]
  setRaidTypes: (raidTypes: RaidType[]) => void

  // UI state
  isCalculating: boolean
  setIsCalculating: (isCalculating: boolean) => void
  error: string | null
  setError: (error: string | null) => void

  // Actions
  reset: () => void
}

const defaultCameraGroup: CameraConfig = {
  num_cameras: 100,
  resolution_id: '2mp_1080p',
  fps: 30,
  codec_id: 'h264',
  quality: 'medium',
  recording_mode: 'continuous',
  audio_enabled: false,
}

const defaultServerConfig: ServerConfig = {
  raid_type: 'raid5',
  failover_type: 'none',
  nic_capacity_mbps: 1000,
  nic_count: 1,
}

const defaultProject: ProjectDetails = {
  project_name: '',
  created_by: '',
  creator_email: '',
}

export const useCalculatorStore = create<CalculatorState>()(
  persist(
    (set) => ({
      // Initial state
      project: defaultProject,
      branding: null,
      cameraGroups: [defaultCameraGroup],
      retentionDays: 30,
      serverConfig: defaultServerConfig,
      results: null,
      resolutions: [],
      codecs: [],
      raidTypes: [],
      isCalculating: false,
      error: null,

      // Project actions
      setProject: (project) =>
        set((state) => ({
          project: { ...state.project, ...project },
        })),

      // Branding actions
      setBranding: (branding) =>
        set((state) => ({
          branding: { ...state.branding, ...branding },
        })),

      // Camera group actions
      addCameraGroup: (group) =>
        set((state) => ({
          cameraGroups: [...state.cameraGroups, group],
        })),

      updateCameraGroup: (index, group) =>
        set((state) => ({
          cameraGroups: state.cameraGroups.map((g, i) =>
            i === index ? { ...g, ...group } : g
          ),
        })),

      removeCameraGroup: (index) =>
        set((state) => ({
          cameraGroups: state.cameraGroups.filter((_, i) => i !== index),
        })),

      // Server configuration actions
      setRetentionDays: (days) => set({ retentionDays: days }),

      setServerConfig: (config) =>
        set((state) => ({
          serverConfig: { ...state.serverConfig, ...config },
        })),

      // Results actions
      setResults: (results) => set({ results }),

      // Configuration data actions
      setResolutions: (resolutions) => set({ resolutions }),
      setCodecs: (codecs) => set({ codecs }),
      setRaidTypes: (raidTypes) => set({ raidTypes }),

      // UI state actions
      setIsCalculating: (isCalculating) => set({ isCalculating }),
      setError: (error) => set({ error }),

      // Reset action
      reset: () =>
        set({
          project: defaultProject,
          cameraGroups: [defaultCameraGroup],
          retentionDays: 30,
          serverConfig: defaultServerConfig,
          results: null,
          error: null,
        }),
    }),
    {
      name: 'nx-calculator-storage',
      partialize: (state) => ({
        project: state.project,
        cameraGroups: state.cameraGroups,
        retentionDays: state.retentionDays,
        serverConfig: state.serverConfig,
      }),
    }
  )
)

