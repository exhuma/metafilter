from flask import Flask, g, render_template
from metafilter.model import Node, Query, Session, set_dsn
app = Flask(__name__)

class FlaskConfig(object):
   DEBUG=True
   SECRET_KEY='YSY*H3ZGFC-;@8F.QG*V@M9<MTXF=?N(OR<6O.%CKZD=\CM(O'

app.config.from_object(FlaskConfig())

@app.before_request
def before_request():
   g.sess = Session()

@app.after_request
def after_request(response):
   g.sess.commit()
   g.sess.close()
   return response

@app.route("/show_entries/<query>")
@app.route("/show_entries/<query>/<path:parent_path>")
def show_entries(parent_path=None, query=None):
   from metafilter.model.nodes import from_query
   if parent_path:
      parent_path = "/"+parent_path
   result = from_query(g.sess, parent_path, query)
   return render_template("entries.html", entries=result, query=query)

@app.route('/query/<path:query>')
def query(query):
   from metafilter.model.nodes import from_query2
   result = from_query2(g.sess, query)
   return render_template("entries.html", entries=result, query=query)

@app.route('/set_rating/<path>/<int:value>')
def set_rating(path, value):
   from metafilter.model.nodes import set_rating
   set_rating(path, value)
   return "OK"

@app.route("/")
def list_queries():
   qry = g.sess.query(Query)
   qry = qry.order_by(Query.query)

   return render_template("queries.html", saved_queries=qry)

if __name__ == "__main__":
   app.debug = True
   set_dsn("postgresql://filemeta:filemeta@localhost/filemeta_old")
   app.run(host="0.0.0.0", port=8181)
