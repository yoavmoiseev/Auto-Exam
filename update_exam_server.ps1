# Скрипт для обновления Exam System на сервере
# Использование: .\update_exam_server.ps1

Write-Host "🚀 Обновление Exam System на сервере..." -ForegroundColor Cyan

# Git push локально
Write-Host "`n📤 Отправка изменений на GitHub..." -ForegroundColor Yellow
git add .
$message = Read-Host "Введите сообщение коммита (или Enter для 'Update')"
if ([string]::IsNullOrWhiteSpace($message)) {
    $message = "Update"
}
git commit -m $message
git push origin main

# Обновление на сервере
Write-Host "`n📥 Обновление кода на сервере..." -ForegroundColor Yellow
& 'C:\Windows\System32\OpenSSH\ssh.exe' -i ~\.ssh\oracle_cloud_key ubuntu@151.145.84.100 'cd ~/apps/Ex; git pull; sudo systemctl restart flask-exam'

# Проверка статуса
Write-Host "`nâœ… Проверка статуса..." -ForegroundColor Yellow
& 'C:\Windows\System32\OpenSSH\ssh.exe' -i ~\.ssh\oracle_cloud_key ubuntu@151.145.84.100 'sudo systemctl status flask-exam --no-pager | head -10'

Write-Host "`n🎉 Готово! Exam System обновлен!" -ForegroundColor Green
