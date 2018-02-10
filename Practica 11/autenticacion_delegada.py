# -*- coding: utf-8 -*-

##
## Gestion de la Informacion en la Web
## Practica Autenticacion Delegada
## Grupo 04
## Marcos Robles Palencia y Alvaro de la Cruz Casado
## declaramos que esta solucion
## es fruto exclusivamente de nuestro trabajo personal. No hemos sido
## ayudados por ninguna otra persona ni hemos obtenido la solucion de
## fuentes externas, y tampoco hemos compartido nuestra solucion con
## nadie. Declaramos ademas que no hemos realizado de manera deshonesta
## ninguna otra actividad que pueda mejorar nuestros resultados
## ni perjudicar los resultados de los demas.
##

import bottle
from bottle import run, get, template, request
import requests
import time
import random
from urllib.parse import urlencode
from beaker.middleware import SessionMiddleware # pip install beaker


# Credenciales.
# https://developers.google.com/identity/protocols/OpenIDConnect#appsetup
# Copiar los valores adecuados.
CLIENT_ID     = ""
CLIENT_SECRET = ""
REDIRECT_URI  = "http://localhost:8080/token"

# Fichero de descubrimiento para obtener el 'authorization endpoint' y el
# 'token endpoint'
# https://developers.google.com/identity/protocols/OpenIDConnect#authenticatingtheuser
DISCOVERY_DOC = "https://accounts.google.com/.well-known/openid-configuration"


# Token validation endpoint para decodificar JWT
# https://developers.google.com/identity/protocols/OpenIDConnect#validatinganidtoken
TOKENINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v3/tokeninfo'


session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
} # Valores para la sesion

app = SessionMiddleware(bottle.app(), session_opts)
# Inicializamos la app

@get('/login_google')
def login_google():

   # Posibles valores para el token anti csrf
   alfabeto = "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", "1","2","3","4","5","6","7","8","9"

   # Tomamos un tamaño de token de 30 caracteres
   token = ""
   for i in range(0, 30):
       token += str(random.choice(alfabeto)) # Vamos rellenando el token

   # Obtenemos la sesion y guardamos el token en ella
   s = bottle.request.environ.get('beaker.session')
   s['token_csrf'] = token
   s.save()

   url = ""

   parametros = {"client_id" : CLIENT_ID, "response_type" : "code", "scope" : "openid email", "redirect_uri": REDIRECT_URI, "state": token}

   url += "https://accounts.google.com/o/oauth2/v2/auth"
   url += "?" # Hemos comprobado que añadiendolo directamente arriba no funciona la url
   url += urlencode(parametros) # Encodeamos los parametros


   return template("login.tpl", param = url)



@get('/token')
def token():

    code = request.query.code
    token = request.query.state

    # Obtenemos la sesion y vemos si coinciden los tokens anti csrf
    s = bottle.request.environ.get('beaker.session')
    if(str(s['token_csrf']) == str(token)):
        payload = {'code': code, 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'redirect_uri': REDIRECT_URI, 'grant_type': 'authorization_code'}
        # Hacemos peticion para obtener el json cifrado y firmado por Google
        r = requests.post("https://www.googleapis.com/oauth2/v4/token", data=payload)
        # En r tenemos ya el json

        payload = {'id_token': r.json()["id_token"]}
        # Obtenemos el json en claro
        p = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo', params=payload)

        # Hacemos varias comprobaciones sobre los datos obtenidos
        if(str(p.json()["iss"]) == "https://accounts.google.com" or str(p.json()["iss"]) == "accounts.google.com"):
            if(str(p.json()["aud"]) == CLIENT_ID ):
                if(int(p.json()["exp"]) > int(time.time())):
                    return template("bienvenida.tpl", param = str(p.json()["email"])) # Si todo hay ido bien, mensaje de bienvenida
                else:
                    return "<p>Ya ha expirado el id_token</p>"
            else:
                return "<p>No coincide el Client Id</p>"
        else:
            return "<p>No coincide el Issuer Id</p>"
    else:
        return "<p>No coincide el token anti CSRF</p>"


if __name__ == "__main__":
    # NO MODIFICAR LOS PARÁMETROS DE run()
    run(host='localhost',port=8080,debug=True, app = app)
