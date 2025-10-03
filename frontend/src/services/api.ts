/**
 * API client for Nx System Calculator
 */

export interface ProjectDetails {
  project_name: string
  created_by: string
  creator_email: string
  receiver_email?: string
  description?: string
  company_name?: string
}

export interface CameraConfig {
  num_cameras: number
  resolution_id?: string
  resolution_area?: number
  fps: number
  codec_id: string
  quality: string
  recording_mode: string
  hours_per_day?: number
  audio_enabled: boolean
  bitrate_kbps?: number
}

export interface ServerConfig {
  raid_type: string
  failover_type: string
  nic_capacity_mbps: number
  nic_count: number
}

export interface CalculationRequest {
  project: ProjectDetails
  camera_groups: CameraConfig[]
  retention_days: number
  server_config: ServerConfig
}

export interface CalculationResponse {
  project: ProjectDetails
  summary: {
    total_devices: number
    total_storage_tb: number
    servers_needed: number
    servers_with_failover: number
    total_bitrate_mbps: number
  }
  bitrate: {
    bitrate_kbps: number
    bitrate_mbps: number
    video_bitrate_kbps: number
    audio_bitrate_kbps: number
  }
  storage: {
    total_storage_gb: number
    total_storage_tb: number
    daily_storage_gb: number
    raw_storage_needed_gb: number
    usable_storage_gb: number
    raid_overhead_gb: number
  }
  servers: {
    servers_needed: number
    servers_with_failover: number
    devices_per_server: number
    bitrate_per_server_mbps: number
    limiting_factor: string
    recommended_tier: {
      tier: string
      cpu: string
      ram_gb: number
      storage_type: string
      nic_config: string
    }
  }
  bandwidth: {
    total_bitrate_mbps: number
    total_bitrate_gbps: number
    per_server_mbps: number
    nic_utilization_percentage: number
  }
  licenses: {
    professional_licenses: number
    total_licenses: number
    licensing_model: string
  }
  warnings: string[]
  errors: string[]
}

export interface Resolution {
  id: string
  name: string
  label: string
  width: number
  height: number
  area: number
  category: string
}

export interface Codec {
  id: string
  name: string
  compression_factor: number
  quality_multipliers: {
    low: number
    medium: number
    high: number
    best: number
  }
}

export interface RaidType {
  id: string
  name: string
  usable_percentage: number
  min_drives: number
  fault_tolerance: number
}

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  async calculate(request: CalculationRequest): Promise<CalculationResponse> {
    return this.request<CalculationResponse>('/calculate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getResolutions(): Promise<{ resolutions: Resolution[] }> {
    return this.request<{ resolutions: Resolution[] }>('/config/resolutions')
  }

  async getCodecs(): Promise<{ codecs: Codec[] }> {
    return this.request<{ codecs: Codec[] }>('/config/codecs')
  }

  async getRaidTypes(): Promise<{ raid_types: RaidType[] }> {
    return this.request<{ raid_types: RaidType[] }>('/config/raid-types')
  }

  async getServerSpecs(): Promise<any> {
    return this.request<any>('/config/server-specs')
  }
}

export const apiClient = new ApiClient()

