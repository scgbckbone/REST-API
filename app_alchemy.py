import os
import sys
from flask import Flask, render_template, jsonify, request
from flask_jwt import JWT
from flask_restful import Api

from resources.items_alchemy import Item, ItemList
from resources.users_alchemy import User_register
from security_alchemy import authenticate, identity
from resources.store_alchemy import Store, StoreList
from resources.contacts_resource import Contact, ContactList
from resources.error_handlers import api_errors
from resources.req_log import logger
from post_man import SMTPPostMan
import postman_conf as config

app = Flask(__name__, template_folder=".", static_folder="assets")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///DATA.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'andrej2154'
api = Api(app, errors=api_errors)

jwt = JWT(app, authenticate, identity)

api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(User_register, '/register')
api.add_resource(Contact, "/call_me/<string:name>")
api.add_resource(ContactList, "/contacts")


ip_addr_set = set()


@app.errorhandler(Exception)
def handle_error_app(e):
    # create file to send as attachment containing last 100 lines from debug.log
    logger.critical("big trap", exc_info=True)
    # try:
    #     os.system(
    #         # "tail -n 100 /var/www/html/items-rest/resources/requests_log/reqlog.log > /home/andrej/tailed_debug_cv.txt"
    #         "tail -n 100 /tmp/req_log.log > /home/scag/tailed_debug_cv.txt"
    #     )
    # except Exception:
    #     logger.critical("Failed to tail log file", exc_info=True)
    #
    # mailer = SMTPPostMan(
    #     smtp_host=config.smtp_host,
    #     smtp_port=config.smtp_port,
    #     addr=config.addr,
    #     pwd=config.pwd
    # )
    #
    # try:
    #     mailer.send_email(
    #         send_to=["virgovica@gmail.com"],
    #         subject="cv alert notification",
    #         attachments=["/home/scag/tailed_debug_cv.txt"]
    #     )
    # except Exception:
    #     logger.critical("Failed to send email", exc_info=True)

    return jsonify({"error": "Internal server error"}), 500


@app.route("/", methods=["GET"])
def render_cv():
    before = len(ip_addr_set)
    visitor_ip = get_real_ip(req_obj=request)
    ip_addr_set.add(visitor_ip)
    if not len(ip_addr_set) == before:
        logger.info("New visitor: {}".format(visitor_ip))
    return render_template("index.html")


def get_real_ip(req_obj):
    return req_obj.environ.get(
        'HTTP_X_FORWARDED_FOR', req_obj.environ.get(
            "X_FORWARDED_FOR", req_obj.environ.get(
                "X-Forwarded-For", req_obj.remote_addr
            )
        )
    )


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    raise RuntimeError()
    return jsonify(
        get_real_ip(req_obj=request)
    ), 200


@app.route("/ipset", methods=["GET"])
def get_ip_set():
    return jsonify(
        {
            "count": len(ip_addr_set),
            "ips": list(ip_addr_set)
        }
    ), 200


if __name__ == '__main__':
    from object_SQLAlchemy import db
    db.init_app(app)
    app.run(port=5000)

