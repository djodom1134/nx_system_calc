# Core Mathematics and Calculations Summary

## Camera Calculations

### Bitrate Calculation
**Primary Formula**: `Camera.prototype.bitrateOne()`
- **H.264/H.265 Codecs**:
  ```
  result = brandFactor × qualityFactor × frameRateFactor × resolutionFactor × codecRatio
  resolutionFactor = 0.009 × (resolution.area)^0.7
  ```
- **Other Codecs**:
  ```
  result = (resolution.area / 6666) × frameRateFactor × qualityFactor × (codecRatio + 1/3) × 12
  ```
- **Quality Factor**: `lowEnd + (hiEnd - lowEnd) × qualityRatio` where lowEnd=0.1, hiEnd=1
- **Final Result**: `result / 1024` (converted to proper units)

### Storage Calculation
**Daily Storage per Camera**:
```
avgStoragePerDayTB = bitrateOne() × (60 × 60 × 24) / (8 × 1024 × 1024) × (hours/24) × motionValue()
```

### Camera Statistics
- **Total Bitrate**: `bitrate × count`
- **Total Storage**: `storagePerDayTBAll × days`
- **Max Camera Bitrate**: `bitrateOne() × (1 + lowMotionQuality/100)`

## Server Calculations

### CPU Requirements
**Camera Limit Check**: Based on `Presets.Server.cpuVariants[cpu].maxCameras`

### Memory (RAM) Requirements
**Formula**:
```
requiredRAM = ramOS + (hostClient ? clientRam : 0) + cameras × cameraRam
```
- **Per Camera**: 40MB RAM requirement
- **Desktop Client**: Additional 3072MB
- **Memory Sizing**: Rounded to next power of 2, max 64GB

### Storage Requirements
**Space Calculation**:
```
storageSpace = Math.ceil(space_in_GB / 1024)  // Convert to TB
```

**Storage Count**:
```
storageCount = Math.ceil(bitrate / (1024 × 204))
```

### Network Interface Requirements
**NIC Count**:
```
networkCount = Math.ceil(bitrate / (1024 × nicBitrate))
requiredNICs = Math.ceil((maxBitrate + clientBitrate) / nicBitrate)
```

## System Statistics Aggregation

### Global Statistics (`Stats` constructor)
- **Average Bitrate**: Sum of all camera bitrates × motion values
- **Max Bitrate**: Sum of all maximum camera bitrates
- **Average Daily Storage**: Sum of all camera daily storage
- **Total Storage**: Sum of all camera total storage

### Failover Calculations
**Failover Estimation**:
```javascript
while (checkRAM() && checkCPU() && checkNIC() && checkHDDCount()) {
    stats.maxBitrate += globalstats.maxCameraBitrate;
    stats.cameras++;
    currentMaxCameras++;
}
failoverEstimate = Math.max(currentMaxCameras - 1, camerasCount);
```

## Hardware Presets and Lookup Tables

### CPU Variants
- **ARM**: 12 cameras max, 64 Mbit/s NIC, 128MB RAM OS
- **Atom**: 32 cameras max, 600 Mbit/s NIC, 1024MB RAM OS
- **Core i3**: 256 cameras max, 600 Mbit/s NIC, 1024MB RAM OS
- **Core i5**: 256 cameras max, 600 Mbit/s NIC, 1024MB RAM OS

### Server Form Factors (Custom Presets)
- **NX1**: ARM, 1 SATA, 1 HDD, 2TB storage, 1GB RAM, 64 Mbit/s NIC
- **NX2**: Core i5, 4 SATA, 8GB RAM, 600 Mbit/s NIC
- **NX3**: Core i3, 12 SATA, 8GB RAM, 600 Mbit/s NIC

### System Requirements Constants
- **Camera RAM**: 40MB per camera
- **Client RAM**: 3072MB for desktop client
- **Client Bitrate**: Additional bitrate for client connections

## Validation Logic

### Server Validation Checks
1. **Camera Count**: `cameras <= maxCameras`
2. **RAM**: `ramStorage × 1024 >= requiredRAM`
3. **CPU**: `cameras <= cpuVariants[cpu].maxCameras`
4. **NIC**: `requiredNICs <= nicCount`
5. **HDD Count**: Based on storage requirements
6. **RAID**: Validation against RAID configuration

### System-Level Validation
- **Camera Assignment**: All cameras assigned to servers
- **Redundancy**: Failover capacity calculation
- **Total Capacity**: Aggregate bitrate and storage validation

## Key Mathematical Constants
- **Bitrate Conversion**: Division by 1024 for unit conversion
- **Storage Conversion**: `60 × 60 × 24 / (8 × 1024 × 1024)` for daily storage
- **Resolution Factor**: `0.009 × area^0.7` for H.264/H.265
- **Memory Rounding**: Powers of 2 for RAM sizing
- **Quality Range**: 0.1 to 1.0 quality factor range

## Cost Estimation
- **Server Cost**: `server.cost × server.count`
- **Storage Cost**: `hddCount × hddPrice`
- **Total Cost**: `serverCost + storageCost`