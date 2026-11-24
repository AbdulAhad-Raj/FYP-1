# SentinelX four-sensor recording validation report

## Executive result

- Five uploaded CSVs were read successfully. All five contain recordings timestamped **17 November 2026**; no 16 November file was included in this upload.
- Consolidated raw observations: **20,381 rows**.
- Target device MAC `B2:BF:3F:73:01:38` appears in **1,261 rows** (all are DATA frames on channel 12).
- Exact-time four-sensor fingerprints: **220 complete fingerprints** after averaging repeated same-sensor reports at the same timestamp within each capture file.
- No positioning model was trained.

## 1. Device identification

- Target MAC: `B2:BF:3F:73:01:38`.
- Target-device rows by capture: Centre 253, North 209, South 356, East 272, West 171.
- The files also contain 95 other distinct MAC addresses (96 unique MACs total across the full raw dataset). The consolidated raw file preserves them; fingerprint generation filters to the requested target MAC.

## 2. Sensor coverage

| Sensor ID | Physical location | Raw observations | Target-device observations |
|---|---:|---:|---:|
| SENSOR-01 | NORTH | 5,323 | 307 |
| SENSOR-02 | SOUTH | 5,133 | 336 |
| SENSOR-03 | EAST | 5,122 | 281 |
| SENSOR-04 | WEST | 4,803 | 337 |

Every raw row has a recognized sensor ID and the sensor-to-location mapping is internally consistent: SENSOR-01=NORTH, SENSOR-02=SOUTH, SENSOR-03=EAST, SENSOR-04=WEST.

## 3. Position labels and capture separation

| Capture file label | Raw rows | Time range (local timestamps as recorded) | Target rows | Complete fingerprints |
|---|---:|---|---:|---:|
| Centre | 4,248 | 2026-11-17T15:39:44 to 2026-11-17T15:42:50 | 253 | 39 |
| North | 3,892 | 2026-11-17T15:46:47 to 2026-11-17T15:49:47 | 209 | 35 |
| South | 4,024 | 2026-11-17T15:58:02 to 2026-11-17T16:01:01 | 356 | 64 |
| East | 4,562 | 2026-11-17T16:03:13 to 2026-11-17T16:06:15 | 272 | 51 |
| West | 3,655 | 2026-11-17T16:06:43 to 2026-11-17T16:09:43 | 171 | 31 |

The `Location` column in the source files identifies the **sensor's physical location**, not the target's capture position. The capture position in the output is therefore derived from the uploaded filename (Centre/North/South/East/West). This avoids incorrectly using the sensor-location field as the ground-truth position.

## 4. RSSI and data-quality checks

- Missing values in the original 10 source columns: **0**.
- RSSI range across all devices: **-98 to -21 dBm**; median **-75.0 dBm**.
- Target-device RSSI range: **-80 to -21 dBm**; median **-53.0 dBm**.
- All target-device records use channel 12 and frame type DATA.
- Repeated target reports at the same capture/timestamp/sensor key: **72 rows involved**. These are retained in the raw dataset and averaged for the fingerprint dataset.

## 5. Synchronization

- Target device was observed at 372 distinct capture/timestamp combinations (summed across five files).
- Candidate target timestamp groups: **372**.
- Groups with all four sensor readings at the exact same recorded second: **220**.
- Groups without all four sensors at that exact second: **152**. These are excluded from the strict synchronized fingerprint file rather than filled or interpolated.
- Synchronization rule: exact timestamp within the same capture file. Multiple reports from one sensor at that timestamp are averaged. No cross-file timestamp matching is performed.

## 6. Coordinate readiness and next requirement

Ground-truth position labels are assigned from the five filenames, but **surveyed x/y coordinates were not present in the uploaded CSVs**. Accordingly, the calibration dataset contains `X_m` and `Y_m` columns left blank and explicitly marked pending. Coordinates must be supplied before this can be treated as a coordinate-labelled calibration set or used for a 2D positioning evaluation.

## Deliverables

1. `01_consolidated_raw_observations.csv` — all source rows, with capture-position and source-file provenance.
2. `02_synchronized_four_sensor_fingerprints.csv` — target MAC only; complete exact-time four-sensor fingerprints.
3. `03_sensor_coverage_data_quality_report.md` — this validation report.
4. `04_coordinate_labelled_calibration_dataset.csv` — complete fingerprints with ground-truth position labels and blank coordinate fields awaiting surveyed coordinates.

**Decision:** the recordings demonstrate coverage from all four sensors at every capture position and provide 220 complete synchronized target-device fingerprints. They are suitable for the next calibration-preparation step, but coordinate-based calibration/evaluation is not complete until the five position coordinates are supplied.