from flask import Flask, g, render_template, request, redirect, make_response
from metafilter.model import Node, Query, Session, set_dsn
from metafilter.model import queries, nodes
import logging

LOG = logging.getLogger(__name__)
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

@app.route('/query')
@app.route('/query/<path:query>')
def query(query="root"):
   from metafilter.model.nodes import from_incremental_query
   result = from_incremental_query(g.sess, query)
   try:
      result = result.order_by( [Node.mimetype != 'other/directory', Node.uri ] )
   except Exception, exc:
      LOG.info(exc)

   return render_template("entries.html", entries=result, query=query)

@app.route('/thumbnail/<path>')
def thumbnail(path):
   import Image
   from cStringIO import StringIO
   node = nodes.by_path(g.sess, path)
   try:
      im = Image.open(node.uri)
      im.thumbnail((128, 128), Image.ANTIALIAS)
      tmp = StringIO()
      im.save(tmp, "JPEG")
      response = make_response(tmp.getvalue())
      response.headers['Content-Type'] = 'image/jpeg'
      return response
   except Exception, exc:
      return str(exc)

@app.route('/download/<path>')
def download(path):
   node = nodes.by_path(g.sess, path)
   response = make_response(open(node.uri,'rb').read())
   response.headers['Content-Type'] = node.mimetype
   return response

@app.route('/set_rating', methods=["POST"])
def set_rating():
   from metafilter.model.nodes import set_rating
   set_rating(request.form["path"], int(request.form['value']))
   return "OK"

@app.route('/new_query', methods=["POST"])
def new_query():
   qry = Query(request.form['query'])
   g.sess.add(qry)
   return redirect(request.referrer)

@app.route("/")
def list_queries():
   qry = g.sess.query(Query)
   qry = qry.order_by(Query.query)

   return render_template("queries.html", saved_queries=qry)

@app.route("/save_query", methods=["POST"])
def save_query():
   old_query = request.form['id']
   new_query = request.form['value']
   queries.update( g.sess, old_query, new_query )
   return new_query

@app.route("/save_tags", methods=["POST"])
def save_tags():
   uri = request.form['id']
   tags_value = request.form['value']
   tags = [x.strip() for x in tags_value.split(',')]
   nodes.set_tags( g.sess, uri, tags )
   return ', '.join(tags)

@app.route("/delete_query/<query>")
def delete_query(query):
   queries.delete( g.sess, query )
   return "OK"

if __name__ == "__main__":
   app.debug = True
   logging.basicConfig(level=logging.DEBUG)
   set_dsn("postgresql://filemeta:filemeta@localhost/filemeta_old")
   app.run(host="0.0.0.0", port=8181)
