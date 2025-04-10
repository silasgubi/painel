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

# ID do seu Google Calendar
calendar_id = "silasgubi@gmail.com"

# Biblioteca de feriados no Brasil, estado SP
br_holidays = holidays.Brazil(prov='SP')
feriado_hoje = br_holidays.get(now.date())

# Verifica se HOJE é feriado
if feriado_hoje:
    feriado_text = f"Hoje é feriado: {feriado_hoje}"
else:
    # Se não é feriado hoje, buscar o próximo feriado no ano
    proximos = sorted(d for d in br_holidays if d > now.date() and d.year == now.year)
    if proximos:
        proximo_feriado_data = proximos[0]
        proximo_feriado_nome = br_holidays.get(proximo_feriado_data)
        feriado_text = f"Próximo feriado: {proximo_feriado_nome} em {proximo_feriado_data.strftime('%d/%m/%Y')}"
    else:
        feriado_text = "Não há mais feriados este ano"

# Clima em São Paulo + ícone + descrição PT + °C
try:
    # São Paulo: %c -> ícone, %C -> texto, %t -> temperatura (°C com &m)
    clima = requests.get("https://wttr.in/Sao+Paulo?format=São+Paulo:+%c+%C+%t&lang=pt&m").text
except Exception:
    clima = "Clima indisponível"

# Agenda do Google Calendar: eventos de hoje até 23h59
time_min = now.isoformat() + 'Z'
time_max = datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + 'Z'
events_result = service.events().list(
    calendarId=calendar_id,
    timeMin=time_min,
    timeMax=time_max,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

if not events:
    agenda_text = "Compromissos: Nenhum"
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
    # Exibir com "Compromissos:" antes
    agenda_text = "Compromissos:<br>" + "<br>".join(agenda_lines)

# Teste de velocidade da Internet
try:
    st = speedtest.Speedtest()
    st.get_best_server()
    down = int(st.download() / 1_000_000)
    up = int(st.upload() / 1_000_000)
    internet_text = f"Velocidade: {down} ↓ / {up} ↑"
except Exception:
    internet_text = "Velocidade: Offline"

# ====================================
# 3. Gerar HTML - Layout Terminal + Ícones Locais
# ====================================
html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Quarto</title>
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
    /* Deixa ícones mais claros caso sejam pretos */
    .btn img {{
      width: 30px;
      height: 30px;
      margin-bottom: 3px;
      filter: invert(100%) brightness(150%);
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

    function atualizarDataHora() {{
      var now = new Date();
      var options = {{ weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }};
      document.querySelector('header div:nth-child(2)').innerText = now.toLocaleDateString('pt-BR', options);
    }}
    setInterval(atualizarDataHora, 60000);
    atualizarDataHora();
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
         <img src="assets/icones/luz_on.svg" alt="Luz Quarto">
         <span>Quarto</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_quarto/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/luz_off.svg" alt="Luz Quarto">
         <span>Quarto</span>
      </button>

      <!-- Abajur 1 -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/abajur_on.svg" alt="Abajur 1">
         <span>Abajur</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajur_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/abajur_off.svg" alt="Abajur 1">
         <span>Abajur</span>
      </button>

      <!-- Abajur 2 -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/abajur_on.svg" alt="Abajur 2">
         <span>Abajur</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajur_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/abajur_off.svg" alt="Abajur 2">
         <span>Abajur</span>
      </button>

      <!-- Luz da Cama -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/cama_on.svg" alt="Cama">
         <span>Cama</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/cama_off.svg" alt="Cama">
         <span>Cama</span>
      </button>
    </div>

    <!-- Seção de Dispositivos -->
    <h3>Dispositivos</h3>
    <div class="grid">
      <!-- Ar-condicionado -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/ar_on.svg" alt="Ar">
         <span>Ar</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/ar_off.svg" alt="Ar">
         <span>Ar</span>
      </button>

      <!-- Projetor -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/projetor_on.svg" alt="Projetor">
         <span>Projetor</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/projetor_off.svg" alt="Projetor">
         <span>Projetor</span>
      </button>

      <!-- Tomada iPad -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/usb_on.svg" alt="iPad">
         <span>iPad</span>
      </button>
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/usb_off.svg" alt="iPad">
         <span>iPad</span>
      </button>
    </div>

    <!-- Seção de Cenas -->
    <h3>Cenas</h3>
    <div class="grid">
      <!-- Cena Luzes Vermelhas -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_vermelhas/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/luzes_vermelhas_on.svg" alt="Vermelhas">
         <span>Vermelhas</span>
      </button>
      <!-- Cena Luzes Grafite -->
      <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_grafite/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
         <img src="assets/icones/grafite_on.svg" alt="Grafite">
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
</body>
</html>
"""

# ====================================
# 4. Salvar o HTML
# ====================================
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
