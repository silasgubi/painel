import requests
import json
import speedtest
from datetime import datetime
import holidays
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Pega o conteúdo do segredo do GitHub
credentials_json = os.environ.get('GOOGLE_CREDENTIALS')

# Cria o arquivo credentials.json
with open('credentials.json', 'w') as f:
    f.write(credentials_json)

# Google Calendar API - credenciais do secret
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_console()
service = build('calendar', 'v3', credentials=creds)

# Data e hora atual
now = datetime.now()
data_hoje = now.strftime("%d/%m/%Y")
hora_hoje = now.strftime("%H:%M:%S")
dia_semana = now.strftime("%A")

# Buscar feriados Brasil + SP
feriados = holidays.Brazil(prov='SP')
feriado_hoje = feriados.get(now.date())

# Buscar clima
clima = requests.get('https://wttr.in/Sao+Paulo?format=3').text

# Buscar agenda Google
events_result = service.events().list(
    calendarId='primary', timeMin=now.isoformat() + 'Z',
    timeMax=(now.replace(hour=23, minute=59, second=59)).isoformat() + 'Z',
    singleEvents=True, orderBy='startTime'
).execute()

events = events_result.get('items', [])
agenda = ""
if not events:
    agenda = "Nenhum compromisso"
else:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        hora = start[11:16] if 'T' in start else start
        agenda += f"{hora} - {event['summary']}<br>"

# Teste de velocidade Internet
try:
    st = speedtest.Speedtest()
    st.get_best_server()
    down = int(st.download() / 1_000_000)
    up = int(st.upload() / 1_000_000)
    status = f"Velocidade: {down} ↓ / {up} ↑"
except:
    status = "Offline"

# Criar HTML
html = f'''
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
<div class="card">{'Feriado: ' + feriado_hoje if feriado_hoje else ''}</div>
<div class="card"><b>Agenda:</b><br>{agenda}</div>
<div class="card">{status}</div>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
