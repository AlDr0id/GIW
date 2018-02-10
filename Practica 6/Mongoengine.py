# GIW
# Practica Mongoengine
# Grupo 04
# Marcos Robles Palencia
# Alvaro de la Cruz Casado
# declaramos que esta solucion
# es fruto exclusivamente de nuestro trabajo personal. No hemos sido
# ayudados por ninguna otra persona ni hemos obtenido la solucion de
# fuentes externas, y tampoco hemos compartido nuestra solucion con
# nadie. Declaramos ademas que no hemos realizado de manera deshonesta
# ninguna otra actividad que pueda mejorar nuestros resultados
# ni perjudicar los resultados de los demas.


from mongoengine import *


class Producto(Document):
    barcode = StringField(unique = True, required = True, regex = "^\d{13}$") # Omitimos min_length = 13 , max_length = 13 al especificarlo con regex
    nombre = StringField(required = True)
    categoriaPrincipal = IntField(required = True, min_value = 0) # Numero natural
    categoriasSecundarias = ListField(IntField(min_value = 0)) # Numeros naturales

    def clean(self):
        # Comprobacion de la condicion del digito de control
        ean = self.barcode[:12]

        sumaImpares = 0
        sumaPares = 0
        i = 0
        for dig in ean:
            if i % 2 == 0: # Al comenzar en 0, esa es la posicion 1 (que es impar)
                sumaImpares += int(dig)
            else:
                sumaPares += int(dig)
            i += 1

        sumaPares = sumaPares * 3
        sumaTotal = sumaPares + sumaImpares
        digitoControl = (10 - (sumaTotal % 10)) % 10 # Dos veces modulo 10 por si la resta primera diera 10, el digito debe ser 0

        if int(digitoControl) != int(self.barcode[12]):
            raise ValidationError("Digito de control incorrecto")

        # Comprobacion de la condicion sobre las categorias secundarias
        if self.categoriasSecundarias != []:
            if self.categoriasSecundarias[0] != self.categoriaPrincipal:
                raise ValidationError("La primera categoria secundaria debe coincidir con la principal")



class LineaPedido(EmbeddedDocument):
    cantidadProducto = IntField(required = True)
    precioProducto = FloatField(required = True, min_value = 0.0) # Un precio nunca puede ser negativo
    nombreProducto = StringField(required = True)
    precioTotal = FloatField(required = True, min_value = 0.0) # Un precio nunca puede ser negativo
    producto = ReferenceField(Producto, required = True)

    def clean(self):
        # Comprobacion de la condicion de la suma de los precios y el precio total
        if self.precioProducto * self.cantidadProducto != self.precioTotal:
            raise ValidationError("El precio total no coincide con la suma de precios de los productos")

        # Comprobacion de la condicion de la coincidencia del nombre del producto
        if self.nombreProducto != self.producto.nombre:
            raise ValidationError("El nombre del producto no coincide")


class Pedido(Document):
    precioTotalPedido = FloatField(required = True, min_value = 0.0) # Un precio nunca puede ser negativo
    fechaPedido = ComplexDateTimeField(required = True)
    lineasPedido = ListField(EmbeddedDocumentField(LineaPedido), required = True)

    def clean(self):
        # Comprobacion de la condicion de la suma de los precios de las lineas y el precio total
        sumaLista = 0.0 # Float
        for producto in self.lineasPedido:
            sumaLista += producto.precioTotal
        if sumaLista != self.precioTotalPedido:
            raise ValidationError("El precio total no coincide con la suma de precios de las lineas")

class TarjetaCredito(EmbeddedDocument):
    nombrePropietario = StringField(required = True)
    numeroTarjeta = StringField(required = True, regex = "^\d{16}$") # Antes era IntField pero al comenzar con 0 daba error
    # Omitimos min_length = 16 , max_length = 16 al especificarlo con regex
    mesCaducidad =  StringField(required = True, regex = "^(0[1-9])|1[0-2]$") # Controlamos cifras correspondientes a que sea un mes. Antes era IntField pero al comenzar con 0 daba error
    # Omitimos min_length = 2 , max_length = 2 al especificarlo con regex
    anioCaducidad = StringField(required = True, regex = "^\d{2}$") # Antes era IntField pero al comenzar con 0 daba error
    # Omitimos min_length = 2 , max_length = 2 al especificarlo con regex
    codigoVerificacion = StringField(required = True, regex = "^\d{3}$") # Antes era IntField pero al comenzar con 0 daba error
    # Omitimos min_length = 3 , max_length = 3 al especificarlo con regex

class Usuario(Document):
    dni = StringField(required = True, unique = True, regex = "^(([X-Z]{1})(\d{7})([A-Z]{1}))|((\d{8})([A-Z]{1}))$") # Consideramos tanto nacional como extranjero
    nombre = StringField(required = True)
    primer_Apellido = StringField(required = True)
    segundo_Apellido = StringField()
    fechaNacimiento = StringField(required = True, regex = "^(\d{4}-\d{2}-\d{2})$") # Que sea AAAA-MM-DD
    fechaUltimosAccesos = ListField(ComplexDateTimeField())
    listaTC = ListField(EmbeddedDocumentField(TarjetaCredito))
    listaPedidos = ListField(ReferenceField(Pedido), reverse_delete_rule = PULL) # Si se borra el pedido, se borra de esta lista

    def clean(self):
        # Comprobacion de la letra tanto para NIE nacional como extranjero
        letrasExtr = "XYZ"
        equivalenciasExtr = {
            "X": 0,
            "Y": 1,
            "Z": 2
        }
        listaLetras = "TRWAGMYFPDXBNJZSQVHLCKE"
        dni = self.dni[:8]
        if dni[0] in letrasExtr: # Saber si es NIE extranjero
            dni[0] = equivalenciasExtr[dni[0]] # Sustituimos valor
        dni = int(dni)
        resto = dni % 23
        letra = listaLetras[resto]
        if letra != self.dni[8]:
            raise ValidationError("La letra no coincide")



def insertar():
    # Minimo 2 usuarios con al menos 2 pedidos diferentes de mas de una linea y al menos un usuario con 2 o mas tarjetas de credito

    # Creamos productos
    producto1 = Producto(barcode = "7382904725368", nombre = "batidora", categoriaPrincipal = 1, categoriasSecundarias = [1, 2])
    producto2 = Producto(barcode = "8392046710244", nombre = "horno", categoriaPrincipal = 2)
    producto3 = Producto(barcode = "2617394857301", nombre = "microondas", categoriaPrincipal = 2)

    # Insertamos productos
    producto1.save()
    producto2.save()
    producto3.save()

    # Creamos lineas
    linea1 = LineaPedido(cantidadProducto = 4, precioProducto = 40, nombreProducto = "batidora", precioTotal = 160, producto = producto1)
    linea2 = LineaPedido(cantidadProducto = 12, precioProducto = 120, nombreProducto = "horno", precioTotal = 1440, producto = producto2)
    linea3 = LineaPedido(cantidadProducto = 2, precioProducto = 70, nombreProducto = "microondas", precioTotal = 140, producto = producto3)

    # No insertamos lineas porque son EmbeddedDocument
    #linea1.save()
    #linea2.save()
    #linea3.save()

    # Creamos pedidos
    pedido1 = Pedido(precioTotalPedido = 1740, fechaPedido = "2017,12,25,00,00,00,000000", lineasPedido = [linea1, linea2, linea3])
    pedido2 = Pedido(precioTotalPedido = 1580, fechaPedido = "2018,10,19,15,02,13,000000", lineasPedido = [linea2, linea3])
    pedido3 = Pedido(precioTotalPedido = 1440, fechaPedido = "2018,11,14,21,45,12,783997", lineasPedido = [linea2])
    pedido4 = Pedido(precioTotalPedido = 160, fechaPedido = "2018,11,14,21,12,00,712997", lineasPedido = [linea1])
    pedido5 = Pedido(precioTotalPedido = 140, fechaPedido = "2018,10,15,21,45,12,783997", lineasPedido = [linea3])
    pedido6 = Pedido(precioTotalPedido = 300, fechaPedido = "2018,12,21,22,43,11,780097", lineasPedido = [linea1, linea3])

    # Insertamos pedidos
    pedido1.save()
    pedido2.save()
    pedido3.save()
    pedido4.save()
    pedido5.save()
    pedido6.save()

    # Creamos tarjetas
    tarjetaP1 = TarjetaCredito(nombrePropietario = "Pedro", numeroTarjeta = "1234567890123456", mesCaducidad = "11", anioCaducidad = "18", codigoVerificacion = "356")
    tarjetaP2 = TarjetaCredito(nombrePropietario = "Pedro", numeroTarjeta = "4238567892123430", mesCaducidad = "10", anioCaducidad = "20", codigoVerificacion = "456")
    tarjetaP3 = TarjetaCredito(nombrePropietario = "Pedro", numeroTarjeta = "5244567890121456", mesCaducidad = "05", anioCaducidad = "19", codigoVerificacion = "924")
    tarjetaM = TarjetaCredito(nombrePropietario = "Maria", numeroTarjeta = "9234564090122456", mesCaducidad = "03", anioCaducidad = "21", codigoVerificacion = "742")
    tarjetaC = TarjetaCredito(nombrePropietario = "Clotilde", numeroTarjeta = "8234307890163426", mesCaducidad = "08", anioCaducidad = "18", codigoVerificacion = "630")
    tarjetaJ = TarjetaCredito(nombrePropietario = "Javier", numeroTarjeta = "6234560890323451", mesCaducidad = "04", anioCaducidad = "22", codigoVerificacion = "411")

    # No insertamos tarjetas porque son EmbeddedDocument
    # tarjetaP1.save()
    # tarjetaP2.save()
    # tarjetaP3.save()
    # tarjetaM.save()
    # tarjetaC.save()
    # tarjetaJ.save()

    # Creamos usuarios
    pedro = Usuario(dni = "84569514D", nombre = "Pedro", primer_Apellido = "Mora", segundo_Apellido = "Sobera", fechaNacimiento = "1990-01-14", fechaUltimosAccesos = ["2017,12,09,14,15,12,178394", "2017,11,09,14,13,22,178094"],  listaTC = [tarjetaP1, tarjetaP2, tarjetaP3], listaPedidos = [pedido1, pedido3])
    maria = Usuario(dni = "45671298Z", nombre = "Maria", primer_Apellido = "Robles", segundo_Apellido = "Avellano", fechaNacimiento = "1978-06-12", fechaUltimosAccesos = ["2017,11,28,12,32,54,928174", "2017,11,02,17,45,56,276653"], listaTC = [tarjetaM, tarjetaP2], listaPedidos = [pedido2, pedido3, pedido4])
    clotilde = Usuario(dni = "57319876N", nombre = "Clotilde", primer_Apellido = "Oreja", segundo_Apellido = "Valverde", fechaNacimiento = "2000-02-03", fechaUltimosAccesos = ["2017,12,10,22,04,23,019456", "2017,12,09,14,15,12,178394"], listaTC = [tarjetaC, tarjetaM], listaPedidos = [pedido5, pedido2])
    javier = Usuario(dni = "28794821V", nombre = "Javier", primer_Apellido = "Pascua", segundo_Apellido = "Fresa", fechaNacimiento = "1985-11-23", fechaUltimosAccesos = ["2017,11,02,17,45,56,276653", "2017,12,10,22,04,23,019456"], listaTC = [tarjetaJ, tarjetaP3], listaPedidos = [pedido2, pedido6])

    # Insertamos usuarios
    pedro.save()
    maria.save()
    clotilde.save()
    javier.save()



db = connect('giw_mongoengine') # Conexion a la base de datos
db.drop_database('giw_mongoengine') # Borramos lo que haya previamente antes de insertar para evitar duplicados
insertar() # Llamamos a insertar
