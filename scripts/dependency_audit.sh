#!/bin/sh
echo "Starting dependency audit..."
pip install --quiet pip-audit pip-licenses

echo "\nRunning pip-audit for vulnerability scanning..."
pip-audit > docs/compliance_report.txt

echo "\nChecking open-source licenses..."
pip-licenses --from=mixed --format=markdown >> docs/compliance_report.txt

echo "\nDependency audit and license report saved to docs/compliance_report.txt"
