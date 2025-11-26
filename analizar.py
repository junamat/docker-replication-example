from datetime import datetime
import os
import numpy as np
import requests

WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 8)) # defaults
THRESHOLD = float(os.getenv("THRESHOLD", 9.233296204297654)) #defaults
MODEL_NAME = os.getenv("MODEL_NAME", "modelo")
SERVING_HOST = os.getenv("SERVING_HOST", "localhost")

def analizar(redis, request, socket):
    html = f"<h1> DETECTOR DE ANOMALÍAS </h1><b>Hostname</b>: {socket.gethostname()}<br/><hr> Ventana compuesta de las siguientes {WINDOW_SIZE} mediciones: <br/><br/>"

    lista = redis.ts().revrange('mediciones', '-', '+')
    m, t = zip(*lista)
    t = np.array(t)
    if len(t) < WINDOW_SIZE:
        html += "No hay suficientes mediciones"

    else:
        t = t[:WINDOW_SIZE]
        m = m[:WINDOW_SIZE]

        for fecha_hora, temperatura in zip(m, t):
            html += f'{temperatura}°C; Registrada a las {datetime.fromtimestamp(fecha_hora/1000)} <br />'

        t = t.reshape(1, WINDOW_SIZE, 1)
        payload = {
            "instances": t.tolist()
        }

        pred_url = f"http://{SERVING_HOST}:8501/v1/models/{MODEL_NAME}:predict"
        valor_predicho = requests.post(pred_url, json=payload).json()
        valor_predicho = np.array(valor_predicho["predictions"])

        if abs(float(request.args.get("dato")) - valor_predicho[:,0,0]) > THRESHOLD:
            html += f'<p style="color:red;">TRUE</p>La temperatura {request.args.get("dato")} es una anomalía.'
        else :
            html += f'<p style="color:green;">FALSE</p>La temperatura {request.args.get("dato")} no es una anomalía.'
    return html