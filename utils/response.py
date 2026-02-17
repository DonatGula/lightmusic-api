from flask import jsonify

def success(data, message="ok"):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    })

def error(message, code=400):
    return jsonify({
        "status": "error",
        "message": message,
        "data": None
    }), code