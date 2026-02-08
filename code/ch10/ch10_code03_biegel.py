import pandas as pd
#import json
from evidently import Report
from evidently.presets import DataDriftPreset

# Reference data
reference = pd.DataFrame({
    "power_kw": [1.8, 2.0, 1.9, 2.1, 2.0, 1.95, 2.05]
})

# Current data
current = pd.DataFrame({
    "power_kw": [2.4, 2.5, 2.6, 2.3, 2.7, 2.5, 2.6]
})

# Create report
report = Report([DataDriftPreset()])

# Run evaluation
result = report.run(current, reference)

# Save HTML
result.save_html("power_drift_report.html")
print("Drift report saved as power_drift_report.html")

# Parse JSON
#report_dict = json.loads(result.json())

print(result.json())
