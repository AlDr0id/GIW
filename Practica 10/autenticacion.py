# -*- coding: utf-8 -*-

##
## Gestion de la Informacion en la Web
## Practica Autenticacion TOTP
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


from bottle import run, post, request, get, template
from pymongo import MongoClient
import random
import onetimepass as otp
from passlib.hash import argon2 # Requiere de los modulos passlib y argon2_cffi
# Para su instalacion: sudo pip3.6 install passlib && sudo pip3.6 install argon2_cffi (Python 3.6 en nuestro caso)

mongoclient = MongoClient()
db = mongoclient.giw # Accedemos a la base de datos
col = db.users # Accedemos a a la coleccion


##############
# APARTADO 1 #
##############

#
# Las contraseñas se almacenan en el campo "password" hasheadas con Argon2,
# una función de derivación de claves (para así hacer que sea extremadamente complicado reversear el hash) ganadora de la Password Hashing Competition.
# Ejemplo: $argon2i$v=19$m=512,t=2,p=2$aI2R0hpDyLm3ltLa+1/rvQ$LqPKjd6n8yniKtAithoR7A
# Se almacenan: la función empleada, la versión de Argon2, el coste en memoria de la variable,
# el coste en iteraciones lineales, el parámetro de paralelización, la sal y la clave derivada de la función
# La seguridad radica en la función de derivación de claves empleada, que hace impracticable obtener en texto plano las contraseñas
#



@post('/signup')
def signup():

    # Lectura de datos
    nickname = request.forms.get('nickname')
    name = request.forms.get('name')
    country = request.forms.get('country')
    email = request.forms.get('email')
    password = request.forms.get('password')
    password2 = request.forms.get('password2')

    # Comprobacion de contraseñas
    if(str(password) != str(password2)):
        return "<p>Las contraseñas no coinciden</p>"

    # Busqueda del usuario
    encontrado = col.find({"_id": nickname})
    if(encontrado.count() > 0): # Si existe
        return "<p>El alias de usuario ya existe</p>"
    else:
        passwordHashed = argon2.using(rounds=1000).hash(password) # Hasheado de la contraseña
        col.insert({"_id": nickname, "name": name, "country": country, "email": email, "password": passwordHashed})
        return template("signup.tpl", param = name)


@post('/change_password')
def change_password():

    # Lectura de datos
    nickname = request.forms.get('nickname')
    old_password = request.forms.get('old_password')
    new_password = request.forms.get('new_password')

    # Busqueda del usuario
    res = col.find({"_id" : nickname})

    if(res.count() > 0):
        old_passwordHashed = res[0]["password"]
        if(argon2.verify(old_password, old_passwordHashed)):
            # Actualizar contraseña
            new_passwordHashed = argon2.using(rounds=1000).hash(new_password)
            col.update({"_id": nickname}, {"$set": {"password": new_passwordHashed}})
            return template("change_pass.tpl", param = nickname)
        else: # Si no corresponde la contraseña
            return "<p>Usuario o contraseña incorrectos</p>"
    else: # Si no existe
        return "<p>Usuario o contraseña incorrectos</p>"



@post('/login')
def login():

    # Lectura de datos
    nickname = request.forms.get('nickname')
    password = request.forms.get('password')

    # Busqueda del usuario
    res = col.find({"_id" : nickname})

    if(res.count() > 0):
        passwordHashed = res[0]["password"]
        if(argon2.verify(password, passwordHashed)):
            return template("login.tpl", param = res[0])
        else: # Si no corresponde la contraseña
            return "<p>Usuario o contraseña incorrectos</p>"
    else: # Si no existe
        return "<p>Usuario o contraseña incorrectos</p>"


##############
# APARTADO 2 #
##############

#
# Para generar la semilla aleatoria definimos un alfabeto con los caracteres alfanuméricos disponibles en base 32
# Hacemos un bucle de 16 iteraciones (hemos establecido un secreto de tamaño 16) y llamamos a random para elegir un caracter cada vez
#
# La url se forma con el tipo (en este caso totp), la etiqueta (en este caso formada por un prefijo que distingue en este caso la asignatura GIW,
# y la cuenta a la que está asociada, en este caso un email ucm inventado del grupo), y los parámetros, que en este caso son el secreto
# y el nombre de usuario de la cuenta a crear. Se pueden añadir otros parámetros opcionales adicionales que en este caso no hemos
# considerado necesarios pero que en una implementación a mayor escala podrían ser útiles
#
#
# El código QR se genera formando una url según la información obtenida en http://goqr.me/api/ a la cual se llama
# pasando por parámetro los datos que queramos introducir en el QR (en este caso la url de Google Authenticator)
# así como el tamaño de imagen que queramos crear
#


@post('/signup_totp')
def signup_totp():

    # Tomamos un tamaño de secreto de 16 caracteres alfanumericos en base 32
    alfabeto = "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","2","3","4","5","6","7"

    secreto = ""
    for i in range(0, 16):
        secreto += str(random.choice(alfabeto)) # Vamos rellenando la semilla

    # Lectura de datos
    nickname = request.forms.get('nickname')
    name = request.forms.get('name')
    country = request.forms.get('country')
    email = request.forms.get('email')
    password = request.forms.get('password')
    password2 = request.forms.get('password2')

    # Comprobacion de contraseñas
    if(str(password) != str(password2)):
        return "<p>Las contraseñas no coinciden</p>"

    # Busqueda del usuario
    res = col.find({"_id": nickname})
    if(res.count() > 0): # Si existe
        return "<p>El alias de usuario ya existe</p>"
    else:
        passwordHashed = argon2.using(rounds=1000).hash(password)
        col.insert({"_id": nickname, "name": name, "country": country, "email": email, "password": passwordHashed, "secretTOTP": secreto})
        url = "otpauth://totp/GIW:grupo04@ucm.es?secret=" + str(secreto) + "&issuer=" + str(nickname) # Formamos la url de Google Authenticator
        qr = "https://api.qrserver.com/v1/create-qr-code/?data=" + str(url) + "&amp;size=100x100" # Formamos la url del QR
        return template("signupTOTP.tpl", user = nickname, qr = qr, semilla = secreto)


@post('/login_totp')
def login_totp():

    # Lectura de datos
    nickname = request.forms.get('nickname')
    password = request.forms.get('password')
    totpIntroducido = request.forms.get('totp')

    # Busqueda del usuario
    res = col.find({"_id" : nickname})

    if(res.count() > 0):
        passwordHashed = res[0]["password"]
        if(argon2.verify(password, passwordHashed)):
            # totp = otp.get_totp(res[0]["secretTOTP"]) # Otra forma de comprobar el codigo totp
            if (otp.valid_totp(totpIntroducido, res[0]["secretTOTP"])):
            # if(str(totp) == str(totpIntroducido)): # Otra forma de comprobar el codigo totp
                return template("login.tpl", param = res[0])
            else: # Si no es valido el codigo totp
                return "<p>Usuario o contraseña incorrectos</p>"
        else: # Si no coinciden las contraseñas
            return "<p>Usuario o contraseña incorrectos</p>"
    else: # Si no existe el usuario
        return "<p>Usuario o contraseña incorrectos</p>"


if __name__ == "__main__":
    # NO MODIFICAR LOS PARÁMETROS DE run()
    run(host='localhost',port=8080,debug=True)
