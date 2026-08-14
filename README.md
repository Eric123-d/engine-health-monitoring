# Simplified Aircraft Engine Health Monitor

This is a compact interview project that demonstrates early fault warning for an aircraft engine. The repository contains only ten files and does not save training traces, intermediate matrices, or duplicate reports.

The single `data.csv` file contains 12,000 consecutive `health_state=1` samples from unit 5 of NASA N-CMAPSS DS02-006. The sampling rate is 1 Hz. T50 is the target, and 31 operating-condition, sensor, and virtual-sensor variables are used as inputs. Temperatures are converted to degrees Celsius.

## Five modules

1. `module1_data.py` removes invalid values, duplicates, and isolated spikes, then makes a chronological 40%/30%/30% split. It does not reject NASA-labelled healthy operating points merely because a regression model has a large residual.
2. `module2_baseline.py` trains an Elastic Net model on the first 40%. It calculates the non-negative absolute residual and a one-sided 10-SD safety boundary.
3. `module3_kalman.py` injects several gradual fault patterns into the middle 30% and learns the A, B, C, bias, Q, and R terms. At each second, the adaptive Kalman filter updates only the state and P, then forecasts no more than 600 seconds.
4. `module4_root_cause.py` compares standardized sensor changes at the first alarm and identifies the likely source.
5. `module5_adjustment.py` verifies a supervised return toward the pre-fault reference state. It never sends a real control command.

## Run

```powershell
pip install -r requirements.txt
./run_all.ps1
```

Each module prints a short validation result. Fault tests cover 10, 30, 100, 300, and 600 one-second samples. An alarm requires two consecutive residual increases and a Kalman forecast that crosses the boundary within 600 seconds; the red alarm point normally appears about two seconds after fault onset. The only saved result is `residual_alarm.png`.

The injected faults, statistical boundary, and adjustment logic are simplified demonstrations. They are not real NASA fault responses, certified engine protection limits, or control instructions.
