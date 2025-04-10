import os
import requests
import json
import speedtest
from datetime import datetime, timedelta
import holidays
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Definir os escopos da Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Cria o arquivo service_account.json utilizando o segredo do GitHub
# É importante que o segredo do GitHub chamado GOOGLE_CREDENTIALS contenha o conteúdo completo do JSON da Service Account
credentials_json = os.environ['GOOGLE_CREDENTIALS']
with open('service_account.json', 'w', encoding='utf-8') as f:
    f.write(credentials_json)

# Autentica usando a Service Account
creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

# Obtém a data e hora atual
now = datetime.now()
data_hoje = now.strftime("%d/%m/%Y")
hora_hoje = now.strftime("%H:%M:%S")
dia_semana = now.strftime("%A")

# Busca os feriados do Brasil com foco em São Paulo usando a biblioteca holidays
br_holidays = holidays.Brazil(prov='SP')
feriado_hoje = br_holidays.get(now.date())
if feriado_hoje:
    feriado_texto = f"Feriado: {feriado_hoje}"
else:
    feriado_texto = ""

# Buscar a previsão do tempo para São Paulo via wttr.in
try:
    clima = requests.get('https://wttr.in/Sao+Paulo?format=3').text.strip()
except Exception as e:
    clima = "Clima indisponível"

# Buscar os eventos do Google Calendar para hoje (do agora até o final do dia)
time_min = now.isoformat() + 'Z'
end_of_day = now.replace(hour=23, minute=59, second=59)
time_max = end_of_day.isoformat() + 'Z'
events_result = service.events().list(
    calendarId='primary', timeMin=time_min,
    timeMax=time_max, singleEvents=True, orderBy='startTime'
).execute()
events = events_result.get('items', [])
agenda = ""
if not events:
    agenda = "Nenhum compromisso"
else:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start:
            hora_evento = start.split('T')[1][:5]
        else:
            hora_evento = start
        agenda += f"{hora_evento} - {event.get('summary', 'Sem título')}<br>"

# Teste de velocidade de conexão com a internet utilizando speedtest-cli
try:
    st = speedtest.Speedtest()
    st.get_best_server()
    down = int(st.download() / 1_000_000)  # em Mbps
    up = int(st.upload() / 1_000_000)        # em Mbps
    status_internet = f"Velocidade: {down} ↓ / {up} ↑"
except Exception as e:
    status_internet = "Status Internet: Offline"

# Monta o conteúdo HTML do painel com layout super dark e ícones minimalistas
html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Quarto</title>
  <style>
    body {{
      background-color: #000;
      color: #fff;
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 0;
      padding: 20px;
    }}
    .header {{
      font-size: 3em;
      margin-bottom: 10px;
    }}
    .subheader {{
      font-size: 1.5em;
      margin-bottom: 20px;
    }}
    .card {{
      background: #121212;
      margin: 10px auto;
      padding: 20px;
      border-radius: 10px;
      width: 90%;
      max-width: 400px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }}
    .card h2 {{
      margin-top: 0;
    }}
    .icon {{
      font-size: 2em;
      vertical-align: middle;
      margin-right: 10px;
    }}
  </style>
</head>
<body>
  <div class="header">{hora_hoje}</div>
  <div class="subheader">{dia_semana}, {data_hoje}</div>
  <div class="card">
    <h2><span class="icon">☀️</span> Clima</h2>
    <p>{clima}</p>
  </div>
  <div class="card">
    <h2><span class="icon">📅</span> Agenda</h2>
    <p>{agenda}</p>
  </div>
  <div class="card">
    <h2><span class="icon">🎉</span> {feriado_texto}</h2>
  </div>
  <div class="card">
    <h2><span class="icon">📶</span> Internet</h2>
    <p>{status_internet}</p>
  </div>
</body>
</html>
"""

# Salva o HTML gerado no arquivo index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("index.html gerado com sucesso!")
