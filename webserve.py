from flask import Flask, g, render_template
from model import Node, Query, Session
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
   from model.nodes import from_query
   if parent_path:
      parent_path = "/"+parent_path
   result = from_query(g.sess, parent_path, query)
   return render_template("entries.html", entries=result, query=query)

@app.route("/")
def list_queries():
   qry = g.sess.query(Query)
   qry = qry.order_by(Query.query)

   return render_template("queries.html", saved_queries=qry)

if __name__ == "__main__":
   app.debug = True
   app.run(host="0.0.0.0")
