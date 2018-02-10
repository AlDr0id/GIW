<!--
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
-->

<!DOCTYPE html>
<html>
  <head>
  <title>Consulta 1</title>
  </head>

  <body>

    <TABLE border=1>
      %num = 0
      <tr>
        <td>Pais</td>
        <td>Usuarios</td>
      </tr>
      %for elem in param:
        %num += 1
        <tr>
          <td>{{elem["_id"]}}</td>
          <td>{{elem["totalPersonas"]}}</td>
        </tr>
      %end
    </TABLE>

    <br>
    <li>Num de elementos: {{num}}</li>

  </body>
</html>
