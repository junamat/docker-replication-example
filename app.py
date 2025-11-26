from datetime import datetime

from flask import Flask, request
from redis import Redis, RedisError
import os
import socket
from analizar import analizar


# Connect to Redis
REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
print("REDIS_HOST: "+REDIS_HOST)
redis = Redis(host=REDIS_HOST, db=0, socket_connect_timeout=2, socket_timeout=2)
try: redis.ts().create("mediciones")
except:
    print("redis.ts() not created")

app = Flask(__name__)

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)

@app.route("/nuevo")
def nuevo():
    fecha_hora = datetime.now()
    try:
        d = float(request.args.get("dato"))
        redis.ts().add("mediciones",  "*", d)
        html = "<b>Hostname</b>: {host}<br/><hr><h3>Añadida temperatura {dato} a las {timestamp}!</h3>"
    except RedisError:
        html = "<b>No se ha podido acceder a la TimeSeries por error de Redis.</b>"
    return html.format(dato=d, timestamp=fecha_hora, host = socket.gethostname())
@app.route("/listar")
def listar():
    try:
        lista = redis.ts().revrange('mediciones', '-', '+')
        html = f"<b>Hostname</b>: {socket.gethostname()}<br/><hr><h1>Temperaturas</h1>\n"
        for (timestamp, temp) in lista:
            html += f'{temp}°C; Registrada a las {datetime.fromtimestamp(timestamp/1000)} <br />'
    except RedisError:
        html = "<b>No se ha podido acceder a la TimeSeries por error de Redis.</b>"
    return html

@app.route("/detectar")
def detectar():
    return analizar(redis, request, socket)


if __name__ == "__main__":
    PORT = os.getenv('PORT', 80)
    print("PORT: "+str(PORT))
    app.run(host='0.0.0.0', port=PORT)
