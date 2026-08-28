# robot-eval

Honest measurement for robot policy evaluation. See PLAN.md.

- analysis/  leaderboard corpus audit -> cleaning -> variance decomposition -> concordance
- robostats/ MIT statistics library (CIs, rank agreement, power)
- paper/     CoRL 2026 workshop submission (deadline Oct 9)

Setup: pip install -e robostats/ && python analysis/01_audit.py
