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

@flaskapp.route('/cajones/cajones-ocupados/<id_funcion>')
def cajones_ocupados(id_funcion):
    sql_sent = '''SELECT * FROM estacionamiento WHERE id_funcion = {}'''.format(id_funcion)
    cajonesResult = executeQuery(sql_sent)
    print(sql_sent)
    cajones = []
    for caj in cajonesResult:
        cajones.append(buildCajonReponse(caj))
    return jsonify(cajones)
    
    
@flaskapp.route('/cajones/cajones-titular/<titular>')    
def cajones_por_titular(titular):
    cajonesResult = executeQuery('''SELECT * FROM estacionamiento WHERE no_tarjeta = {}'''.format(titular))
    print(cajonesResult)
    cajones = []
    for caj in cajonesResult:
        cajones.append(buildCajonReponse(caj))
    print("JSON: ",cajones)
    return jsonify(cajones)
    
@flaskapp.route('/cajones/add/<id_funcion>/<no_tarjeta>/<num_cajon>')
def promo_add_titular(id_funcion, no_tarjeta, num_cajon):
    query_str = '''INSERT INTO estacionamiento VALUES({}, {}, {})'''.format(no_tarjeta, id_funcion, num_cajon)
    sql_query = query_str
    print("SQL",query_str)
    result = executeQuery(sql_query)
    if result != None:
        return "Ok"
    else:
        return "Error"    
    
def start():
    config = GlobalConfiguration()
    flaskapp.config['MYSQL_DATABASE_USER'] = config.DATABASE_USER
    flaskapp.config['MYSQL_DATABASE_PASSWORD'] = config.DATABASE_PASSWD
    flaskapp.config['MYSQL_DATABASE_DB'] = config.DATABASE_NAME
    flaskapp.config['MYSQL_DATABASE_HOST'] = config.DATABASE_HOST
    mysql.init_app(flaskapp)

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5002)
 
 
 
 
 
 
    
    
