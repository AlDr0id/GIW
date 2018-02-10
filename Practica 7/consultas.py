# -*- coding: utf-8 -*-

##
## Gestion de la Informacion en la Web
## Practica Consultas MongoDB
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

from pymongo import MongoClient
from bottle import get, run, request, template
import re
mongoclient = MongoClient()

@get('/find_users')
def find_users():
    db = mongoclient.giw # Accedemos a la base de datos
    col = db.usuarios # Accedemos a a la coleccion
    query = dict()
    for elem in request.query:
        if str(elem) == "name": # Si el elemento es name, agregamos la consulta sobre el nombre
            query["name"] = request.query.name
        elif str(elem) == "surname": # Si el elemento es surname, agregamos la consulta sobre el apellido
            query["surname"] = request.query.surname
        elif str(elem) == "birthdate": # Si el elemento es birthdate, agregamos la consulta sobre el cumpleaños
            query["birthdate"] = request.query.birthdate
        else:
            return template("ej1Error.tpl", param = str(elem)) # En caso de error, un template personalizado

    resultado = col.find(query)
    # http://localhost:8080/find_users?name=Luz
    # http://localhost:8080/find_users?name=Luz&surname=Romero
    # http://localhost:8080/find_users?name=Luz&&surname=Romero&birthdate=2006-08-14
    return template("ej1.tpl", param = resultado, num = resultado.count())

@get('/find_email_birthdate')
def email_birthdate():
    db = mongoclient.giw # Accedemos a la base de datos
    col = db.usuarios # Accedemos a a la coleccion
    frm = request.query["from"] # Cogemos el parametro from
    to = request.query.to # Cogemos el parametro to
    resultado = col.find({"$and": [{"birthdate":{"$gte":frm, "$lte":to}}]}, {"_id":1,"birthdate":1,"email":1})
    return template("ej2.tpl", param = resultado, num = resultado.count())
    # http://localhost:8080/find_email_birthdate?from=1973-01-01&to=1990-12-31


@get('/find_country_likes_limit_sorted')
def find_country_likes_limit_sorted():
    db = mongoclient.giw # Accedemos a la base de datos
    col = db.usuarios # Accedemos a a la coleccion
    country = request.query.country # Cogemos el parametro country
    tmp = request.query.likes # Cogemos el parametro likes
    likes = tmp.split(',') # Parseamos
    limit = int(request.query.limit)  # Cogemos el parametro limit
    orden = request.query.ord # Cogemos el parametro ord
    if str(orden) == "asc": # Vemos que orden hay que seguir
        orden = 1
    else:
        orden = -1
    # Hemos seguido el orden en el cual ordenamos tal cual es la fecha de nacimiento, tomada como string,
    # no teniendo en cuenta la edad, que en cuyo caso seria ordenado al reves, cuanto menor fuera la fecha
    # mas mayor seria la persona

    resultado = col.find({"$and": [{"address.country": {"$eq": country}}, {"likes": {"$all": likes}}]}).sort("birthdate", orden).limit(limit)
    # http://localhost:8080/find_country_likes_limit_sorted?country=Irlanda&likes=movies,animals&limit=4&ord=asc
    if resultado.count() < limit: # Si hay menos resultados que el limite, el numero de resultados de encima de la tabla sera ese
        numero = resultado.count()
    else: # Si hay un numero igual o superior, el numero sera el limite
        numero = limit
    return template("ej3.tpl", param = resultado, num = numero)

@get('/find_birth_month')
def find_birth_month():
    db = mongoclient.giw # Accedemos a la base de datos
    col = db.usuarios # Accedemos a a la coleccion
    month = str(request.query.month)
    meses = {
        "enero" : "01",
        "febrero" : "02",
        "marzo" : "03",
        "abril" : "04",
        "mayo" : "05",
        "junio" : "06",
        "julio" : "07",
        "agosto" : "08",
        "septiembre" : "09",
        "octubre" : "10",
        "noviembre" : "11",
        "diciembre" : "12"
    } # Diccionario para cambiar el string de mes obtenido a lo que aparece en la base de datos

    regex = "-" + meses[month] + "-" # Para la busqueda, el mes va siempre entre dos guiones, asi que usamos una expresion regular
    resultado = col.find({"birthdate" : {"$regex": regex}}).sort("birthdate", 1)

  # http://localhost:8080/find_birth_month?month=abril
    return template("ej4.tpl", param = resultado, num = resultado.count())

@get('/find_likes_not_ending')
def find_likes_not_ending():
    db = mongoclient.giw # Accedemos a la base de datos
    col = db.usuarios # Accedemos a a la coleccion
    ending = request.query.ending # Cogemos el parametro ending
    resultado = col.find({"likes":{"$not": re.compile(ending+"$", re.IGNORECASE)}}) # Tenemos en cuenta que no sea case sensitive
  # http://localhost:8080/find_likes_not_ending?ending=s
    return template("ej5.tpl", param = resultado, num = resultado.count())

@get('/find_leap_year')
def find_leap_year():
  # http://localhost:8080/find_leap_year?exp=20
    db = mongoclient.giw # Accedemos a la base de datos
    col = db.usuarios # Accedemos a a la coleccion
    exp = request.query.exp # Cogemos el parametro exp

    resultado = []
    # bisiesto:
    # divisible entre 4 && ((no divisible entre 100) || (divisible entre 400))
    tmp = col.find({"credit_card.expire.year": {"$eq": exp}}) # Hacemos una primera criba obteniendo los que cumplen la condicion de la tarjeta de credito
    for elem in tmp:
        year = int(elem["birthdate"][0:4]) # Obtenemos el año de nacimiento
        if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            resultado.append(elem) # Si es bisiesto, se añade a la lista de usuarios a mostrar

    return template("ej6.tpl", param = resultado, num = len(resultado))


###################################
# NO MODIFICAR LA LLAMADA INICIAL #
###################################
if __name__ == "__main__":
    run(host='localhost',port=8080,debug=True)
