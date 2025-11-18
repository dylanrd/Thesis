# Sensor Activation Analysis Summary
## Threshold Log: 20251116_143220

### Overview
This analysis identifies which sensors were activated (pressed) when you placed a wooden block (20x10 cm) on the sensor array and stood on it.

### Key Statistics
- **Total frames analyzed:** 39
- **Total sensors activated:** 1,897 out of 2,304 sensors (82.3%)
- **Average activation frequency:** 15.9 frames per sensor
- **Most frequently activated sensor:** Sensor ID 1927 (activated in all 39 frames)

### Top 30 Most Frequently Activated Sensors

These sensors showed the most consistent activation across all frames:

| Sensor ID | Row | Col | Press Count | Max Change (Ohms) | Avg Change (Ohms) | Baseline (Ohms) |
|-----------|-----|-----|-------------|-------------------|-------------------|-----------------|
| 1927 | 40 | 7 | 39 | 387,681 | 265,585 | 601,218 |
| 1937 | 40 | 17 | 39 | 427,430 | 301,406 | 515,003 |
| 2034 | 42 | 18 | 38 | 341,215 | 247,543 | 601,218 |
| 1939 | 40 | 19 | 38 | 437,929 | 256,340 | 550,971 |
| 1943 | 40 | 23 | 37 | 505,530 | 348,471 | 483,369 |
| 2113 | 44 | 1 | 37 | 508,654 | 221,096 | 391,444 |
| 2130 | 44 | 18 | 37 | 566,143 | 254,591 | 376,290 |
| 2185 | 45 | 25 | 37 | 623,245 | 198,021 | 365,655 |
| 1959 | 40 | 39 | 37 | 358,935 | 295,196 | 583,498 |
| 2138 | 44 | 26 | 37 | 540,814 | 229,833 | 379,970 |
| 2017 | 42 | 1 | 36 | 422,123 | 301,817 | 566,776 |
| 2054 | 42 | 38 | 36 | 267,596 | 240,062 | 721,304 |
| 1245 | 25 | 45 | 36 | 243,810 | 237,541 | 721,304 |
| 2152 | 44 | 40 | 36 | 493,356 | 305,114 | 471,757 |
| 2153 | 44 | 41 | 36 | 493,356 | 305,114 | 471,757 |
| 2139 | 44 | 27 | 36 | 612,609 | 238,976 | 376,290 |
| 1951 | 40 | 31 | 35 | 460,077 | 321,779 | 528,822 |
| 2025 | 42 | 9 | 35 | 437,929 | 329,697 | 550,971 |
| 2183 | 45 | 23 | 35 | 534,599 | 237,632 | 407,834 |
| 1212 | 25 | 12 | 35 | 605,830 | 243,906 | 314,954 |
| 2205 | 45 | 45 | 35 | 601,355 | 509,998 | 387,545 |
| 2206 | 45 | 46 | 35 | 601,355 | 509,998 | 387,545 |
| 2207 | 45 | 47 | 35 | 601,355 | 509,998 | 387,545 |
| 2140 | 44 | 28 | 34 | 434,128 | 173,444 | 358,884 |
| 2272 | 47 | 16 | 33 | 198,336 | 66,259 | 291,051 |
| 2146 | 44 | 34 | 33 | 502,480 | 210,123 | 358,884 |
| 2147 | 44 | 35 | 33 | 374,395 | 165,473 | 334,077 |
| 2301 | 47 | 45 | 33 | 195,887 | 192,597 | 793,012 |
| 1160 | 24 | 8 | 33 | 28,126 | 16,186 | 79,112 |
| 58 | 1 | 10 | 33 | 46,520 | 33,343 | 119,907 |

### Sensor Grid Location Analysis

The activated sensors are primarily concentrated in:
- **Rows 40-47** (bottom portion of the grid)
- **Rows 25-26** (middle section)
- **Rows 1-2** (top section)

This suggests your wooden block was positioned in the lower-middle to bottom area of the sensor array.

### For Your Experiment

To analyze how sensor values change on average over the pressed area with different weights, you should focus on:

1. **Primary sensors (most consistent):** Sensors 1927, 1937, 2034, 1939, 1943, 2113, 2130, 2185, 1959, 2138
   - These were activated in 37-39 frames and show the most reliable pressure response

2. **Secondary sensors:** Sensors 2017, 2054, 1245, 2152, 2153, 2139, 1951, 2025, 2183, 1212
   - Activated in 35-36 frames, still very consistent

3. **All activated sensors:** See `activated_sensors_analysis.csv` for complete list of 1,897 sensors with detailed statistics

### Data Files

- **activated_sensors_analysis.csv:** Complete analysis with all activated sensors, their press counts, resistance changes, and statistics
- **baseline_values.csv:** Baseline resistance values for all sensors
- **threshold_changes.csv:** Raw threshold change data

### Notes

- Resistance increases when pressure is applied (typical for pressure-sensitive sensors)
- Sensors with higher baseline resistance tend to show larger absolute changes
- The average resistance change across all activated sensors is 65,433 Ohms
- Maximum resistance change observed: 961,550 Ohms (Sensor ID 136)

### Next Steps for Your Experiment

1. Use the top 30-50 sensors listed above for your weight experiment
2. Track average resistance values for these sensors across different weights
3. Compare the average resistance change vs. weight applied
4. Consider normalizing by baseline resistance to account for sensor-to-sensor variation

