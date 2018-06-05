from app.config import GlobalConfiguration
from flask import Flask, jsonify
from flaskext.mysql import MySQL
from flask_pymongo import PyMongo
import time

flaskapp = Flask(__name__)
mysql = MySQL()
#mongo = PyMongo(flaskapp)
''' routes '''
def start():
    config = GlobalConfiguration()

    flaskapp.config['MONGO_DBNAME'] = 'bimo'
    flaskapp.config['MONGO_URI'] = 'mongodb://localhost:27017/bimo'
    global mongo 
    mongo = PyMongo(flaskapp, config_prefix='MONGO')

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5002) 

def executeQuery(sql):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
    except Exception as e:
        print("SQL Error. Failed executing next query: "+str(e))
        return None
    finally:
        cursor.close()
        conn.close()

    return result

def buildCajonReponse(caj):
    return {
        'no_tarjeta': caj[0],
        'id_funcion': caj[1],
        'num_cajon': caj[2]
    }

#@flaskapp.route('/cajones/cajones-ocupados/<id_funcion>')
#def cajones_ocupados(id_funcion):
    #sql_sent = '''SELECT * FROM estacionamiento WHERE id_funcion = {}'''.format(id_funcion)
    #cajonesResult = executeQuery(sql_sent)
    #print(sql_sent)
    #cajones = []
    #for caj in cajonesResult:
        #cajones.append(buildCajonReponse(caj))
    #return jsonify(cajones) 

@flaskapp.route('/cajones/cajones-ocupados/<id_funcion>')
def cajones_ocupados(id_funcion):
    print(str(id_funcion))
    parking = mongo.db.estacionamiento
    cajones = []
    for caj in parking.find({"id_funcion":int(id_funcion)}):
        cajones.append({'no_tarjeta': int(caj['no_tarjeta']),'id_funcion': int(caj['id_funcion']),'num_cajon': int(caj['num_cajon'])})
    return jsonify(cajones) 
    
    
#@flaskapp.route('/cajones/cajones-titular/<titular>')    
#def cajones_por_titular(titular):
    #cajonesResult = executeQuery('''SELECT * FROM estacionamiento WHERE no_tarjeta = {}'''.format(titular))
    #print(cajonesResult)
    #cajones = []
    #for caj in cajonesResult:
        #cajones.append(buildCajonReponse(caj))
    #print("JSON: ",cajones)
    #return jsonify(cajones) 

@flaskapp.route('/cajones/cajones-titular/<no_tarjeta>')    
def cajones_por_titular(no_tarjeta):
    parking = mongo.db.estacionamiento
    cajones = []
    print(parking.find({"no_tarjeta":str(no_tarjeta)}))
    for caj in  parking.find({"no_tarjeta":str(no_tarjeta)}):
        cajones.append({'no_tarjeta': str(caj['no_tarjeta']),'id_funcion': int(caj['id_funcion']),'num_cajon': int(caj['num_cajon'])})
    return jsonify(cajones)
    
#@flaskapp.route('/cajones/add/<id_funcion>/<no_tarjeta>/<num_cajon>')
#def promo_add_titular(id_funcion, no_tarjeta, num_cajon):
    #query_str = '''INSERT INTO estacionamiento VALUES({}, {}, {})'''.format(no_tarjeta, id_funcion, num_cajon)
    #sql_query = query_str
    #print("SQL",query_str)
    #result = executeQuery(sql_query)
    #if result != None:
        #return "Ok"
    #else:
        #return "Error"    

@flaskapp.route('/cajones/add/<id_funcion>/<no_tarjeta>/<num_cajon>')
def promo_add_titular(id_funcion, no_tarjeta, num_cajon):
    parking = mongo.db.estacionamiento
    mongo.db.estacionamiento.insert({"no_tarjeta":no_tarjeta,"id_funcion":int(id_funcion),"num_cajon":int(num_cajon)})
    return 'OK'    
    
'''def start():
    config = GlobalConfiguration()
    flaskapp.config['MYSQL_DATABASE_USER'] = config.DATABASE_USER
    flaskapp.config['MYSQL_DATABASE_PASSWORD'] = config.DATABASE_PASSWD
    flaskapp.config['MYSQL_DATABASE_DB'] = config.DATABASE_NAME
    flaskapp.config['MYSQL_DATABASE_HOST'] = config.DATABASE_HOST
    mysql.init_app(flaskapp)

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5002) ''' 
 
 
 
 
 
    
    
