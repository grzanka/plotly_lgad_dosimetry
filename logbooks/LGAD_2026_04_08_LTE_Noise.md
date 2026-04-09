# LGAD Experiments - April 8, 2026
## LTE (Low-Temperature Environment) Noise Characterization

**Date:** April 8, 2026  
**Objective:** Measure and characterize Low-Temperature Environment (LTE) noise from LGAD detector  
**Beam Status:** No beam - noise measurements only  
**Data Location (Local):** `/home/leszekgrzanka/workspace/lgad_data`  
**Data Location (Ares):** `/net/pr2/projects/plgrid/plggdiamonds/lgad/2025/20260408`

---

## Experiment Overview

This experimental campaign focuses on characterizing Low-Temperature Environment (LTE) noise in LGAD (Low-Gain Avalanche Detector) detectors. No particle beam was used during these measurements; instead, we isolated the detector systems and measured the intrinsic noise characteristics at various detector positions and distances.

### Key Parameters

- **Acquisition System:** LeCroy WP404HD Oscilloscope (Firmware: 11.1.0)
- **Channels Used:** C1, C2, C3 (Primary signal channels)
- **Auxiliary Channels:** SpecAn, SpecAn2 (Spectrum analysis)
- **File Format:** LeCroy binary format (.trc files)

---

## Data Structure and Organization

Total experimental data size: **83 GB**

### Measurement Breakdown

| Measurement | Type | Size | TRC Files | Subdirectories | Description |
|-------------|------|------|-----------|-----------------|-------------|
| Meas01 | `.txt` files | 19 M | 0 | 1 | Initial test/specification measurements |
| Meas02 | `.txt` files | 6.1 M | 0 | 1 | Test series |
| Meas03 | `.txt` files | 6.1 M | 0 | 1 | Test series |
| Meas04 | `.txt` files | 6.1 M | 0 | 1 | Test series |
| Meas05 | `.txt` files | 6.1 M | 0 | 1 | Test series |
| Meas06 | `.txt` files | 6.1 M | 0 | 1 | Test series |
| Meas07 | `.trc` + `.lss` | 176 M | 0 | 10 | Multi-distance measurement campaign |
| Meas08 | `.trc` + `.lss` | 14 G | 30 | 11 | Comprehensive distance-dependent study |
| Meas09 | `.trc` + `.lss` | 69 G | 149 | 6 | High-statistics measurement campaign |

### Distance Configurations Tested

The main measurement campaigns (Meas07, Meas08, Meas09) include distance-dependent measurements:

- **00cm** - Reference/optimal position
- **05cm** - 5 cm displacement
- **10cm** - 10 cm displacement
- **15cm** - 15 cm displacement  
- **20cm** - 20 cm displacement
- **25cm** - 25 cm displacement
- **30cm** - 30 cm displacement
- **34cm** - 34 cm displacement
- **best** - Best configuration identified
- **final** - Final optimized configuration

---

## Data Format Details

### TRC Files (LeCroy Binary Format)

**File Type:** Binary waveform data  
**File Size:** ~478 MB per file (100 MHz sampling, high-resolution capture)  
**Channels:** Multi-channel oscilloscope recordings (C1, C2, C3)

**Format Components:**
- Magic header: `#9500200346WAVEDESCLECROY_2_3`
- Binary encoded waveform data
- Time-domain voltage measurements with high temporal resolution
- Device information: LeCroy WP404HD

**Reading Requirements:** 
- LeCroy software or compatible binary decoder
- Contains full acquisition parameters in header
- Supports direct import to analysis software

### LSS Files (LeCroy Configuration)

**File Type:** LeCroy XStream VBScript configuration  
**File Size:** ~92 KB  
**Format:** Text-based VBScript commands

**Key Configuration Elements:**
```
' LeCroy WP404HD Configuration
' Acquisition Date: Wednesday, April 8, 2026 7:02:55 PM
' Firmware Version: 11.1.0
' Serial: LCRY4607N02241

[Probe Calibration Parameters]
- Gain settings (channels 1-4)
- Offset corrections
- Impedance skew calculations
- Common mode settings

[Acquisition Settings]
- Timebase configuration
- Trigger parameters
- Channel coupling
- Vertical resolution
```

**Typical Configuration includes:**
- Probe calibration for all channels
- Deskew reference channel (typically C2)
- Gain/offset adjustments
- Sampling rate and memory depth
- Trigger mode and level settings

---

## Acquisition Campaign Details

### Physics Motivation

Low-Temperature Environment (LTE) noise characterization is essential for:
1. Understanding intrinsic detector noise floor
2. Optimizing signal-to-noise ratio for physics analysis
3. Identifying systematic noise sources
4. Performance comparison across different configurations
5. Validation of detector operation in low-noise conditions without particle interference

### Measurement Strategy

**Phase 1: Initial Tests (Meas01-06)**
- Specification verification
- System checkout
- Cable and connector testing
- Brief noise characterization (~6-19 MB per measurement)

**Phase 2: Distance Optimization (Meas07)**
- First comprehensive scan at 9 distance settings
- 176 MB of data across all distances
- Used to identify optimal detector positioning

**Phase 3: Primary Campaign (Meas08)**
- Systematic noise measurement at multiple distances
- ~14 GB acquisition with 30 TRC files
- Higher statistical quality than Meas07
- 11 subdirectories covering 00cm to 34cm range

**Phase 4: Extended Campaign (Meas09)**
- High-statistics measurement campaign
- ~69 GB of data with 149 TRC files
- Most comprehensive dataset
- Additional distance configurations

---

## Key File Information

### Sample TRC File
```
Path: /home/leszekgrzanka/workspace/lgad_data/Meas08/00cm/C1--AIC144-second---00000.trc
Size: 478 M
Device: LeCroy WP404HD (Serial: LCRY4607N02241)
Format: Binary waveform (LeCroy proprietary)
Channels: C1, C2, C3
Acquisition: April 8, 2026
```

### Sample LSS Configuration
```
Path: /home/leszekgrzanka/workspace/lgad_data/Meas08/00cm/setup.lss
Size: 92 K
Format: VBScript with LeCroy XStreamDSO API calls
Device: LeCroy WP404HD (Firmware 11.1.0)
Lines: 3497
Configuration: Full oscilloscope setup parameters
```

---

## Processing and Analysis

### Required Tools
- **LeCroy WaveRunner:** Binary TRC file viewer and exporter
- **Python Analysis:** Custom scripts to parse TRC headers and extract waveforms
- **Waveform Analysis:** Time-domain noise characterization, spectral analysis
- **Statistical Methods:** SNR calculation, noise floor determination

### Next Steps
- [ ] Parse TRC file headers and extract acquisition parameters
- [ ] Develop Python-based TRC file reader
- [ ] Perform noise spectral analysis (FFT)
- [ ] Compare noise characteristics across distances
- [ ] Identify optimal detector geometry
- [ ] Document detector positions and setup details
- [ ] Compare measurements across Meas07, Meas08, Meas09 campaigns

---

## Data Integrity and Backup

**Backup Status:**
- ✅ Local copy: `/home/leszekgrzanka/workspace/lgad_data` (83 GB)
- ✅ Ares (plgrid) copy: `/net/pr2/projects/plgrid/plggdiamonds/lgad/2025/20260408` (synchronized)

**Data Verification:** To be confirmed with MD5/SHA checksums

---

## Related Resources

- **Main Repository:** `/home/leszekgrzanka/workspace/plotly_lgad_dosimetry`
- **Analysis Scripts:** `dosimetry.py`, `analyse.ipynb`
- **Monte Carlo Simulations:** `montecarlo/mc.ipynb`
- **Hardware Configuration:** See `setup.lss` files for each measurement

---

## Metadata

- **Date Created:** 2026-04-09
- **Last Updated:** 2026-04-09
- **Status:** Preliminary documentation - under development
- **Notes to Self:** Extend with detector position details and experimental aims in subsequent prompts

---

## Appendix: LeCroy Configuration Structure

The `setup.lss` files contain comprehensive oscilloscope configuration with sections for:

1. **XStreamDSO Configuration** - Main API access
2. **ProbesCal** - Probe calibration and deskewing
3. **Preferences** - User interface and general settings
4. **Channels** - Individual channel configuration
5. **Timebase** - Sampling rate and acquisition window
6. **Trigger** - Trigger source, level, and mode
7. **Measurements** - Automated measurement definitions
8. **Cursors** - Cursor positioning and analysis

Each section is VBScript-compatible and can be programmatically modified or parsed for automation.
