/**
 * Results display component
 */

import { useCalculatorStore } from '../stores/calculatorStore'
import { useState } from 'react'

export default function Results() {
  const { results, project, cameraGroups, retentionDays, serverConfig } = useCalculatorStore()
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false)

  const handleDownloadPdf = async () => {
    try {
      setIsGeneratingPdf(true)

      // Prepare the request data
      const requestData = {
        project: {
          project_name: project.project_name,
          created_by: project.created_by,
          creator_email: project.creator_email,
        },
        camera_groups: cameraGroups.map(group => ({
          num_cameras: group.num_cameras,
          resolution_id: group.resolution_id,
          fps: group.fps,
          codec_id: group.codec_id,
          quality: group.quality,
          recording_mode: group.recording_mode,
          audio_enabled: group.audio_enabled,
          bitrate_kbps: group.bitrate_kbps,
        })),
        retention_days: retentionDays,
        server_config: {
          raid_type: serverConfig.raid_type,
          failover_type: serverConfig.failover_type,
          nic_capacity_mbps: serverConfig.nic_capacity_mbps,
          nic_count: serverConfig.nic_count,
        },
      }

      // Call the API to generate PDF
      const response = await fetch('/api/v1/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      })

      if (!response.ok) {
        throw new Error('Failed to generate PDF')
      }

      // Create a download link
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${project.project_name.replace(/\s+/g, '_')}_VMS_Report.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error generating PDF:', error)
      alert('Failed to generate PDF report. Please try again.')
    } finally {
      setIsGeneratingPdf(false)
    }
  }

  if (!results) {
    return (
      <div className="card">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Results</h2>
        <div className="text-center py-12 text-gray-500">
          <svg
            className="mx-auto h-12 w-12 text-gray-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
          <p className="text-lg">Configure your project and click Calculate</p>
          <p className="text-sm mt-2">Results will appear here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Download PDF Button */}
      <div className="flex justify-end">
        <button
          onClick={handleDownloadPdf}
          disabled={isGeneratingPdf}
          className="btn-primary flex items-center gap-2"
          aria-label="Download PDF Report"
        >
          {isGeneratingPdf ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating PDF...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download PDF Report
            </>
          )}
        </button>
      </div>

      {/* Summary Card */}
      <div className="rounded-lg shadow-md p-4 sm:p-6 lg:p-8" style={{ backgroundColor: '#1D252D' }}>
        <h2 className="text-2xl font-bold mb-6 text-white">System Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
            <p className="text-sm text-gray-300 mb-1">Total Devices</p>
            <p className="text-3xl font-bold" style={{ color: '#407EC9' }}>
              {results.summary.total_devices}
            </p>
          </div>
          <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
            <p className="text-sm text-gray-300 mb-1">Servers Needed</p>
            <p className="text-3xl font-bold" style={{ color: '#407EC9' }}>
              {results.summary.servers_needed}
            </p>
            {results.summary.servers_with_failover > results.summary.servers_needed && (
              <p className="text-xs text-gray-400 mt-1">
                +{results.summary.servers_with_failover - results.summary.servers_needed}{' '}
                failover
              </p>
            )}
          </div>
          <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
            <p className="text-sm text-gray-300 mb-1">Total Storage</p>
            <p className="text-3xl font-bold" style={{ color: '#407EC9' }}>
              {results.summary.total_storage_tb.toFixed(2)} TB
            </p>
          </div>
          <div className="rounded-lg p-4" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
            <p className="text-sm text-gray-300 mb-1">Total Bandwidth</p>
            <p className="text-3xl font-bold" style={{ color: '#407EC9' }}>
              {results.summary.total_bitrate_mbps.toFixed(0)} Mbps
            </p>
          </div>
        </div>
      </div>

      {/* Storage Details */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 text-gray-900">Storage Requirements</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Usable Storage Needed:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.storage.total_storage_tb.toFixed(2)} TB
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Raw Storage (with RAID):</span>
            <span className="font-semibold text-lg text-gray-900">
              {(results.storage.raw_storage_needed_gb / 1024).toFixed(2)} TB
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">RAID Overhead:</span>
            <span className="font-semibold text-lg text-red-700">
              {(results.storage.raid_overhead_gb / 1024).toFixed(2)} TB
            </span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-900">Daily Storage:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.storage.daily_storage_gb.toFixed(2)} GB/day
            </span>
          </div>
        </div>
      </div>

      {/* Server Configuration */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 text-gray-900">Server Configuration</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Servers Required:</span>
            <span className="font-semibold text-lg text-gray-900">{results.servers.servers_needed}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">With Failover:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.servers.servers_with_failover}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Devices per Server:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.servers.devices_per_server}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Bitrate per Server:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.servers.bitrate_per_server_mbps.toFixed(2)} Mbps
            </span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-900">Limiting Factor:</span>
            <span className="font-semibold text-lg capitalize text-gray-900">
              {results.servers.limiting_factor.replace('_', ' ')}
            </span>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold mb-2" style={{ color: '#407EC9' }}>Recommended Server Tier</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-900">Tier:</span>
              <span className="ml-2 font-medium text-gray-900 capitalize">
                {results.servers.recommended_tier.tier}
              </span>
            </div>
            <div>
              <span className="text-gray-900">CPU:</span>
              <span className="ml-2 font-medium text-gray-900">{results.servers.recommended_tier.cpu}</span>
            </div>
            <div>
              <span className="text-gray-900">RAM:</span>
              <span className="ml-2 font-medium text-gray-900">
                {results.servers.recommended_tier.ram_gb} GB
              </span>
            </div>
            <div>
              <span className="text-gray-900">Storage:</span>
              <span className="ml-2 font-medium text-gray-900">
                {results.servers.recommended_tier.storage_type}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Network Bandwidth */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 text-gray-900">Network Bandwidth</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Total Bitrate:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.bandwidth.total_bitrate_mbps.toFixed(2)} Mbps (
              {results.bandwidth.total_bitrate_gbps.toFixed(2)} Gbps)
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Per Server:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.bandwidth.per_server_mbps.toFixed(2)} Mbps
            </span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-900">NIC Utilization:</span>
            <span
              className={`font-semibold text-lg ${
                results.bandwidth.nic_utilization_percentage > 80
                  ? 'text-red-700'
                  : results.bandwidth.nic_utilization_percentage > 60
                  ? 'text-yellow-700'
                  : 'text-green-700'
              }`}
            >
              {results.bandwidth.nic_utilization_percentage.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Licenses */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 text-gray-900">License Requirements</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-900">Professional Licenses:</span>
            <span className="font-semibold text-lg text-gray-900">
              {results.licenses.professional_licenses}
            </span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-900">Total Licenses:</span>
            <span className="font-semibold text-lg text-gray-900">{results.licenses.total_licenses}</span>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {results.warnings.length > 0 && (
        <div className="card bg-yellow-50 border-l-4 border-yellow-400">
          <h3 className="text-lg font-bold mb-3 text-yellow-900">⚠️ Warnings</h3>
          <ul className="list-disc list-inside space-y-1 text-yellow-900">
            {results.warnings.map((warning, idx) => (
              <li key={idx}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Errors */}
      {results.errors.length > 0 && (
        <div className="card bg-red-50 border-l-4 border-red-400">
          <h3 className="text-lg font-bold mb-3 text-red-900">❌ Errors</h3>
          <ul className="list-disc list-inside space-y-1 text-red-900">
            {results.errors.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

