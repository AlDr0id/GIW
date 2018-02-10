# -*- coding: utf-8 -*-

##
## Gestion de la Informacion en la Web
## Practica Aggregation Pipelines
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


mongoclient = MongoClient()
db = mongoclient["giw"]
cUsuarios = db.usuarios
cPedidos = db.pedidos

@get('/top_countries')
# http://localhost:8080/top_countries?n=3
def agg1():

    # Recibe un parametro n, y genera una pagina HTML mostrando los n paıses
    # con mas numero de usuarios junto a dicho numero de usuarios. En caso de
    # empate a usuarios, los paıses se ordenan alfabeticamente. Lo resultados se deben
    # mostrar en una tabla con 2 columnas: la primera contendra el nombre del paıs
    # y la segunda el numero de usuarios. Justo debajo de la tabla debe aparecer un
    # mensaje indicando el numero de resultados devueltos por esta consulta.

    num = int(request.query["n"]) # Leemos el valor del parametro

    resultado = cUsuarios.aggregate([
        {"$group": {"_id": "$pais", "totalPersonas": {"$sum": 1}}}, # Agrupamos por nombre de pais y sumamos 1 por cada usuario que aparezca
        {"$sort": {"totalPersonas": -1, "_id": 1}}, # De mayor a menor numero de usuarios, y alfabeticamente
        {"$limit": num}]) # Numero max de resultados

    return template("ej1.tpl", param = resultado)


@get('/products')
# http://localhost:8080/products?min=2.34
def agg2():

    # Recibe un parametro min representando un precio mınimo. Genera una pagina
    # HTML que muestra, por cada producto cuyo precio es igual o superior a
    # min, el numero de unidades vendidas entre todos los pedidos junto con su precio
    # unitario (que sera el mismo en todos los pedidos en los que aparezca). Los
    # resultados se muestran en una tabla de 3 columnas: nombre de producto, numero
    # de unidades vendidas y finalmente precio unitario. Justo debajo de la tabla
    # debe aparecer un mensaje indicando el numero de resultados devueltos por esta
    # consulta.

    precioMin = float(request.query["min"]) # Leemos el valor del parametro

    resultado = cPedidos.aggregate([
        {"$unwind": "$lineas"}, # Separamos las lineas
        {"$match": {"lineas.precio": {"$gte": precioMin}}}, # Filtramos por las que el precio sea menor o igual al parametro
        {"$group": {"_id": "$lineas.nombre", "uds": {"$sum": "$lineas.cantidad"}, "precioUnitario": {"$max": "$lineas.precio"}}}])
        # Aunque se especifica que el precio sera el mismo en todos los pedidos en los que aparezca un producto, por si en alguno
        # hubiera algun error usamos max para tener siempre el de mayor valor en beneficio de la hipotetica empresa

    return template("ej2.tpl", param = resultado)

@get('/age_range')
# http://localhost:8080/age_range?min=80
def agg3():

    # Agrupar por país, los que tengan mas de "min" usuarios.
    # Mostrar diferencia entre edad max y min.
    # Ordenados de mayor a menor, y en empate por nombre del país
    # Mostrar dos columnas: nombre país y rango edades. Debajo numero de resultados

    minimo = int(request.query["min"]) # Leemos el valor del parametro

    resultado = cUsuarios.aggregate([
        {"$group": {"_id": "$pais", "edadMax": {"$max": "$edad"}, "edadMin": {"$min": "$edad"}, "totalPersonas": {"$sum": 1}}},
        # Agrupamos por pais, obtenemos la edad maxima, la minima, y por cada resultado sumamos 1 para el total de personas
        {"$match" : {"totalPersonas":{"$gt":minimo}}}, # Filtramos por los que superen el numero minimo del parametro
        {"$project": {"diferencia" : { "$subtract" : ["$edadMax",  "$edadMin"]}}}, # Obtenemos el rango de edades
        {"$sort": {"diferencia": -1, "_id": 1}}]) # De mayor a menor rango, y alfabeticamente los paises

    return template("ej3.tpl", param = resultado)


@get('/avg_lines')
# http://localhost:8080/avg_lines
def agg4():

    # Genera una pagina HTML que muestra, por cada pais, el numero promedio
    # de lineas que tienen los pedidos realizados por usuarios de dicho pais. Los
    # resultados se muestran en una tabla de 2 columnas: nombre de pais y numero
    # de lineas promedio de sus pedidos. Bajo de la tabla debe aparecer un mensaje
    # indicando el numero de resultados devueltos por esta consulta.

    resultado = cPedidos.aggregate([
        {"$unwind": "$lineas"}, # Separamos las lineas
        {"$group": {"_id": "$_id", "numLineas": {"$sum": 1}, "cliente": {"$first": "$cliente"}}},
        # Agrupamos por pedido, contamos las lineas y obtenemos el cliente
        {"$lookup": { "from": "usuarios", "localField": "cliente", "foreignField": "_id", "as": "usuario"}},
        # Añadimos los usuarios
        {"$group": {"_id": "$usuario.pais", "media": {"$avg": "$numLineas"}}}])
        # Agrupamos por usuario y obtenemos el numero de lineas promedio

    return template("ej4.tpl", param = resultado)

@get('/total_country')
# http://localhost:8080/total_country?c=Alemania
def agg5():

    # Recibe como parametro c el nombre de un paıs, y calcula el total de euros
    # gastado en todos los pedidos realizados por usuarios de dicho paıs. Los resultados
    # se muestran en una tabla de 2 columnas: nombre de paıs y total de euros
    # gastados. Se debe mostrar el numero de resultados devueltos por esta consulta
    # bajo la tabla.

    pais = request.query["c"] # Leemos el valor del parametro

    resultado = cUsuarios.aggregate([
        {"$match": {"pais": pais}}, # Filtramos por el pais del parametro
        {"$lookup": {"from": "pedidos", "localField": "_id", "foreignField": "cliente", "as": "pedidos"}},
        # Añadimos los pedidos
        {"$unwind": "$pedidos"}, # Separamos los pedidos
        {"$unwind": "$pedidos.lineas"}, # Y dentro de los pedidos, las lineas
        {"$group": {"_id": "$pais", "gasto": {"$sum": "$pedidos.lineas.total"}}}])
        # Agrupamos por pais y obtenemos el gasto total como suma de los gastos de cada linea de pedido

    return template("ej5.tpl", param = resultado)


if __name__ == "__main__":
    # No cambiar host ni port ni debug
    run(host='localhost',port=8080,debug=True)
