from app.config import GlobalConfiguration
from flask import Flask, jsonify
from flaskext.mysql import MySQL
from flask_pymongo import PyMongo
import time
from datetime import datetime

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

@flaskapp.route('/promos/addpromo/<no_promo>/<descrip>/<f_inicio>/<f_final>/<descuento>')
def addPromo(no_promo, descrip, f_inicio, f_final, descuento):
    print("INSERTANDO:",f_inicio,f_final)
    promo = mongo.db.promocion
    promo.insert({'num_promo':int(no_promo),'descripcion':str(descrip),'fecha_inicio':datetime.strptime(f_inicio+"T05:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"), 'fecha_fin':datetime.strptime(f_final+"T05:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"), 'descuento':float(descuento)})    
    return jsonify(True)

@flaskapp.route('/promos/updatepromo/<no_promo>/<descrip>/<f_inicio>/<f_final>/<descuento>')
def cambioPromo(no_promo, descrip, f_inicio, f_final, descuento):
    promo = mongo.db.promocion
    promo.update_one({'num_promo':int(no_promo)},{'$set':{'descripcion':str(descrip),'fecha_inicio':datetime.strptime(f_inicio+"T05:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"), 'fecha_fin':datetime.strptime(f_final+"T05:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"), 'descuento':float(descuento)}},upsert=True)    
    return jsonify(True)

@flaskapp.route('/promos/delpromo/<no_promo>')
def delPromo(no_promo):
    mongo.db.promocion.remove({'num_promo': int(no_promo)})    
    return jsonify(True)

@flaskapp.route('/promos/all')
def all_promos():
	promocion = mongo.db.promocion
	promos = []
	for promo in promocion.find():
		promos.append({'num_promo': int(promo['num_promo']),'descripcion': promo['descripcion'],'fecha_inicio': formato(promo['fecha_inicio']),'fecha_fin': formato(promo['fecha_fin']),'descuento': float(promo['descuento'])})
	return jsonify(promos)


def formato(f):
	return "{:%m/%d/%Y}".format(f)






def start():
    config = GlobalConfiguration()

    flaskapp.config['MONGO_DBNAME'] = 'bimo'
    flaskapp.config['MONGO_URI'] = 'mongodb://localhost:27017/bimo'
    global mongo 
    mongo = PyMongo(flaskapp, config_prefix='MONGO')

    print("Initializing application!")
    flaskapp.run(host='0.0.0.0',port=5001)
        
