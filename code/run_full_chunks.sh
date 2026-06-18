#!/bin/bash
set -e

cd /Users/madanibezoui/Documents/Projects/ALUR/code

echo "Wiping old chunks..."
rm -f ../results/protocol/tmp_v2/bench_*.npz

echo "Running chunks..."
python3 run_protocol.py --config configs/ejor_final.yaml --stage benchmark --csize 100
python3 run_protocol.py --config configs/ejor_final.yaml --stage benchmark --csize 300
python3 run_protocol.py --config configs/ejor_final.yaml --stage benchmark --csize 1000 --crit 3,5,8
python3 run_protocol.py --config configs/ejor_final.yaml --stage benchmark --csize 1000 --crit 10,15,20

echo "Finalizing benchmark..."
python3 run_protocol.py --config configs/ejor_final.yaml --stage bfinalize

echo "Running other stages..."
python3 run_protocol.py --config configs/ejor_final.yaml --stage redundancy
python3 run_protocol.py --config configs/ejor_final.yaml --stage probes
python3 run_protocol.py --config configs/ejor_final.yaml --stage gates
python3 run_protocol.py --config configs/ejor_final.yaml --stage direct
python3 run_protocol.py --config configs/ejor_final.yaml --stage stochastic
python3 run_protocol.py --config configs/ejor_final.yaml --stage multistakeholder

echo "Generating final report..."
python3 run_protocol.py --config configs/ejor_final.yaml --stage report

echo "Done!"
