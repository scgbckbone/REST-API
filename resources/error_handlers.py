
api_errors = {
    "BoundaryReachedError": {
        "message": "Max rate limit reached",
        "status": 429
    },
    "RedisOperationalError": {
        "message": "Internal Server Error",
        "status": 500
    }
}






# from ..app_alchemy import api, app
#
#
# @api.errorhandler(Exception)
# def handle_error(e):
#
#     return {"error": str(e)}
#
#

#
#
# @app.handle_exception(Exception)
# def handle_it_app(e):
#     return {"error": str(e.args[0])}
#
#
# @api.handle_exception(Exception)
# def handle_it(e):
#     return {"error": str(e.args[0])}
