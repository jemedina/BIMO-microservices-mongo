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

def buildPromoReponse(promo):
    return {
        'num_promo': promo[0],
        'folio': promo[1],
        'descripcion': promo[2],
        'fecha_inicio': int(time.mktime(promo[3].timetuple()))*1000,
        'fecha_fin': int(time.mktime(promo[4].timetuple()))*1000,
        'descuento': float(promo[5])
    }

@flaskapp.route('/promos/all')
def all_promos():
    promosResult = executeQuery('''SELECT * FROM promocion WHERE fecha_fin >= curdate()''')
    print(promosResult)
    promos = []
    for promo in promosResult:
        promos.append(buildPromoReponse(promo))
    return jsonify(promos)

@flaskapp.route('/promos/byevent/<folio>')
def promo_by_event(folio):
    promosResult = executeQuery('''SELECT * FROM promocion WHERE fecha_fin >= curdate() and folio = {}'''.format(folio))
    print(promosResult)
    promos = []
    for promo in promosResult:
        promos.append(buildPromoReponse(promo))
    return jsonify(promos)

@flaskapp.route('/promos/bynumpromo/<num_promo>')
def promo_by_num_promo(num_promo):
    promosResult = executeQuery('''SELECT * FROM promocion WHERE fecha_fin >= curdate() and num_promo = {}'''.format(num_promo))
    print(promosResult)
    promos = []
    for promo in promosResult:
        promos.append(buildPromoReponse(promo))
    return jsonify(promos)

@flaskapp.route('/promos/bytitular/<no_tarjeta>')
def promo_by_titular(no_tarjeta):
    promosResult = executeQuery('''SELECT promocion.* FROM promocion, promocion_titular WHERE promocion.fecha_fin >= curdate() and promocion_titular.num_promo = promocion.num_promo and promocion_titular.no_tarjeta = {}'''.format(no_tarjeta))
    print(promosResult)
    promos = []
    for promo in promosResult:
        promoBuilt = buildPromoReponse(promo)
        promoBuilt['no_tarjeta'] = no_tarjeta
        promos.append(promoBuilt)
    return jsonify(promos)

@flaskapp.route('/promos/add/titular/<num_promo>/<no_tarjeta>')
def promo_add_titular(num_promo, no_tarjeta):
    sql_query = '''INSERT INTO promocion_titular VALUES({}, {})'''.format(num_promo,no_tarjeta)
    result = executeQuery(sql_query)
    if result != None:
        return "Ok"
    else:
        return "Error"

@flaskapp.route('/promos/codeslist/<num_promo>')
def codes_list(num_promo):
    codesResult = executeQuery('''SELECT * FROM lista_de_codigos_validos WHERE estado = 0 and num_promo = {}'''.format(num_promo))
    print(codesResult)
    codes = []
    for code in codesResult:
        codes.append(buildCodeReponse(code))
    return jsonify(codes)

def buildCodeReponse(code):
    return {
        'codigo': code[0],
        'estado': code[1],
        'num_promo': code[2]
    }

def start():
    config = GlobalConfiguration()
    flaskapp.config['MYSQL_DATABASE_USER'] = config.DATABASE_USER
    flaskapp.config['MYSQL_DATABASE_PASSWORD'] = config.DATABASE_PASSWD
    flaskapp.config['MYSQL_DATABASE_DB'] = config.DATABASE_NAME
    flaskapp.config['MYSQL_DATABASE_HOST'] = config.DATABASE_HOST
    mysql.init_app(flaskapp)

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5001)
        
