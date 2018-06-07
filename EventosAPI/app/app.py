from app.config import GlobalConfiguration
from flask import Flask, jsonify
from flaskext.mysql import MySQL
from flask_pymongo import PyMongo
from datetime import datetime
import time

flaskapp = Flask(__name__)
mysql = MySQL()

''' routes '''
'''
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
'''

def start():
    config = GlobalConfiguration()

    flaskapp.config['MONGO_DBNAME'] = 'bimo'
    flaskapp.config['MONGO_URI'] = 'mongodb://localhost:27017/bimo'
    global mongo 
    mongo = PyMongo(flaskapp, config_prefix='MONGO')

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5000)


@flaskapp.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin'"] = "*"
    return response

@flaskapp.route('/funciones/addfuncion/<folio>/<id_funcion>/<fecha>/<hora>')
def addfuncion(folio, id_funcion, fecha, hora):
    mongo.db.evento.find_one_and_update({'folio':int(folio)}, {'$push': {'funciones': {'id':int(id_funcion), 'fecha': datetime.strptime(fecha+"T05:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"), 'hora': hora}}})
    return jsonify(True)

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
@flaskapp.route('/favicon.ico')
def nofavicon():
    return ""
def buildSeatsReponse(seat):
    return {
        'id_funcion': seat['id_funcion'],
        'asientos': seat['asientos'],
        'titular': seat['no_tarjeta'],
        'seccion': seat['seccion'],
        'fecha': str(seat['fecha_mov']),
        'hora': seat['hora_mov'], 
        'total': seat['total']
    }

@flaskapp.route('/funciones/asientos-reservados-por-titular/<no_tarjeta>')
def seats_by_titular(no_tarjeta):
    funciones = []
    asiento = mongo.db.asiento
    for func in asiento.find({'no_tarjeta':no_tarjeta}):
        funciones.append(buildSeatsReponse(func))
    return jsonify(funciones)

@flaskapp.route('/funciones/eventos-por-id/<id_funcion>')
def eventos_por_id(id_funcion):
    eventos = mongo.db.evento
    funciones = []
		
    for funcion in eventos.find({'funciones.id':int(id_funcion)}):
        funciones.append(buildFEReponse(funcion, id_funcion))

    return jsonify(funciones)

@flaskapp.route('/funciones/all-seats/<id_funcion>/<seccion>')
def all_seats_by_section(id_funcion, seccion):
    asiento = mongo.db.asiento
    funciones = []    
    for item in asiento.find({'id_funcion':int(id_funcion),'seccion':seccion}):
        funciones.append(buildSeatsReponse(item))
    return jsonify(funciones)

@flaskapp.route('/funciones/datos_eventos/<folio>')
def events_data(folio):
    eventos = mongo.db.evento
    funciones = []
    for funcion in eventos.find({'folio': int(folio)}):
        funciones.append(buildEventsReponse(funcion))    
    print(funciones)
    return jsonify(funciones)

@flaskapp.route('/funciones/preciosporevento/<folio>')
def preciosAsientos(folio):
    eventos = mongo.db.evento
    precios = []
    for funcion in eventos.find({'folio': int(folio)}):
        precios.append(buildPreciosResponse(funcion))    
    return jsonify(precios)


@flaskapp.route('/funciones/save/<funcion_id>/<folio_artista>/<seccion>/<asientos>/<cardNumber>/<cardCvc>/<fecha_mov>/<hora_mov>/<total>')
def guardarReservacion(funcion_id,folio_artista,seccion,asientos,cardNumber,cardCvc,fecha_mov, hora_mov, total):
    asiento = mongo.db.asiento
    asientosReservadosCount = 0
    for fun in asiento.find({'id_funcion':int(funcion_id),'no_tarjeta':cardNumber}):
        asientosReservadosCount += len(fun['asientos'].split(","))
    asientosReservadosCount += len(asientos.split(","))
    try:    
        if asientosReservadosCount <=5:
            mongo.db.asiento.insert({'id_funcion': int(funcion_id), 'asientos': asientos, 'no_tarjeta': cardNumber, 'seccion': seccion, 'fecha_mov': datetime.strptime(fecha_mov+"T05:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"), 'hora_mov':hora_mov, 'total': total})
            return jsonify(True)
        else:
            print("Error. Cant insert seats, due user would reserve:",asientosReservadosCount)
            return jsonify(False)
    except Exception as e:
        print("Error during insert:",str(e))
        return jsonify(False)

@flaskapp.route('/funciones/elimina-Evento/<folio>/<id_funcion>')
def eliminaFuncion(folio,id_funcion):
    evento = mongo.db.evento
    #evento.update_one({'folio':int(folio)},{'$pull':{'funciones':{'id':int(id_funcion)}})
    evento.update_one({'folio':int(folio)},{'$pull':{'funciones':{'id':int(id_funcion)}}})
    return 'OK'

@flaskapp.route('/funciones/alta-funcion/<folio>/<id_funcion>/<fecha>/<horario>')
def altaFuncion(folio,id_funcion,fecha,horario):
    evento = mongo.db.evento
    evento.update_one({'folio':int(folio)},{'$push':{'funciones':{'id':int(id_funcion),'fecha':str(fecha),'hora':str(horario)}}},upsert=True)    
    return 'OK'

@flaskapp.route('/funciones/cambio-funcion/<folio>/<id_funcion>/<fecha>/<horario>')
def cambioFuncion(folio,id_funcion,fecha,horario):
    evento = mongo.db.evento
    evento.update_one({'folio':int(folio),'funciones.id':int(id_funcion)},{'$set':{'funciones':{'id':int(id_funcion),'fecha':str(fecha),'hora':str(horario)}}},upsert=True)    
    return 'OK'



@flaskapp.route('/funciones/save_wpromo/<funcion_id>/<folio_artista>/<seccion>/<asientos>/<cardNumber>/<cardCvc>/<fecha_mov>/<hora_mov>/<total>/<num_promo>')
def guardarReservacionConPromo(funcion_id,folio_artista,seccion,asientos,cardNumber,cardCvc,fecha_mov, hora_mov, total,num_promo):
    asiento = mongo.db.asiento
    asientosReservadosCount = 0
    for fun in asiento.find({'id_funcion':int(funcion_id),'no_tarjeta':cardNumber}):
        asientosReservadosCount += len(fun['asientos'].split(","))
    asientosReservadosCount += len(asientos.split(","))
    try:    
        if asientosReservadosCount <=5:
            mongo.db.asiento.insert({'id_funcion': int(funcion_id), 'asientos': asientos, 'no_tarjeta': cardNumber, 'seccion': seccion, 'fecha_mov': datetime.strptime(fecha_mov+"T05:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"), 'hora_mov':hora_mov, 'total': total})
            return jsonify(True)
        else:
            print("Error. Cant insert seats, due user would reserve:",asientosReservadosCount)
            return jsonify(False)
    except Exception as e:
        print("Error during insert:",str(e))
        return jsonify(False)


@flaskapp.route('/funciones/all')
def all_events():
    eventos = mongo.db.evento
    funciones = []
    for funcion in eventos.find():
        funciones.append(buildEventsReponse(funcion))
    print(funciones)
    return jsonify(funciones)

@flaskapp.route('/funciones/get_folio/<id_funcion>')
def get_folio(id_funcion):
    sql_code = '''SELECT * FROM funcion WHERE id_funcion = {}'''.format(id_funcion)
    funcionesResult = executeQuery(sql_code)
    print(sql_code)
    funciones = []
    for func in funcionesResult:
        funciones.append(buildFuncionReponse(func))
    return jsonify(funciones) 

@flaskapp.route('/funciones/get-datos/<no_tarjeta>')
def get_datos(no_tarjeta):
    funciones = []
    evento = mongo.db.evento
    asiento = mongo.db.asiento

    for asient in asiento.find({'no_tarjeta': no_tarjeta}):
        for evt in evento.find({'funciones.id': int(asient['id_funcion'])}):
            funciones.append(buildMetasReponse(asient, evt))

    return jsonify(funciones)
@flaskapp.route('/funciones/funciones-asociadas/<no_tarjeta>')
def funciones_asociadas(no_tarjeta):
    funciones = []
    evento = mongo.db.evento
    asiento = mongo.db.asiento

    for asient in asiento.find({'no_tarjeta': no_tarjeta}):
        for evt in evento.find({'funciones.id': int(asient['id_funcion'])}):
            funciones.append(buildFuncionesAsociadasResponse(evt, asient))

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
def formatearFecha(f):
    return "{:%d/%m/%Y}".format(f)

def buildEventsReponse(events):
    funciones = []
    for fun in events['funciones']: 
        funciones.append({'id':int(fun['id']), 'fecha':formatearFecha(fun['fecha']), 'hora': fun['hora']})
	
    return {
        'folio': int(events['folio']),
        'nombre': events['nombre'],
        'artistas': events['artistas'],
        'descripcion': events['descripcion'],
        'imgurl': events['imgurl'],
        'precios': {
            'top': events['precios']['top'],
            'mid': events['precios']['mid'],
            'low': events['precios']['low']				
		},
        'funciones': funciones
    } 

def buildMetasReponse(asient, event):

    for fun in event['funciones']:
        if fun['id'] == int(asient['id_funcion']):
            funcion = fun
            break

    return {
        'id_funcion': asient['id_funcion'],
        'asientos': asient['asientos'],
        'seccion': asient['seccion'],
        'folio': event['folio'],
        'nombre': event['nombre'],
        'artistas': event['artistas'],
        'fecha': str(fun['fecha']),
        'hora': str(fun['hora']),
        'precios': {
            'top': event['precios']['top'],
            'mid': event['precios']['mid'],
            'low': event['precios']['low']					
		}
    } 

def buildPreciosResponse(precios):
    return {
        'folio_evento': precios['folio'],
        'top': precios['precios']['top'],
        'mid': precios['precios']['mid'],
        'low': precios['precios']['low']
    }

def buildFEReponse(events, id_funcion):
    for fun in events['funciones']:
        if fun['id'] == int(id_funcion):
            funcion = fun
            break

    return {
        'id': funcion['id'],
        'folio': events['folio'],
        'fecha': str(funcion['fecha']),
        'hora': str(funcion['hora']),
        'nombre': events['nombre'],
        'artistas': events['artistas']
    }

def buildFuncionesAsociadasResponse(events,asients):
    for fun in events['funciones']:
        if fun['id'] == int(asients['id_funcion']):
            funcion = fun
            break
    return {
        'nombre': str(events['nombre']),
        'folio': events['folio'],
        'fecha': str(fun['fecha']),
        'hora': str(fun['hora']),
        'no_tarjeta': str(asients['no_tarjeta']),
        'id_funcion': fun['id']
    }

