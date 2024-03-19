
def set_access_control_allows(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type, Authorization, Origin,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS"
    )
    return response