#I also have a dependency_audit.sh file for Unix systems. Here is the equivalent shell script for Powershell.
Write-Host "Starting dependency audit..."
pip install --quiet pip-audit pip-licenses

Write-Host "`nRunning pip-audit for vulnerability scanning..."
pip-audit | Out-File -FilePath docs/compliance_report.txt -Encoding utf8

Write-Host "`nChecking open-source licenses..."
pip-licenses --from=mixed --format=markdown | Out-File -Append docs/compliance_report.txt -Encoding utf8

Write-Host "`nDependency audit and license report saved to docs/compliance_report.txt"
