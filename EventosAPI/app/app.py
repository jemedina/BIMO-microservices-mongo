from app.config import GlobalConfiguration
from flask import Flask, jsonify
from flaskext.mysql import MySQL
import time

flaskapp = Flask(__name__)
mysql = MySQL()

''' routes '''

def executeQuery(sql):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        print("SQL Error. Failed executing next query: "+str(e))
        return None
    finally:
        cursor.close()
        conn.close()

    return result


def start():
    config = GlobalConfiguration()
    flaskapp.config['MYSQL_DATABASE_USER'] = config.DATABASE_USER
    flaskapp.config['MYSQL_DATABASE_PASSWORD'] = config.DATABASE_PASSWD
    flaskapp.config['MYSQL_DATABASE_DB'] = config.DATABASE_NAME
    flaskapp.config['MYSQL_DATABASE_HOST'] = config.DATABASE_HOST
    mysql.init_app(flaskapp)

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5000)

@flaskapp.route('/funciones/precio/<num_asiento>/<seccion>/<folio>/<fecha>/<hora>')
def price_by_num_asiento(num_asiento,seccion, folio, fecha, hora):
    funcionesResult = executeQuery('''SELECT precio FROM asiento WHERE num_asiento = {}'''.format(num_asiento),''' and folio = {}'''.format(folio),''' and fecha = {}'''.format(fecha),''' and hora = {}'''.format(hora),''' and seccion = {}'''.format(seccion))
    print(funcionesResult)
    funciones = []
    funciones.append(buildPriceReponse(funcionesResult))
    return jsonify(funciones)

def buildPriceReponse(precio):
    return {
        'precio': precio
    }

@flaskapp.route('/funciones/asientos-ocupados-por-seccion/<seccion>/<folio>/<fecha>/<hora>')
def reserved_seats_by_section(seccion, folio, fecha, hora):
    funcionesResult = executeQuery('''SELECT * FROM asiento_titular WHERE seccion = {}'''.format(seccion),''' and folio = {}'''.format(folio),''' and fecha = {}'''.format(fecha),''' and hora = {}'''.format(hora))
    print(funcionesResult)
    funciones = []
    for func in funcionesResult:
        funciones.append(buildSeatsReponse(func))
    return jsonify(funciones)

def buildSeatsReponse(seat):
    return {
        'id_funcion': seat[0],
        'asientos': seat[1],
        'titular': seat[2],
        'seccion': seat[3],
        'fecha': str(seat[4]),
        'hora': str(seat[5]), 
        'total': seat[6]
    }

@flaskapp.route('/funciones/asientos-reservados-por-titular/<no_tarjeta>')
def seats_by_titular(no_tarjeta):
    funcionesResult = executeQuery('''SELECT * FROM asiento WHERE no_tarjeta = {}'''.format(no_tarjeta))
    print("----->",format(no_tarjeta))
    funciones = []
    for func in funcionesResult:
        funciones.append(buildSeatsReponse(func))
    return jsonify(funciones)

@flaskapp.route('/funciones/eventos-por-id/<id_funcion>')
def eventos_por_id(id_funcion):
    funcionesResult = executeQuery('''SELECT * FROM funcion, evento WHERE evento.folio=funcion.folio and funcion.id = {}'''.format(id_funcion))
    print("----->",format(id_funcion))
    funciones = []
    for func in funcionesResult:
        funciones.append(buildFEReponse(func))
    return jsonify(funciones)

@flaskapp.route('/funciones/all-seats/<id_funcion>/<seccion>')
def all_seats_by_section(id_funcion, seccion):
    sql_code = '''SELECT * FROM asiento WHERE id_funcion = {}'''.format(id_funcion)+''' and seccion = '{}' '''.format(seccion)
    funcionesResult = executeQuery(sql_code)
    print(sql_code)
    funciones = []
    for func in funcionesResult:
        funciones.append(buildSeatsReponse(func))
    return jsonify(funciones)

@flaskapp.route('/funciones/datos_eventos/<folio>')
def events_data(folio):
    funcionesResult = executeQuery('''SELECT * FROM evento inner join precios_evento on evento.folio = precios_evento.folio_evento AND evento.folio = {}'''.format(folio))
    funciones = []
    for funcion in funcionesResult:
        funciones.append(buildEventsReponse(funcion))
    funcionesHorarios = executeQuery('''SELECT * FROM funcion WHERE folio = {}'''.format(folio))
    for horario in funcionesHorarios:
        appendHorariosToFunciones(funciones, horario)
    print(funciones)
    return jsonify(funciones)

@flaskapp.route('/funciones/preciosporevento/<folio>')
def preciosAsientos(folio):
    preciosResult = executeQuery('''SELECT * FROM precios_evento  WHERE folio_evento = {}'''.format(folio))
    precios = []
    for precio in preciosResult:
        precios.append(buildPreciosResponse(precio))
    return jsonify(precios)


@flaskapp.route('/funciones/save/<funcion_id>/<folio_artista>/<seccion>/<asientos>/<cardNumber>/<cardCvc>/<fecha_mov>/<hora_mov>/<total>')
def guardarReservacion(funcion_id,folio_artista,seccion,asientos,cardNumber,cardCvc,fecha_mov, hora_mov, total):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        query = '''INSERT INTO asiento VALUES ({},"{}","{}","{}","{}","{}",{})'''.format(funcion_id,asientos,cardNumber,seccion,fecha_mov, hora_mov,total)
        print('Query:',query)
        res = cursor.execute(query)
        conn.commit()
        print('Query:',query)
        return jsonify(True)
    except Exception as e:
        print("Error during insert:",str(e))
        print("QUERY------------------------------------------------>",query)
        return jsonify(False)



@flaskapp.route('/funciones/all')
def all_events():
    funcionesResult = executeQuery('''SELECT * FROM evento inner join precios_evento on evento.folio = precios_evento.folio_evento''')
    funciones = []
    for funcion in funcionesResult:
        funciones.append(buildEventsReponse(funcion))
    funcionesHorarios = executeQuery('''SELECT * FROM funcion''')
    for horario in funcionesHorarios:
        appendHorariosToFunciones(funciones, horario)
    print(funciones)
    return jsonify(funciones)

flaskapp.route('/funciones/get_folio/<id_funcion>')
def get_folio(id_funcion):
    sql_code = '''SELECT * FROM funcion WHERE id_funcion = {}'''.format(id_funcion)
    funcionesResult = executeQuery(sql_code)
    print(sql_code)
    funciones = []
    for func in funcionesResult:
        funciones.append(buildFuncionReponse(func))
    return jsonify(funciones) 

flaskapp.route('/funciones/get-datos/<no_tarjeta>')
def get_datos(no_tarjeta):
    print("xD",no_tarjeta)
    funcionesResult = executeQuery('''SELECT * FROM asiento, evento, funcion, precios_evento WHERE asiento.id_funcion=funcion.id and funcion.folio=evento.folio and evento.folio=precios_evento.folio_evento and asiento.no_tarjeta={}'''.format(no_tarjeta));
    print("#########################################",funcionesResult)
    funciones = []
    for funcion in funcionesResult:
        funciones.append(buildMetasReponse(funcion))
    print(funciones)
    return jsonify(funciones)

def appendHorariosToFunciones(funciones, horario):
    for i in range(0, len(funciones)):
        if funciones[i]['folio'] == horario[1]:
            if not 'funciones' in funciones[i]:
                funciones[i]['funciones'] = []
            funciones[i]['funciones'].append({
				'id': horario[0],
                'fecha':str(horario[2]),
                'hora':str(horario[3])
                })
			
def buildEventsReponse(events):
    return {
        'folio': events[0],
        'nombre': events[1],
        'artistas': events[2],
        'descripcion': events[3],
        'imgurl': events[4],
        'precios': {
            'top': events[6],
            'mid': events[7],
            'low': events[8]				
		}
    } 

def buildMetasReponse(events):
    return {
        'id_funcion': events[0],
        'asientos': events[1],
        'seccion': events[3],
        'folio': events[4],
        'nombre': events[5],
        'artistas': events[6],
        'fecha': str(events[11]),
        'hora': str(events[12]),
        'precios': {
            'top': events[14],
            'mid': events[15],
            'low': events[16]					
		}
    } 

def buildPreciosResponse(precios):
    return {
        'folio_evento': precios[0],
        'top': precios[1],
        'mid': precios[2],
        'low': precios[3]
    }

def buildFEReponse(events):
    return {
        'id': events[0],
        'folio': events[1],
        'fecha': str(events[2]),
        'hora': str(events[3]),
        'nombre': events[5],
        'artistas': events[6]
    }

