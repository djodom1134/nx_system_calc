/**
 * Server configuration form component
 */

import { useEffect } from 'react'
import { useCalculatorStore } from '../stores/calculatorStore'
import { apiClient } from '../services/api'

export default function ServerForm() {
  const {
    retentionDays,
    setRetentionDays,
    serverConfig,
    setServerConfig,
    raidTypes,
    setRaidTypes,
  } = useCalculatorStore()

  useEffect(() => {
    // Load RAID types
    const loadRaidTypes = async () => {
      try {
        const data = await apiClient.getRaidTypes()
        setRaidTypes(data.raid_types)
      } catch (error) {
        console.error('Failed to load RAID types:', error)
      }
    }
    loadRaidTypes()
  }, [setRaidTypes])

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Server & Storage Configuration</h2>

      <div className="space-y-4">
        <div>
          <label className="label">
            Retention Days <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            className="input-field"
            value={retentionDays}
            onChange={(e) => setRetentionDays(parseInt(e.target.value) || 30)}
            min="1"
            max="365"
          />
          <p className="text-sm text-gray-500 mt-1">
            Number of days to retain recorded video (1-365)
          </p>
        </div>

        <div>
          <label className="label">RAID Type</label>
          <select
            className="input-field"
            value={serverConfig.raid_type}
            onChange={(e) => setServerConfig({ raid_type: e.target.value })}
          >
            {raidTypes.map((raid) => (
              <option key={raid.id} value={raid.id}>
                {raid.name} - {raid.usable_percentage}% usable, {raid.fault_tolerance} drive
                fault tolerance
              </option>
            ))}
          </select>
          <p className="text-sm text-gray-500 mt-1">
            RAID configuration affects usable storage capacity
          </p>
        </div>

        <div>
          <label className="label">Failover Configuration</label>
          <select
            className="input-field"
            value={serverConfig.failover_type}
            onChange={(e) => setServerConfig({ failover_type: e.target.value })}
          >
            <option value="none">None (No Failover)</option>
            <option value="n_plus_1">N+1 (One Backup Server)</option>
            <option value="n_plus_2">N+2 (Two Backup Servers)</option>
          </select>
          <p className="text-sm text-gray-500 mt-1">
            Failover adds redundant servers for high availability
          </p>
        </div>

        <div>
          <label className="label">Network Interface Capacity</label>
          <select
            className="input-field"
            value={serverConfig.nic_capacity_mbps}
            onChange={(e) =>
              setServerConfig({ nic_capacity_mbps: parseInt(e.target.value) })
            }
          >
            <option value="1000">1 GbE (1000 Mbps)</option>
            <option value="10000">10 GbE (10000 Mbps)</option>
            <option value="25000">25 GbE (25000 Mbps)</option>
          </select>
          <p className="text-sm text-gray-500 mt-1">
            Network interface speed per server
          </p>
        </div>

        <div>
          <label className="label">Number of NICs per Server</label>
          <input
            type="number"
            className="input-field"
            value={serverConfig.nic_count}
            onChange={(e) =>
              setServerConfig({ nic_count: parseInt(e.target.value) || 1 })
            }
            min="1"
            max="4"
          />
          <p className="text-sm text-gray-500 mt-1">
            Multiple NICs increase total bandwidth capacity (1-4)
          </p>
        </div>
      </div>
    </div>
  )
}

