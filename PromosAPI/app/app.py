from app.config import GlobalConfiguration
from flask import Flask, jsonify
from flaskext.mysql import MySQL
from flask_pymongo import PyMongo
import time

flaskapp = Flask(__name__)
mysql = MySQL()

''' routes '''


def buildPromoReponse(promo):
    return {
        'num_promo': promo['num_promo'],
        'folio': promo['folio'],
        'descripcion': promo['descripcion'],
        'fecha_inicio': promo['fecha_inicio'],
        'fecha_fin': promo['fecha_fin'],
        'descuento': float(promo['descuento'])
    }

@flaskapp.route('/promos/cambio-promo/<no_promo>/<descrip>/<f_inicio>/<f_final>/<descuento>')

def cambioPromo(no_promo, descrip, f_inicio, f_final, descuento):
    promo = mongo.db.promocion
    promo.update_one({'num_promo':int(no_promo)},{'$set':{'descripcion':str(descrip),'fecha_inicio':str(f_inicio), 'fecha_fin':str(f_final), 'descuento':float(descuento)}},upsert=True)    
    return 'OK'

@flaskapp.route('/promos/all')
def all_promos():
	promocion = mongo.db.promocion
	promos = []
	for promo in promocion.find():
		promos.append({'num_promo': int(promo['num_promo']),'folio': int(promo['folio']),'descripcion': promo['descripcion'],'fecha_inicio': promo['fecha_inicio'],'fecha_fin': promo['fecha_fin'],'descuento': float(promo['descuento'])})
	return jsonify(promos)


def formato(f):
	return "{:%d/%m/%Y}".format(f)






def start():
    config = GlobalConfiguration()

    flaskapp.config['MONGO_DBNAME'] = 'bimo'
    flaskapp.config['MONGO_URI'] = 'mongodb://localhost:27017/bimo'
    global mongo 
    mongo = PyMongo(flaskapp, config_prefix='MONGO')

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5001)
        
