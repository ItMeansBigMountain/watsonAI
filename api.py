import flask
from flask import request, jsonify , render_template
import json
import requests



# SETTINGS
application = flask.Flask(__name__)
application.config["DEBUG"] = True



# TODO
    # create api key
    # get this to run on the same server as disc bot
    # login administration
    # stripe $10 payment


# homepage
@application.route('/', methods=['GET'])
def home():
    if 'server' in request.args:
        server_id = str(request.args['server'])
        with open( "{}.json".format(server_id) , 'r' ) as db:
            data = json.load(db)
        return jsonify(data)
    else:
        return '<h1>Trpistan</h1><p>we are watching...</p>'




# 404 ERROR
@application.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found...</p>", 404



application.run(host = '0.0.0.0' , port = 8080)



