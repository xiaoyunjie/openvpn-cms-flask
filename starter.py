from app.app import create_app

import sqlalchemy

app = create_app(environment='production')

@app.route('/', methods=['GET'], strict_slashes=False)
def lin_slogan():
    return """<h1>OPENVPN<h1>"""


if __name__ == '__main__':
    # app.run(debug=True, host="0.0.0.0")
    app.run(host="0.0.0.0")
