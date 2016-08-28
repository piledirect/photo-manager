
from flask import jsonify, Response, request

from .. import app
from ..documents import PhotoDocument, PhotoSearch
from ..models import Photo

@app.route('/api/photos')
def photos():
    filters = {}
    if "date" in request.args:
        filters["date"] = request.args["date"]
    if "aperture" in request.args:
        filters["aperture"] = request.args["aperture"]
    

    date = request.args.get("date", None)
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))
    search = request.args.get("filter", None)

    if limit > 20:
        limit = 20

    order = request.args.get("order", "-date")

    q = PhotoSearch(query=search, filters=filters).build_search()
    
    response = q.sort(order)[offset:limit].execute()

    return jsonify({
        'facets': dict([(key, [{'value' : f[0], 'selected' : f[2], 'count' : f[1]} for f in getattr(response.facets, key)]) for key, val in PhotoSearch.facets.items()]), 
        'photos' : [d.extended_dict() for d in response.hits], 
        'results' : response.hits.total,
        'query' : q.to_dict()
    })
