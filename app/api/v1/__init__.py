from flask import Blueprint
from app.api.v1 import openvpn


def create_v1():
    bp_v1 = Blueprint('v1', __name__)
    openvpn.openvpn_api.register(bp_v1)
    return bp_v1
