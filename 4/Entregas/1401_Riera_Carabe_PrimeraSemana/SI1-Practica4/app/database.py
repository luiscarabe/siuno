# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()



def getListaCliMes(mes, anio, iumbral, iintervalo, use_prepare, break0, niter):
    db_conn=dbConnect()
    if use_prepare == True:
        db_conn.execute("PREPARE clientDistPrep (int) AS \
                    SELECT clientesDistintos($1, " + "{0:0=4d}".format(anio) + \
                    "{0:0=2d}".format(mes) +") as cc;")

    # Array con resultados de la consulta para cada umbral
    dbr=[]

    for ii in range(niter):
        if use_prepare==True:
            res = db_conn.execute("EXECUTE clientDistPrep ( " + str(iumbral) +\
                ");").fetchone()

        else:
            res = db_conn.execute("SELECT clientesDistintos (" + str(iumbral) +", " +\
                str(anio) + str(mes) +");").fetchone()
        # Guardar resultado de la query
        dbr.append({"umbral":iumbral,"contador":res['cc']})

        if break0==True and res['cc']==None:
            break;

        # Actualizacion de umbral
        iumbral = iumbral + iintervalo

    if use_prepare == True:
        db_conn.execute("DEALLOCATE clientDistPrep;")
    dbCloseConnect(db_conn)
    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)

    resultproxy.close()

    db_conn.close()

    return a

def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()

    db_conn.close()

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}

def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):

    # Array de trazas a mostrar en la página
    dbr=[]

    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()

    try:
        # TODO: ejecutar consultas
        print("err")
    except Exception as e:
        print("err")
        # TODO: deshacer en caso de error

    else:
        print("err")
        # TODO: confirmar cambios si todo va bien


    return dbr
