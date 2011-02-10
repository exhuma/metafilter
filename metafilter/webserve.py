from flask import Flask, g, render_template, request, redirect, make_response, url_for
from metafilter.model import Node, Query, Session, set_dsn
from metafilter.model import queries, nodes
from optparse import OptionParser
import logging

LOG = logging.getLogger(__name__)
app = Flask(__name__)

class FlaskConfig(object):
    DEBUG = True
    SECRET_KEY = 'YSY*H3ZGFC-;@8F.QG*V@M9<MTXF=?N(OR<6O.%CKZD=\CM(O'

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
    result = nodes.subdirs(g.sess, query)
    if not result:
        result = []
    result += nodes.from_incremental_query(g.sess, query).order_by(Node.path).all()

    try:
        result = result.order_by( [Node.mimetype != 'other/directory', Node.uri ] )
    except Exception, exc:
        LOG.info(exc)

    return render_template("entries.html", entries=result, query=query)

@app.route('/delete_from_disk/<path>')
def delete_from_disk(path):
    nodes.delete_from_disk(g.sess, path)
    return redirect(request.referrer)

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

@app.route('/tag_all', methods=["POST"])
def tag_all():
    node_qry = nodes.from_incremental_query(g.sess, request.form["query"])
    tags = []
    for tagname in request.form['tags'].split(','):
        tagname = tagname.strip()
        tag = nodes.Tag.find(g.sess, tagname)
        if not tag:
            tag = nodes.Tag(tagname)
        tags.append(tag)

    for node in node_qry:
        if node.is_dir():
            continue
        node.tags.extend(tags)

    return redirect(url_for('query', query=request.form['query']))

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

@app.route("/duplicates")
def duplicates():
    return render_template("duplicates.html",
            duplicates=nodes.duplicates(g.sess))

@app.route("/acknowledge_duplicate/<md5>")
def acknowledge_duplicate(md5):
    nodes.acknowledge_duplicate(g.sess, md5)
    return redirect(url_for('duplicates'))

@app.route("/view/<path:path>/<int:index>")
def view(path, index=0):
    return render_template("view.html",
            node = nodes.one_image(g.sess, path, index),
            index = index,
            )

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-d", "--dsn", dest="dsn",
                            help="Database DSN (see sqlalchemy docs for details)",
                            metavar="DSN")
    parser.add_option("-p", "--port", dest="port",
                            help="Port on which the webserver will run",
                            default = 8080)
    parser.add_option("-i", "--iface", dest = "interface",
                            help = "Network interface address to which the "
                            "process will be bound",
                            default = "127.0.0.1")
    (options, args) = parser.parse_args()

    app.debug = True
    logging.basicConfig(level=logging.DEBUG)

    if options.dsn:
       dsn = options.dsn
    else:
       dsn = "postgresql://filemeta:filemeta@localhost/filemeta_old"

    set_dsn(dsn)
    app.run(host=options.interface, port=int(options.port))
