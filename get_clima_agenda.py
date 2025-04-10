import os
import requests
import speedtest
from datetime import datetime, timedelta
import holidays
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ====================================
# 1. Configuração do Google Calendar via Service Account
# ====================================
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# Cria o arquivo service_account.json com o conteúdo do segredo (definido no GitHub Secrets)
credentials_json = os.environ['GOOGLE_CREDENTIALS']
with open('service_account.json', 'w', encoding='utf-8') as f:
    f.write(credentials_json)
creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

# ====================================
# 2. Dados Dinâmicos
# ====================================
now = datetime.now()
data_hoje = now.strftime("%d/%m/%Y")
hora_hoje = now.strftime("%H:%M")
dia_semana = now.strftime("%a.")

# Use seu ID do Google Calendar (geralmente seu email) 
calendar_id = "silasgubi@gmail.com"

# Feriados (Brasil, província SP)
br_holidays = holidays.Brazil(prov='SP')
feriado = br_holidays.get(now.date())
feriado_text = f"Feriado: {feriado}" if feriado else "Sem feriado"

# Clima em São Paulo (em Celsius)
try:
    clima = requests.get('https://wttr.in/Sao+Paulo?format=%C+%t&m').text
except Exception:
    clima = "Clima indisponível"

# Agenda do Google Calendar (eventos de hoje até o final do dia)
time_min = now.isoformat() + 'Z'
end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
time_max = end_of_day.isoformat() + 'Z'
events_result = service.events().list(
    calendarId=calendar_id, timeMin=time_min,
    timeMax=time_max, singleEvents=True, orderBy='startTime'
).execute()
events = events_result.get('items', [])
if not events:
    agenda_text = "Nenhum compromisso"
else:
    agenda_lines = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start:
            event_time = start.split("T")[1][:5]
        else:
            event_time = start
        summary = event.get('summary', 'Sem título')
        agenda_lines.append(f"{event_time} - {summary}")
    agenda_text = "<br>".join(agenda_lines)

# Teste de velocidade da Internet com speedtest-cli
try:
    st = speedtest.Speedtest()
    st.get_best_server()
    down = int(st.download() / 1_000_000)
    up = int(st.upload() / 1_000_000)
    internet_text = f"Velocidade: {down} ↓ / {up} ↑"
except Exception:
    internet_text = "Velocidade: Offline"

# ====================================
# 3. Gerar HTML com Layout Flat, Dark (modo terminal) e Botões Separados
# ====================================
# Para cada dispositivo, há dois botões: um para ligar e outro para desligar.
# Os links foram atualizados com sua IFTTT key.
html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Quarto</title>
  <!-- Ícones locais serão carregados a partir da pasta assets/icones/ -->
  <style>
    body {{
      background-color: #000;
      color: #fff;
      font-family: 'Courier New', Courier, monospace;
      padding: 10px;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9em;
      padding: 5px 0;
    }}
    .container {{
      display: flex;
      flex-direction: column;
      gap: 20px;
      margin-top: 10px;
    }}
    h3 {{
      border-top: 1px solid #222;
      padding-top: 10px;
      opacity: 0.7;
      text-transform: uppercase;
      font-size: 1em;
      letter-spacing: 1px;
    }}
    .grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .btn {{
      background: #111;
      border: none;
      border-radius: 5px;
      width: 60px;
      height: 60px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.1s, background 0.2s;
    }}
    .btn:hover {{
      background: #222;
    }}
    .btn:active {{
      transform: scale(0.95);
    }}
    .btn img {{
      width: 30px;
      height: 30px;
      margin-bottom: 3px;
    }}
    .btn span {{
      font-size: 0.6em;
      opacity: 0.8;
    }}
    .info {{
      background: #111;
      padding: 10px;
      border-radius: 5px;
      margin-top: 10px;
    }}
  </style>
  <script>
    function chamarIFTTT(url) {{
      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, true);
      xhr.send();
    }}
  </script>
</head>
<body>
<header>
    <div style="opacity:0.7;">Quarto</div>
    <div style="opacity:0.7;">{dia_semana} {data_hoje}, {hora_hoje}</div>
</header>
<div class="container">
    <!-- Seção de Luzes -->
    <h3>Luzes</h3>
    <div class="grid">
      <!-- Luz do Quarto -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_luz_quarto/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Luz Quarto">
         <span>Quarto</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_quarto/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Luz Quarto">
         <span>Quarto</span>
      </button>
      <!-- Abajur 1 -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Abajur 1">
         <span>Abajur</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajur_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Abajur 1">
         <span>Abajur</span>
      </button>
      <!-- Abajur 2 -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Abajur 2">
         <span>Abajur</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajur_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Abajur 2">
         <span>Abajur</span>
      </button>
      <!-- Luz da Cama -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Cama">
         <span>Cama</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Cama">
         <span>Cama</span>
      </button>
    </div>
    <!-- Seção de Dispositivos -->
    <h3>Dispositivos</h3>
    <div class="grid">
      <!-- Ar-condicionado -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Ar">
         <span>Ar</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Ar">
         <span>Ar</span>
      </button>
      <!-- Projetor -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Projetor">
         <span>Projetor</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Projetor">
         <span>Projetor</span>
      </button>
      <!-- Tomada iPad -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="iPad">
         <span>iPad</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="iPad">
         <span>iPad</span>
      </button>
    </div>
    <!-- Seção de Cenas -->
    <h3>Cenas</h3>
    <div class="grid">
      <!-- Cena Luzes Vermelhas -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_vermelhas/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Vermelhas">
         <span>Vermelhas</span>
      </button>
      <!-- Cena Luzes Grafite -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_grafite/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/XXX.svg" alt="Grafite">
         <span>Grafite</span>
      </button>
    </div>
    <!-- Seção de Sistema -->
    <h3>Sistema</h3>
    <div class="info">
      <p>{clima}</p>
      <p>{agenda_text}</p>
      <p>{internet_text}</p>
      <p>{feriado_text}</p>
    </div>
</div>
<script>
function atualizarDataHora() {{
    var now = new Date();
    var options = {{ weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }};
    document.querySelector('header div:nth-child(2)').innerText = now.toLocaleDateString('pt-BR', options);
}}
atualizarDataHora();
setInterval(atualizarDataHora, 60000);
function chamarIFTTT(url) {{
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.send();
}}
</script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
