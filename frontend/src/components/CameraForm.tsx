/**
 * Camera configuration form component
 */

import { useEffect } from 'react'
import { useCalculatorStore } from '../stores/calculatorStore'
import { apiClient } from '../services/api'

export default function CameraForm() {
  const {
    cameraGroups,
    updateCameraGroup,
    addCameraGroup,
    removeCameraGroup,
    resolutions,
    setResolutions,
    codecs,
    setCodecs,
  } = useCalculatorStore()

  useEffect(() => {
    // Load configuration data
    const loadConfig = async () => {
      try {
        const [resData, codecData] = await Promise.all([
          apiClient.getResolutions(),
          apiClient.getCodecs(),
        ])
        setResolutions(resData.resolutions)
        setCodecs(codecData.codecs)
      } catch (error) {
        console.error('Failed to load configuration:', error)
      }
    }
    loadConfig()
  }, [setResolutions, setCodecs])

  const handleAddGroup = () => {
    addCameraGroup({
      num_cameras: 50,
      resolution_id: '2mp_1080p',
      fps: 30,
      codec_id: 'h264',
      quality: 'medium',
      recording_mode: 'continuous',
      audio_enabled: false,
    })
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Camera Configuration</h2>
        <button onClick={handleAddGroup} className="btn-secondary text-sm">
          + Add Camera Group
        </button>
      </div>

      <div className="space-y-6">
        {cameraGroups.map((group, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4 relative">
            {cameraGroups.length > 1 && (
              <button
                onClick={() => removeCameraGroup(index)}
                className="absolute top-2 right-2 text-red-500 hover:text-red-700"
                title="Remove camera group"
              >
                ✕
              </button>
            )}

            <h3 className="font-semibold text-lg mb-4 text-gray-700">
              Camera Group {index + 1}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Number of Cameras</label>
                <input
                  type="number"
                  className="input-field"
                  value={group.num_cameras}
                  onChange={(e) =>
                    updateCameraGroup(index, {
                      num_cameras: parseInt(e.target.value) || 0,
                    })
                  }
                  min="1"
                  max="2560"
                />
              </div>

              <div>
                <label className="label">Resolution</label>
                <select
                  className="input-field"
                  value={group.resolution_id || ''}
                  onChange={(e) =>
                    updateCameraGroup(index, { resolution_id: e.target.value })
                  }
                >
                  <option value="">Select resolution...</option>
                  {resolutions.map((res) => (
                    <option key={res.id} value={res.id}>
                      {res.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">FPS (Frames Per Second)</label>
                <input
                  type="number"
                  className="input-field"
                  value={group.fps}
                  onChange={(e) =>
                    updateCameraGroup(index, { fps: parseInt(e.target.value) || 30 })
                  }
                  min="1"
                  max="100"
                />
              </div>

              <div>
                <label className="label">Codec</label>
                <select
                  className="input-field"
                  value={group.codec_id}
                  onChange={(e) =>
                    updateCameraGroup(index, { codec_id: e.target.value })
                  }
                >
                  {codecs.map((codec) => (
                    <option key={codec.id} value={codec.id}>
                      {codec.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Quality</label>
                <select
                  className="input-field"
                  value={group.quality}
                  onChange={(e) =>
                    updateCameraGroup(index, { quality: e.target.value })
                  }
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="best">Best</option>
                </select>
              </div>

              <div>
                <label className="label">Recording Mode</label>
                <select
                  className="input-field"
                  value={group.recording_mode}
                  onChange={(e) =>
                    updateCameraGroup(index, { recording_mode: e.target.value })
                  }
                >
                  <option value="continuous">Continuous</option>
                  <option value="motion">Motion Detection</option>
                  <option value="object">Object Detection</option>
                  <option value="scheduled">Scheduled</option>
                </select>
              </div>

              {group.recording_mode === 'scheduled' && (
                <div>
                  <label className="label">Hours Per Day</label>
                  <input
                    type="number"
                    className="input-field"
                    value={group.hours_per_day || 12}
                    onChange={(e) =>
                      updateCameraGroup(index, {
                        hours_per_day: parseFloat(e.target.value) || 12,
                      })
                    }
                    min="0"
                    max="24"
                    step="0.5"
                  />
                </div>
              )}

              <div className="flex items-center">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={group.audio_enabled}
                    onChange={(e) =>
                      updateCameraGroup(index, { audio_enabled: e.target.checked })
                    }
                  />
                  <span className="text-sm text-gray-700">Enable Audio Recording</span>
                </label>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

