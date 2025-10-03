# Calculation Alignment Plan

**Date**: 2025-10-03  
**Status**: 🔴 **CRITICAL - NOT STARTED**  
**Priority**: **HIGHEST**

---

## 🎯 Objective

Align ALL calculation formulas, constants, and lookup tables in the Nx System Calculator with the exact specifications documented in `/docs/core_calculations.md`. This ensures mathematical accuracy and consistency with the legacy system.

---

## 📋 Task Overview

**Parent Task**: Update All Calculations to Match core_calculations.md  
**Total Subtasks**: 23  
**Estimated Effort**: 3-5 days  
**Complexity**: High

### Task Categories

1. **Audit Tasks (11)** - Deep analysis to identify deviations
2. **Update Tasks (11)** - Implement exact formulas
3. **Validation Task (1)** - Create comprehensive test suite
4. **Documentation Task (1)** - Document all changes

---

## 🔍 Key Findings from Initial Analysis

### Critical Deviations Identified

#### 1. **Bitrate Calculation** ⚠️ MAJOR DEVIATION
**Current Implementation**:
```python
bitrate = (resolution_area × fps × compression_factor × quality_multiplier) / 1000
```

**Required Implementation** (from core_calculations.md):
```javascript
// For H.264/H.265:
resolutionFactor = 0.009 × (resolution.area)^0.7
result = brandFactor × qualityFactor × frameRateFactor × resolutionFactor × codecRatio
result = result / 1024

// For other codecs:
result = (resolution.area / 6666) × frameRateFactor × qualityFactor × (codecRatio + 1/3) × 12
result = result / 1024
```

**Impact**: Current formula is LINEAR with resolution area, but should use POWER function (area^0.7). This significantly affects bitrate estimates for high-resolution cameras.

#### 2. **Quality Factor** ⚠️ MAJOR DEVIATION
**Current Implementation**:
```json
{
  "low": 0.6,
  "medium": 1.0,
  "high": 1.4,
  "best": 2.0
}
```

**Required Implementation**:
```javascript
qualityFactor = lowEnd + (hiEnd - lowEnd) × qualityRatio
// where lowEnd = 0.1, hiEnd = 1.0
// qualityRatio is 0-1 normalized value
```

**Impact**: Current quality multipliers (0.6-2.0) don't match the required range (0.1-1.0). This affects all bitrate calculations.

#### 3. **Server RAM Calculation** ⚠️ MISSING CONSTANTS
**Current Implementation**: Uses generic RAM calculations

**Required Implementation**:
```javascript
requiredRAM = ramOS + (hostClient ? clientRam : 0) + cameras × cameraRam
// Constants:
// - cameraRam = 40MB per camera
// - clientRam = 3072MB for desktop client
// - ramOS = 128MB (ARM) or 1024MB (Atom/i3/i5)
// - Round to next power of 2, max 64GB
```

**Impact**: RAM estimates may be inaccurate without exact constants.

#### 4. **CPU-Based Camera Limits** ⚠️ MISSING VARIANTS
**Current Implementation**: Generic max 256 devices per server

**Required Implementation**:
```javascript
CPU Variants:
- ARM: 12 cameras max, 64 Mbit/s NIC, 128MB RAM OS
- Atom: 32 cameras max, 600 Mbit/s NIC, 1024MB RAM OS
- Core i3: 256 cameras max, 600 Mbit/s NIC, 1024MB RAM OS
- Core i5: 256 cameras max, 600 Mbit/s NIC, 1024MB RAM OS
```

**Impact**: Cannot accurately model different server tiers (NX1, NX2, NX3).

#### 5. **Max Camera Bitrate** ⚠️ MISSING CALCULATION
**Current Implementation**: Only calculates average bitrate

**Required Implementation**:
```javascript
maxCameraBitrate = bitrateOne() × (1 + lowMotionQuality/100)
// Default lowMotionQuality = 20%
```

**Impact**: NIC capacity planning and failover calculations should use max bitrate, not average.

#### 6. **Storage Throughput Limit** ⚠️ MISSING FORMULA
**Current Implementation**: No storage throughput constraint

**Required Implementation**:
```javascript
storageCount = Math.ceil(bitrate / (1024 × 204))
// 204 Mbit/s = throughput per storage device
```

**Impact**: Server count may be underestimated if storage throughput is the limiting factor.

#### 7. **Failover Logic** ⚠️ SIMPLIFIED
**Current Implementation**: Simple multiplication (servers × failover_factor)

**Required Implementation**:
```javascript
while (checkRAM() && checkCPU() && checkNIC() && checkHDDCount()) {
    stats.maxBitrate += globalstats.maxCameraBitrate;
    stats.cameras++;
    currentMaxCameras++;
}
failoverEstimate = Math.max(currentMaxCameras - 1, camerasCount);
```

**Impact**: Failover capacity may be inaccurate without iterative resource checking.

---

## 📊 Detailed Task Breakdown

### Phase 1: Audit (Days 1-2)

| Task | File(s) | Status | Priority |
|------|---------|--------|----------|
| Audit Bitrate Calculation | `bitrate.py` | 🔴 Not Started | CRITICAL |
| Audit Storage Calculation | `storage.py` | 🔴 Not Started | HIGH |
| Audit Server RAM Calculation | `servers.py` | 🔴 Not Started | HIGH |
| Audit CPU and Camera Limits | `server_specs.json`, `servers.py` | 🔴 Not Started | HIGH |
| Audit Network Interface Calculations | `bandwidth.py` | 🔴 Not Started | MEDIUM |
| Audit Storage Count and HDD Calculations | `servers.py`, `storage.py` | 🔴 Not Started | MEDIUM |
| Audit Failover Calculation Logic | `servers.py` | 🔴 Not Started | HIGH |
| Audit Max Camera Bitrate Calculation | `bitrate.py`, `bandwidth.py` | 🔴 Not Started | HIGH |
| Audit Server Form Factor Presets | `server_specs.json` | 🔴 Not Started | MEDIUM |
| Audit Quality Factor Implementation | `codecs.json`, `bitrate.py` | 🔴 Not Started | CRITICAL |

### Phase 2: Implementation (Days 2-4)

| Task | File(s) | Status | Priority |
|------|---------|--------|----------|
| Update Bitrate Calculation | `bitrate.py` | 🔴 Not Started | CRITICAL |
| Update Storage Calculation | `storage.py` | 🔴 Not Started | HIGH |
| Update Server RAM Calculation | `servers.py` | 🔴 Not Started | HIGH |
| Update CPU Variants and Camera Limits | `server_specs.json`, `servers.py` | 🔴 Not Started | HIGH |
| Update Network Interface Calculations | `bandwidth.py` | 🔴 Not Started | MEDIUM |
| Update Storage Count Calculations | `servers.py` | 🔴 Not Started | MEDIUM |
| Update Failover Calculation Logic | `servers.py` | 🔴 Not Started | HIGH |
| Update Max Camera Bitrate Calculation | `bitrate.py`, `bandwidth.py` | 🔴 Not Started | HIGH |
| Update Server Form Factor Presets | `server_specs.json` | 🔴 Not Started | MEDIUM |
| Update Quality Factor Implementation | `codecs.json`, `bitrate.py` | 🔴 Not Started | CRITICAL |

### Phase 3: Validation (Day 4)

| Task | File(s) | Status | Priority |
|------|---------|--------|----------|
| Create Comprehensive Validation Test Suite | `test_core_calculations_validation.py` | 🔴 Not Started | CRITICAL |
| Update Existing Tests to Match New Formulas | `test_bitrate.py`, `test_storage.py`, `test_api.py` | 🔴 Not Started | HIGH |

### Phase 4: Documentation (Day 5)

| Task | File(s) | Status | Priority |
|------|---------|--------|----------|
| Document All Formula Changes | `003-calculation-formula-alignment.md`, `IMPLEMENTATION_STATUS.md`, `README.md` | 🔴 Not Started | HIGH |

---

## 🔧 Files to Modify

### Backend Calculation Modules (6 files)
- ✏️ `backend/app/services/calculations/bitrate.py` - Major changes
- ✏️ `backend/app/services/calculations/storage.py` - Minor changes
- ✏️ `backend/app/services/calculations/servers.py` - Major changes
- ✏️ `backend/app/services/calculations/bandwidth.py` - Medium changes
- ✏️ `backend/app/services/calculations/raid.py` - No changes expected
- ✏️ `backend/app/services/calculations/licenses.py` - No changes expected

### Configuration Files (2 files)
- ✏️ `config/server_specs.json` - Major changes (add CPU variants)
- ✏️ `config/codecs.json` - Medium changes (update quality factors)

### Test Files (4 files)
- ✏️ `backend/app/tests/test_bitrate.py` - Update expected values
- ✏️ `backend/app/tests/test_storage.py` - Update expected values
- ✏️ `backend/app/tests/test_api.py` - Update expected values
- ➕ `backend/app/tests/test_core_calculations_validation.py` - NEW FILE

### Documentation Files (3 files)
- ➕ `docs/adr/003-calculation-formula-alignment.md` - NEW FILE
- ✏️ `IMPLEMENTATION_STATUS.md` - Update status
- ✏️ `README.md` - Add note about formula alignment

**Total Files**: 15 (13 modified, 2 new)

---

## ⚠️ Risk Assessment

### High Risk Areas

1. **Breaking Changes**: New formulas will produce different results
   - **Mitigation**: Create golden test suite with known inputs/outputs
   - **Mitigation**: Document all changes in ADR

2. **Backward Compatibility**: Existing calculations may be referenced
   - **Mitigation**: Keep function signatures identical
   - **Mitigation**: Add deprecation warnings if needed

3. **Test Failures**: All existing tests will fail with new formulas
   - **Mitigation**: Update tests systematically
   - **Mitigation**: Run tests after each module update

4. **Frontend Impact**: UI may display different values
   - **Mitigation**: Update frontend expectations
   - **Mitigation**: Add migration notes for users

### Medium Risk Areas

1. **Configuration Changes**: JSON files structure may change
   - **Mitigation**: Maintain backward compatibility where possible
   - **Mitigation**: Add validation for new fields

2. **Performance**: Power function (area^0.7) may be slower
   - **Mitigation**: Profile performance
   - **Mitigation**: Cache results if needed

---

## ✅ Success Criteria

1. ✅ All formulas match core_calculations.md exactly
2. ✅ All constants match documented values
3. ✅ All CPU variants properly defined
4. ✅ Golden test suite passes with known values
5. ✅ All existing tests updated and passing
6. ✅ API returns consistent results
7. ✅ Documentation complete (ADR + README)
8. ✅ No regression in functionality

---

## 📈 Progress Tracking

**Overall Progress**: 0/23 tasks (0%)

- **Audit Phase**: 0/10 tasks (0%)
- **Implementation Phase**: 0/10 tasks (0%)
- **Validation Phase**: 0/2 tasks (0%)
- **Documentation Phase**: 0/1 tasks (0%)

---

## 🚀 Next Steps

### Immediate Actions (Start Here)

1. **Read core_calculations.md thoroughly** - Understand all formulas
2. **Start with Audit Bitrate Calculation** - Most critical deviation
3. **Create test cases with known values** - Establish baseline
4. **Update bitrate.py with new formula** - Implement area^0.7
5. **Run tests and validate** - Ensure correctness

### Recommended Order

1. Bitrate calculation (CRITICAL - affects everything)
2. Quality factor (CRITICAL - affects bitrate)
3. Max camera bitrate (HIGH - affects bandwidth/failover)
4. Server RAM calculation (HIGH - affects server sizing)
5. CPU variants (HIGH - affects server tiers)
6. Storage calculation (MEDIUM - verify constants)
7. Network interface calculations (MEDIUM)
8. Storage throughput (MEDIUM)
9. Failover logic (HIGH)
10. Server presets (MEDIUM)
11. Validation tests (CRITICAL)
12. Update existing tests (HIGH)
13. Documentation (HIGH)

---

## 📞 Questions to Resolve

1. **brandFactor**: What is this value? Not defined in core_calculations.md
2. **frameRateFactor**: Is this just FPS or a normalized value?
3. **codecRatio**: Is this the compression_factor from config?
4. **lowMotionQuality**: Default value? Configurable?
5. **Server Presets**: Should we replace existing tiers or add new ones?
6. **Quality Slider**: Discrete levels or continuous 0-100%?

---

## 🎓 Key Learnings

1. **Power Function Critical**: area^0.7 is fundamentally different from linear
2. **Constants Matter**: 40MB/camera, 3072MB client are exact requirements
3. **CPU Variants Essential**: Different server tiers have different limits
4. **Max vs Average Bitrate**: Must track both for accurate planning
5. **Iterative Failover**: Can't use simple multiplication

---

## 📚 References

- **Source Document**: `/docs/core_calculations.md`
- **Current Implementation**: `/backend/app/services/calculations/`
- **Configuration**: `/config/*.json`
- **Tests**: `/backend/app/tests/`

---

**Status**: 🔴 **READY TO START**  
**Priority**: 🔥 **CRITICAL - HIGHEST PRIORITY**  
**Estimated Completion**: 3-5 days with focused effort

---

*This plan ensures the Nx System Calculator produces mathematically accurate results consistent with the legacy system.*

