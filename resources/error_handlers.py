
api_errors = {
    "JWTError": {
        "message": "Invalid Token",
        "status": 401
    },
    "BoundaryReachedError": {
        "message": "Max rate limit reached",
        "status": 429
    },
    "RedisOperationalError": {
        "message": "Internal Server Error",
        "status": 500
    }
}
