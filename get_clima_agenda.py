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
dia_semana = now.strftime("%A")

# Feriados (Brasil, província SP)
br_holidays = holidays.Brazil(prov='SP')
feriado = br_holidays.get(now.date())
feriado_text = f"Feriado: {feriado}" if feriado else "Sem feriado"

# Clima (usando wttr.in em formato simples)
try:
    clima = requests.get('https://wttr.in/Sao+Paulo?format=3&m').text
except Exception:
    clima = "Clima indisponível"

# Agenda do Google Calendar (eventos de hoje até o final do dia)
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
except Exception:
    internet_text = "Velocidade: Offline"

# ====================================
# 3. Gerar HTML com Layout Flat, Dark (modo terminal) e Botões Separados
# ====================================
# Cada dispositivo terá dois botões: um para ligar e outro para desligar.
# Os links já foram corrigidos conforme solicitado.
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
    .btn {{
      background: #111;
      border: none;
      color: #fff;
      padding: 10px;
      font-size: 1.2em;
      border-radius: 5px;
      width: 60px;
      height: 60px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.1s, background-color 0.2s;
    }}
    .btn:hover {{
      background: #222;
    }}
    .btn:active {{
      transform: scale(0.95);
    }}
    .btn i {{
      margin-bottom: 5px;
    }}
    .btn span {{
      font-size: 0.6em;
      opacity: 0.8;
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
        <!-- Luz do Quarto: ligar e desligar -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_luz_quarto/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-lightbulb"></i>
          <span>Liga</span>
        </button>
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_quarto/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-lightbulb"></i>
          <span>Desliga</span>
        </button>
        <!-- Abajur 1 -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-bed"></i>
          <span>Liga</span>
        </button>
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajur_1/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-bed"></i>
          <span>Desliga</span>
        </button>
        <!-- Abajur 2 -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_abajur_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-bed"></i>
          <span>Liga</span>
        </button>
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_abajur_2/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-bed"></i>
          <span>Desliga</span>
        </button>
        <!-- Luz da Cama -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-lightbulb"></i>
          <span>Liga</span>
        </button>
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_luz_cama/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-lightbulb"></i>
          <span>Desliga</span>
        </button>
      </div>
    </div>

    <!-- Seção de Dispositivos -->
    <div class="section" id="dispositivos">
      <h3>Dispositivos</h3>
      <div class="button-row">
        <!-- Ar-condicionado -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-snowflake"></i>
          <span>Liga</span>
        </button>
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_ar/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-snowflake"></i>
          <span>Desliga</span>
        </button>
        <!-- Tomada iPad -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-plug"></i>
          <span>Liga</span>
        </button>
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_tomada_ipad/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-plug"></i>
          <span>Desliga</span>
        </button>
        <!-- Projetor -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/ligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-video"></i>
          <span>Liga</span>
        </button>
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/desligar_projetor/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="far fa-video"></i>
          <span>Desliga</span>
        </button>
      </div>
    </div>

    <!-- Seção de Cenas -->
    <div class="section" id="cenas">
      <h3>Cenas</h3>
      <div class="button-row">
        <!-- Cena Luzes Vermelhas -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_vermelhas/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-heart"></i>
          <span>Vermelhas</span>
        </button>
        <!-- Cena Luzes Grafite -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_grafite/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-square"></i>
          <span>Grafite</span>
        </button>
        <!-- Cena Aconchegante -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_aconchegante/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-home"></i>
          <span>Aconchegante</span>
        </button>
        <!-- Cena Luzes Vermelhas Banheiro -->
        <button class="btn" onclick="chamarIFTTT('https://maker.ifttt.com/trigger/cena_luzes_vermelhas_banheiro/with/key/dyC3gXsJqHMp5uYOPt-s2W')">
          <i class="fas fa-bath"></i>
          <span>Banheiro</span>
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
    // Função para chamar os IFTTT webhooks
    function chamarIFTTT(url) {{
      var xhr = new XMLHttpRequest();
      xhr.open("GET", url, true);
      xhr.send();
    }}

    // Atualiza a data e hora no header a cada minuto
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

# ====================================
# 4. Salvar o HTML no arquivo index.html
# ====================================
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
