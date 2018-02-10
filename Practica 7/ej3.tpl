<!--
##
## Gestion de la Informacion en la Web
## Practica Consultas MongoDB
## Grupo 04
## Sergio Juan Higuera Velasco, Pablo Gomez Calvo, Marcos Robles Palencia y Alvaro de la Cruz Casado
## declaramos que esta solucion
## es fruto exclusivamente de nuestro trabajo personal. No hemos sido
## ayudados por ninguna otra persona ni hemos obtenido la solucion de
## fuentes externas, y tampoco hemos compartido nuestra solucion con
## nadie. Declaramos ademas que no hemos realizado de manera deshonesta
## ninguna otra actividad que pueda mejorar nuestros resultados
## ni perjudicar los resultados de los demas.
##
-->

<!DOCTYPE html>
<html>
  <head>
  <title>Consulta 3</title>
  </head>

  <body>

    <li>Num de elementos: {{num}}</li>
    <br>
    <TABLE border=1>
      %for elem in param:
        <tr>
          <td>{{elem["_id"]}}</td>
          <td>{{elem["email"]}}</td>
          <td>{{elem["webpage"]}}</td>
          <td>Num tarjeta {{elem["credit_card"]["number"]}} que expira el mes {{elem["credit_card"]["expire"]["month"]}} de 20{{elem["credit_card"]["expire"]["year"]}}</td>
          <td>{{elem["password"]}}</td>
          <td>{{elem["name"]}}</td>
          <td>{{elem["surname"]}}</td>
          <td>{{elem["address"]["street"]}} num {{elem["address"]["num"]}}, {{elem["address"]["zip"]}} de {{elem["address"]["country"]}}</td>
          <td>{{elem["likes"]}}</td>
          <td>{{elem["birthdate"]}}</td>
        </tr>
      %end
    </TABLE>

  </body>
</html>
