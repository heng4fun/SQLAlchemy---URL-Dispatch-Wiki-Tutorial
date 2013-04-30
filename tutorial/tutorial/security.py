USERS = {'editor' : 'editor', 'view' : 'viewer'}
GROUPS = {'editor' : ['group:editor']}

def groupfinder(useid, request):
    if useid in USERS:
        return GROUPS.get(useid, [])
