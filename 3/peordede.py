from flask import Flask, request, render_template, redirect, session, url_for
import json
import os
import random
import md5
import sys
import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://alumnodb@localhost/si1'
#db = SQLAlchemy(app)
Base = automap_base()
engine = create_engine("postgres://alumnodb@localhost/si1")
Base.prepare(engine, reflect=True)
connection = engine.connect()
sys.path.append('~/apache2/var/www/html/')
app.secret_key = 'teamoluis'
app.root_path=os.path.dirname(os.path.abspath(__file__))

# Funcion auxiliar para crear el carrito
def createCarrito(customerid):
    # Comprobar si existe el carrito
    if(len(connection.execute("select 1 from orders where status = NULL and customerid = \'" +
        str(customerid) + "\'"))==0):
        connection.execute("select createCarrito(" + str(customerid) + ")")

@app.route('/', methods = ['POST', 'GET'])
def index(methods = ['POST', 'GET']):
  #films = json.load(open(os.path.join(app.root_path,'data/catalogo.json')))['peliculas']
  #films = json.load(join(dirname(realpath(__file__)), 'data/catalogo.json'))
  #films=json.load(open('/data/catalogo.json'))
  films = connection.execute("select * \
        from products as p, imdb_movies as f\
        where p.movieid=f.movieid;").fetchall()
  genres = [genre[0] for genre in connection.execute("select genre from genres;").fetchall()]
  genres.sort()
  genre=request.args.get('filters')
  if(not(genre==None or genre=='-')):
    films = connection.execute("select * \
          from products as p, imdb_movies as f, imdb_moviegenres AS g\
          where genre='" + genre + "' AND f.movieid=g.movieid AND p.movieid=f.movieid;").fetchall()
  if('username' in session):
    return render_template('index.html', films = films, genres = genres, log = session['username'])
  else:
    return render_template('index.html', films = films, genres = genres, log = None)

@app.route('/carrito/', methods=['GET','POST'])
def carrito(methods=['GET','POST']):
  try:
    jsonFile = open(app.root_path + '/data/catalogo.json')
  except IOError:
    return "No se pudieron cargar las peliculas"
  films_cat=json.load(jsonFile)['peliculas']
  try:
    carrito = session['carrito']
  except KeyError:
    carrito=[]
    sumPrice=0
  else:
    sumPrice = 0
    carrito = [x for x in carrito if x[0] in films_cat]
    for film in carrito:
      sumPrice += (film[0]['precio']*film[1])
  if(request.method=='POST'):
    del_film_id=request.form.get('id')
    carrito = [x for x in carrito if x[0]['id'] != int(del_film_id)]
    session['carrito']=carrito
    return redirect(url_for("carrito"))


  if('username' in session):
    return render_template('carrito.html', films = carrito, sumPrice = sumPrice, log = session['username'])
  else:
    return render_template('carrito.html', films = carrito, sumPrice = sumPrice,log = None)

@app.route('/contacto/')
def contacto():
  if('username' in session):
    return render_template('contacto.html', log = session['username'])
  else:
    return render_template('contacto.html', log = None)

@app.route('/iniciosesion/', methods = ['POST', 'GET'])
def iniciosesion(methods = ['POST', 'GET']):

  if(request.method=='POST'):
    username=request.form.get('nombre')
    if(username!=None):
      # Obtenemos la contrasenia asociada al usuario,
      # la lista passwords tendra longitud 1 o 0
      passwords = list(connection\
        .execute("select password from customers where username = \'" + \
        username + "\';"))
      # Si existe la password, existe el usuario
      if len(passwords) > 0:
        contrasenia=passwords[0][0]
        if contrasenia == md5.new(request.form.get('contrasenia')).hexdigest():
          session['username']=username
          return redirect(url_for("index"))
        return render_template('iniciosesion.html', usrNoexiste=None, pswEquivocada=1)
      return render_template('iniciosesion.html', usrNoexiste=1, pswEquivocada=None)

    return render_template('iniciosesion.html', usrNoexiste=None, pswEquivocada=None)
  else:
    return render_template('iniciosesion.html', usrNoexiste=None, pswEquivocada=None)

@app.route('/registro/', methods = ['POST', 'GET'])
def registro():
  if(request.method=='POST'):
    username=request.form.get('usuario')
    if (username!=None):

      existeUser = len(list(connection\
        .execute("select username from customers where username = \'" + \
        username + "\';")))
      if existeUser > 0:
        return render_template('registro.html', existe=1)

      connection.execute("insert into customers "
        "(username, firstname, lastname, password, "
        "email, creditcard, creditcardtype, creditcardexpiration, address1, "
        "country, zip, city) "
        " values (\'" + username + "\', \'" + \
        request.form.get('nombre') + "\', \'" +\
        request.form.get('apellidos') + "\', \'" + \
        md5.new(request.form.get('contrasenia')).hexdigest() + \
        "\', \'" + request.form.get('correo') + "\', \'" + \
        request.form.get('tarjeta') + "\', \'" + \
        request.form.get('tarjetaTipo') + "\', \'" + \
        request.form.get('expiration') + "\', \'" + \
        request.form.get('direccion') + "\', \'" + \
        request.form.get('country') + "\', \'" + \
        request.form.get('zip') + "\', \'" + \
        request.form.get('city') + \
        "\');")

      #Creamos historial.json
      # f = open(historialR, "w+")
      # f.write("{\n\t\"peliculas\": []\n}")
      # f = None
      session['username']=username
      #Creamos data.json
      # with open(dataR,"w") as f:
      #   f.write("{\n\t\"username\": ")
      #   f.write("\""+username+"\",\n")

      #   f.write("\t\"name\": ")
      #   f.write("\""+request.form.get('nombre')+"\",\n")

      #   f.write("\t\"surname\": ")
      #   f.write("\""+request.form.get('apellidos')+"\",\n")

      #   contraseniaCifrada = md5.new(request.form.get('contrasenia')).hexdigest()
      #   f.write("\t\"password\": ")
      #   f.write("\""+contraseniaCifrada+"\",\n")

      #   f.write("\t\"email\": ")
      #   f.write("\""+request.form.get('correo')+"\",\n")

      #   f.write("\t\"creditcard\": ")
      #   f.write("\""+request.form.get('tarjeta')+"\",\n")

      #   f.write("\t\"secretno\": ")
      #   f.write("\""+request.form.get('secretnum')+"\",\n")

      #   f.write("\t\"saldo\": ")
      #   f.write(str(random.randint(1,100))+"\n}")
      #   session['username']=username
      return index()


    return render_template('registro.html', existe=None)

  else:
    return render_template('registro.html', existe=None)

@app.route('/cuenta/', methods = ['POST', 'GET'])
def cuenta():
  if('username' in session):
    #root=app.root_path + '/data/usuarios/'
    #ruta = root+session['username']+"/data.json"
    #datosUsuario = json.load(open(ruta))
    datosUsuario = connection.execute("select * " + \
      "from customers where username = \'" + \
      session['username'] + "\'").fetchone()

    if(request.method=='POST'):
      incr=int(request.form.get('quantity'))
      newSaldo=datosUsuario['income']+incr
      #with open(ruta, "w") as jfile:
      #  json.dump(datosUsuario, jfile)
      connection.execute("update customers " + \
        "set income = " + str(newSaldo))
      datosUsuario = connection.execute("select * " + \
      "from customers where username = \'" + \
      session['username'] + "\'").fetchone()
    return render_template('cuenta.html',log = datosUsuario)
  else:
    return render_template('cuenta.html',log = None)

@app.route('/finalizarCompra/')
def finalizarCompra():
  films_cat = json.load(open(app.root_path + '/data/catalogo.json'))['peliculas']
  try:
    carrito = session['carrito']
  except KeyError:
    carrito=[]
    sumPrice=0
  else:
    sumPrice = 0
    carrito = [x for x in carrito if x[0] in films_cat]
    for film in carrito:
      sumPrice += (film[0]['precio']*film[1])
  root=app.root_path + '/data/usuarios/'
  ruta = root+session['username']+"/data.json"
  saldo = json.load(open(ruta))['saldo']
  if('username' in session):
    return render_template('finalizarCompra.html', films = carrito, sumPrice = sumPrice, log = session['username'], saldo=saldo)
  else:
    return render_template('finalizarCompra.html', films = carrito, sumPrice = sumPrice, log = None, saldo=None)

@app.route('/historialCompras/')
def historialCompras():
  if('username' in session):
    root=app.root_path +'/data/usuarios/'
    ruta = root+session['username']+"/historial.json"
    historialUsuario = json.load(open(ruta))['peliculas']
    fechas = []
    for film in historialUsuario:
      if film['fechaCompra'] not in fechas:
        fechas.append(film['fechaCompra'])

    return render_template('historialCompras.html', films = historialUsuario, log = session['username'], fechas=fechas)
  else:
    return render_template('historialCompras.html', films = None, log = None)

@app.route('/pelicula/<path:name>', methods = ['POST', 'GET'])
def pelicula(name, methods = ['POST', 'GET']):
  if request.method=='GET':
    film = connection.execute("select * \
          from products as p, imdb_movies as f, imdb_moviegenres AS g\
          where p.prod_id=" + str(name) + " AND f.movieid=g.movieid AND p.movieid=f.movieid;").fetchall()[0]
    print film
    if('username' in session):
      return render_template('pelicula.html', film = film, log = session['username'])
    else:
      return render_template('pelicula.html', film = film, log = None)
    if('username' in session):
      return render_template('pelicula.html', film = None, log = session['username'])
    else:
      return render_template('pelicula.html', film = None, log = None)

  if request.method=='POST':
    for film in films:
      if(int(name) == film['prod_id']):
        # Si el usuario no esta loggeado, metemos el carrito en la sesion
        if('username' in session):
            # Si no hay carrito
            try:
              carrito=session['carrito']
            except KeyError:
              # Si no hay carrito
              session['carrito']=[]
              carrito=session['carrito']
            # Buscamos la pelicula en el carrito

            for i in range(len(carrito)):
              # Si la encontramos en el carrito
              if carrito[i][0]['prod_id']==film['prod_id']:
                carrito[i][1]+=int(request.form['quantity'])
                session['carrito']=carrito
                return redirect(url_for("carrito"))

              # Si no la hemos encontrado en el carrito

            session['carrito']=carrito + [[film, int(request.form['quantity'])]]
        # Si el usuario esta loggeado metemos el carrito en la base de datos
        else:
            connection.execute("insert into orderdetails \
                (prod_id, price, quantity)")
        return redirect(url_for("carrito"))

    return redirect(url_for("carrito"))

@app.route('/logout/')
def logout():
  session.clear()
  return redirect(url_for("index"))

@app.route('/contador', methods=['POST'])
def contador():
    number=''
    for muda in range(4):
        number+=str(random.randint(0,9))
    return number

@app.route('/confirmar/')
def confirmar():
    # films_cat = json.load(open(app.root_path +'/data/catalogo.json'))['peliculas']
    # root=app.root_path +'/data/usuarios/'
    # ruta = root+session['username']+"/data.json"
    # rutaHistorial = root+session['username']+"/historial.json"
    #saldo = list(connection.execute("select income from customers where username = \'" + \
    #  session['username'] + "\';"))[0]
    #usuario = json.load(open(ruta))
    usuario = connection.execute("select * from customers where username = \'" + \
      session['username'] + "\';").fetchone()
    historial = connection.execute("select * from imdb_movies," + \
        "(select movieid from orders, orderdetails where customerid = \'" + \
        usuario['customerid'] + "\' and orders.orderid = orderdetails.orderid)" + \
        " as moviesOfUser where imdb_movies.movieid = moviesOfUser.movieid").fetchall()
    saldo = usuario['income']
    fecha = datetime.date.today()
    films_cat = connection.execute("select * from imdb_movies").fetchall()
    try:
        carrito = session['carrito']
    except KeyError:
        carrito=[]
        sumPrice=0
    else:
        sumPrice = 0
        carrito = [x for x in carrito if x[0] in films_cat]
    for film in carrito:
        sumPrice += (film[0]['precio']*film[1])
        flag=0
        for peli in historial:
          if film[0]['id'] == peli['id'] and peli['fechaCompra'] == str(fecha):
            peli['cantidad'] += film[1]
            flag=1
            break
        if flag== 0:
          film[0]['cantidad'] = film[1]
          film[0]['fechaCompra']=str(fecha)
          #historial['peliculas'].append(film[0])

        if sumPrice > saldo:
            return redirect(url_for("index"))

    saldo = saldo-sumPrice
    session['carrito']=[]
    connection.execute("update customers set income = " + str(saldo))
    #with open(rutaHistorial, "w") as jfile:
    #    json.dump(historial, jfile)

    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
