@echo off
rem r931 bm-a S6 chain launcher (r926 bloodline rolled; 39 legs incl regime_thermo_build per O-20261009-2340)
echo START %date% %time%
cd /d C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney
python results\_r931bma_s6_driver.py > results\_r931bma_s6_driver.log 2>&1
