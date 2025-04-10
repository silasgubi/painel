import requests
import json
import speedtest
from datetime import datetime
import holidays
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

# Escopo de acesso (ler eventos do calendário)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# 1. Criar o arquivo service_account.json com o conteúdo do segredo do GitHub
credentials_json = os.environ['GOOGLE_CREDENTIALS']
with open('service_account.json', 'w', encoding='utf-8') as f:
    f.write(credentials_json)

# 2. Autenticar via Service Account
creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

# 3. Data e hora atuais
now = datetime.now()
data_hoje = now.strftime("%d/%m/%Y")
hora_hoje = now.strftime("%H:%M:%S")
dia_semana = now.strftime("%A")

# 4. Feriados no Brasil (estado SP)
feriados = holidays.Brazil(prov='SP')
feriado_hoje = feriados.get(now.date())

# 5. Buscar clima (wttr.in)
clima = requests.get('https://wttr.in/Sao+Paulo?format=3').text

# 6. Buscar agenda no Google Calendar
end_of_day = now.replace(hour=23, minute=59, second=59)
events_result = service.events().list(
    calendarId='primary',
    timeMin=now.isoformat() + 'Z',
    timeMax=end_of_day.isoformat() + 'Z',
    singleEvents=True,
    orderBy='startTime'
).execute()
events = events_result.get('items', [])

agenda = ""
if not events:
    agenda = "Nenhum compromisso"
else:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start:
            hora_evento = start[11:16]
        else:
            hora_evento = start
        agenda += f"{hora_evento} - {event.get('summary', 'Sem título')}<br>"

# 7. Teste de velocidade Internet
try:
    st = speedtest.Speedtest()
    st.get_best_server()
    down = int(st.download() / 1_000_000)
    up = int(st.upload() / 1_000_000)
    status_internet = f"Velocidade: {down} ↓ / {up} ↑"
except:
    status_internet = "Offline"

# 8. Montar HTML final
feriado_str = f"Feriado: {feriado_hoje}" if feriado_hoje else ""
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quarto</title>
    <style>
        body {{
            background-color: #000;
            color: #fff;
            font-family: sans-serif;
            text-align: center;
            padding: 20px;
        }}
        h1 {{
            font-size: 3em;
        }}
        h2 {{
            font-size: 2em;
        }}
        .card {{
            background: #111;
            padding: 15px;
            margin: 10px auto;
            border-radius: 10px;
            width: 300px;
        }}
    </style>
</head>
<body>
    <h1>{hora_hoje}</h1>
    <h2>{dia_semana}, {data_hoje}</h2>
    <div class="card">{clima}</div>
    <div class="card">{feriado_str}</div>
    <div class="card"><b>Agenda:</b><br>{agenda}</div>
    <div class="card">{status_internet}</div>
</body>
</html>
"""

# 9. Salvar o HTML em index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
