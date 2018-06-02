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

    flaskapp.config['MONGO_DBNAME'] = 'prueba_db'
    flaskapp.config['MONGO_URI'] = 'mongodb://localhost:27017/prueba_db'
    global mongo 
    mongo = PyMongo(flaskapp, config_prefix='MONGO')

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5001)
        
