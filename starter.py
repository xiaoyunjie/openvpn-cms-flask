"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from app.app import create_app
# from flask_migrate import Migrate
import sqlalchemy

# app = create_app(environment='development')
app = create_app(environment='production')

# migrate = Migrate(app)

@app.route('/', methods=['GET'], strict_slashes=False)
def lin_slogan():
    return """<h1>OPENVPN<h1>"""


if __name__ == '__main__':
    app.run(debug=True, host="192.168.149.9")
