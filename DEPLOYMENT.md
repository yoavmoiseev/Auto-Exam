# Deployment: Exam System на VM вместе с WEB-ScSc

## 📋 Информация о развертывании

**Сервер:** Oracle Cloud VM  
**IP:** 151.145.84.100  
**Текущий проект (соседний):** WEB-ScSc (school shadow)  
**Наш проект:** Ex (Exam System)  
**Домен:** Будет добавлен (subdomain)  

---

## 🏗️ Структура развертывания

```
~/apps/
├── WEB-ScSc/          # Школьный расписание (уже запущено)
│   ├── app.py (Flask на :5000)
│   └── ...
└── Ex/                # Система экзаменов (новое)
    ├── app.py (Flask на :5001)
    └── ...
```

---

## 📦 Зависимости

- Python 3.8+
- Flask
- Ubuntu 22.04 LTS (на VM)
- Nginx (reverse proxy)
- Systemd (для управления сервисами)
- SSH ключ: `~/.ssh/oracle_cloud_key`

---

## 🚀 Этапы развертывания

### 1️⃣ На локальном ПК (подготовка)

```powershell
# Убедиться, что все изменения запушены на GitHub
cd C:\Users\User\Desktop\Ex
git status
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2️⃣ На VM (выполнить через SSH)

```bash
# Подключиться к серверу
ssh -i ~/.ssh/oracle_cloud_key ubuntu@151.145.84.100

# Перейти в папку apps
cd ~/apps

# Склонировать репозиторий Ex
git clone https://github.com/yoavmoiseev/Auto-Exam.git Ex

# Перейти в папку проекта
cd Ex

# Создать виртуальное окружение
python3 -m venv venv

# Активировать окружение
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл (если нужен)
# cp .env.example .env (если есть)
# nano .env  # Отредактировать если нужно
```

### 3️⃣ Настроить Systemd сервис

```bash
# Создать файл сервиса для Ex
sudo nano /etc/systemd/system/flask-exam.service
```

**Содержимое `/etc/systemd/system/flask-exam.service`:**

```ini
[Unit]
Description=Exam System Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/apps/Ex
ExecStart=/home/ubuntu/apps/Ex/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment="FLASK_ENV=production"
Environment="FLASK_PORT=5001"

[Install]
WantedBy=multi-user.target
```

**Включить и запустить:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-exam
sudo systemctl start flask-exam
sudo systemctl status flask-exam
```

### 4️⃣ Настроить Nginx reverse proxy

**Добавить в `/etc/nginx/sites-available/default` или создать новый конфиг:**

```nginx
# Для Ex (Exam System)
upstream exam_app {
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name exam.yamsoft.org;  # Будет добавлен позже

    location / {
        proxy_pass http://exam_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Проверить и перезагрузить Nginx:**

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔄 Обновление кода на сервере

### Способ 1: Вручную через SSH

```bash
ssh -i ~/.ssh/oracle_cloud_key ubuntu@151.145.84.100

cd ~/apps/Ex
git pull origin main
sudo systemctl restart flask-exam
```

### Способ 2: PowerShell скрипт (как в WEB-ScSc)

Создать `update_exam_server.ps1`:

```powershell
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
```

---

## 🧪 Проверка

### После развертывания:

```bash
# Проверить статус сервиса
sudo systemctl status flask-exam

# Проверить логи
sudo journalctl -u flask-exam -n 50 --no-pager

# Проверить процесс
ps aux | grep "python app.py"

# Проверить порт
sudo netstat -tulpn | grep 5001
```

### Проверить через curl:

```bash
curl http://127.0.0.1:5001/
```

---

## ⚠️ Важные моменты

1. **Порты:**
   - WEB-ScSc: 5000
   - Ex (Exam): 5001
   - Nginx: 80/443

2. **Переменные окружения:**
   - Если нужны, создать `.env` файл в папке Ex
   - Не забыть добавить в `.gitignore`

3. **Бэкапы:**
   - Регулярно бэкапить базу данных (если есть)
   - Бэкапить user uploads

4. **SSL сертификат:**
   - Использовать Let's Encrypt (certbot)
   - После добавления домена

5. **Конфликты портов:**
   - WEB-ScSc уже на 5000 ✅
   - Ex должен быть на 5001 (или другой свободный)

---

## 🔧 Troubleshooting

### Проблема: "Port 5001 already in use"
```bash
sudo lsof -i :5001  # Найти процесс
sudo kill -9 <PID>   # Убить процесс
sudo systemctl restart flask-exam
```

### Проблема: "Permission denied" при git pull
```bash
# Проверить SSH ключ
ssh -i ~/.ssh/oracle_cloud_key -T git@github.com

# Если нужно, перегенерировать
ssh-keygen -t ed25519 -f ~/.ssh/oracle_cloud_key
```

### Проблема: Nginx не видит приложение
```bash
# Перезагрузить Nginx
sudo systemctl restart nginx

# Проверить конфиг
sudo nginx -t
```

---

## 📝 Команда для быстрого развертывания

```bash
ssh ubuntu@151.145.84.100 -i ~/.ssh/oracle_cloud_key << 'EOF'
cd ~/apps && \
git clone https://github.com/yoavmoiseev/Auto-Exam.git Ex && \
cd Ex && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
echo "✅ Ex готов к запуску"
EOF
```

---

**Статус:** 🟡 В подготовке  
**Дата последнего обновления:** 3 февраля 2026  
**Ответственный:** GitHub Copilot
