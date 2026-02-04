# Quick diagnostic script
Write-Host "=== Checking flask-exam service ===" -ForegroundColor Cyan
ssh -i $env:USERPROFILE\.ssh\oracle_cloud_key ubuntu@151.145.84.100 "sudo systemctl is-active flask-exam"

Write-Host "`n=== Testing local connection on VM ===" -ForegroundColor Cyan
ssh -i $env:USERPROFILE\.ssh\oracle_cloud_key ubuntu@151.145.84.100 "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5001/"

Write-Host "`n=== Checking iptables ===" -ForegroundColor Cyan
ssh -i $env:USERPROFILE\.ssh\oracle_cloud_key ubuntu@151.145.84.100 "sudo iptables -L INPUT -n | grep -E '80|443|5001'"

Write-Host "`n=== Testing external connection to port 5001 ===" -ForegroundColor Cyan
Test-NetConnection -ComputerName 151.145.84.100 -Port 5001 -InformationLevel Detailed
