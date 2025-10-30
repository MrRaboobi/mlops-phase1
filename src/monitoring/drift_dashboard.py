import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

def generate_drift_report():
    reference_data = pd.DataFrame({"signal": [0.1, 0.2, 0.3, 0.4]})
    current_data = pd.DataFrame({"signal": [0.15, 0.25, 0.35, 0.45]})

    report = Report(metrics=[DataDriftPreset()])
    report_result = report.run(reference_data=reference_data, current_data=current_data)
    report_result.save_html("docs/drift_report.html")

    
    print("Evidently drift report saved to docs/drift_report.html")

if __name__ == "__main__":
    generate_drift_report()