import os
import requests
import json
import speedtest
from datetime import datetime, timedelta
import holidays
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ===========================
# 1. Configuração do Google Calendar via Service Account
# ---------------------------
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# Cria o arquivo service_account.json com o conteúdo do segredo (já definido no GitHub Secrets)
credentials_json = os.environ['GOOGLE_CREDENTIALS']
with open('service_account.json', 'w', encoding='utf-8') as f:
    f.write(credentials_json)
creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

# ===========================
# 2. Dados dinâmicos: data, feriado, clima, agenda, e internet
# ---------------------------
now = datetime.now()
data_hoje = now.strftime("%d/%m/%Y")
hora_hoje = now.strftime("%H:%M")
dia_semana = now.strftime("%A")

# Feriados (Brasil com província SP)
br_holidays = holidays.Brazil(prov='SP')
feriado = br_holidays.get(now.date())
if feriado:
    feriado_text = f"Feriado: {feriado}"
else:
    feriado_text = "Sem feriado"

# Clima: usando wttr.in (em formato simples)
try:
    clima = requests.get('https://wttr.in/Sao+Paulo?format=3').text
except Exception as e:
    clima = "Clima indisponível"

# Agenda: eventos do Google Calendar para hoje (até o final do dia)
time_min = now.isoformat() + 'Z'
end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
time_max = end_of_day.isoformat() + 'Z'
events_result = service.events().list(
    calendarId='primary', timeMin=time_min,
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
except Exception as e:
    internet_text = "Velocidade: Offline"

# ===========================
# 3. Template HTML do Painel com Layout Flat, Dark e Botões em Seções
# ---------------------------
html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Quarto</title>
  <!-- Ícones minimalistas via FontAwesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    * {{
      box-sizing: border-box;
    }}
    body {{
      background-color: #000;
      color: #fff;
      margin: 0;
      padding: 10px;
      font-family: 'Courier New', Courier, monospace;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9em;
      padding: 5px 0;
    }}
    header .title {{
      opacity: 0.7;
    }}
    header .datetime {{
      opacity: 0.8;
    }}
    .container {{
      display: flex;
      flex-direction: column;
      gap: 20px;
      margin-top: 10px;
    }}
    .section {{
      border-top: 1px solid #222;
      padding-top: 10px;
    }}
    .section h3 {{
      font-size: 1em;
      margin: 5px 0 10px;
      text-transform: uppercase;
      opacity: 0.7;
      letter-spacing: 1px;
    }}
    .button-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    button {{
      background: #111;
      border: none;
      color: #fff;
      padding: 15px;
      font-size: 1.5em;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.1s, background-color 0.2s;
    }}
    button:hover {{
      background: #222;
    }}
    button:active {{
      transform: scale(0.95);
    }}
    .info-card {{
      background: #111;
      padding: 10px;
      border-radius: 5px;
      font-size: 0.9em;
    }}
    .info-card p {{
      margin: 5px 0;
    }}
  </style>
</head>
<body>
  <header>
    <div class="title">Quarto</div>
    <div class="datetime" id="datetime">{dia_semana}, {data_hoje} {hora_hoje}</div>
  </header>
  <div class="container">
    <!-- Seção de Luzes -->
    <div class="section" id="luzes">
      <h3>Luzes</h3>
      <div class="button-row">
        <!-- Luz do Quarto -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_luz_quarto/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-lightbulb"></i>
        </button>
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_quarto/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-lightbulb"></i>
        </button>
        <!-- Abajur 1 -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-bed"></i>
        </button>
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajar_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-bed"></i>
        </button>
        <!-- Abajur 2 -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-bed"></i>
        </button>
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajar_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-bed"></i>
        </button>
        <!-- Luz da Cama -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-lightbulb"></i>
        </button>
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-lightbulb"></i>
        </button>
      </div>
    </div>

    <!-- Seção de Dispositivos -->
    <div class="section" id="dispositivos">
      <h3>Dispositivos</h3>
      <div class="button-row">
        <!-- Tomada iPad -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-plug"></i>
        </button>
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-plug"></i>
        </button>
        <!-- Projetor -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-video"></i>
        </button>
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-video"></i>
        </button>
        <!-- Ar-condicionado -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-snowflake"></i>
        </button>
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-snowflake"></i>
        </button>
      </div>
    </div>

    <!-- Seção de Cenas -->
    <div class="section" id="cenas">
      <h3>Cenas</h3>
      <div class="button-row">
        <!-- Cena Luzes Vermelhas -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_vermelhas/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-heart"></i>
        </button>
        <!-- Cena Luzes Grafite -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_grafite/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-square"></i>
        </button>
        <!-- Cena Aconchegante -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_aconchegante/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-home"></i>
        </button>
        <!-- Cena Luzes Vermelhas Banheiro -->
        <button onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_vermelhas_banheiro/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-bath"></i>
        </button>
      </div>
    </div>

    <!-- Seção de Sistema -->
    <div class="section" id="sistema">
      <h3>Sistema</h3>
      <div class="info-card" id="infoCard">
        <p id="infoClima">{clima}</p>
        <p id="infoAgenda">{agenda_text}</p>
        <p id="infoInternet">{internet_text}</p>
        <p id="infoFeriado">{feriado_text}</p>
      </div>
    </div>
  </div>

  <script>
    function chamarIFTTT(url) {{
      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, true);
      xhr.send();
    }}
    function atualizarDataHora() {{
      var now = new Date();
      var options = {{ weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }};
      document.getElementById('datetime').innerText = now.toLocaleDateString('pt-BR', options);
    }}
    atualizarDataHora();
    setInterval(atualizarDataHora, 60000);
  </script>
</body>
</html>
"""

# ===========================
# 4. Salvar o HTML no arquivo index.html
# ---------------------------
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
