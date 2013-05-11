from .models import DBSession, User
#USERS = {'editor' : 'editor', 'viewer' : 'viewer'}
#GROUPS = {'editor' : ['group:editors']}

def groupfinder(userid, request):
    #if userid in USERS:
        #return GROUPS.get(userid, [])
    user = DBSession.query(User).filter_by(user_name=userid).first()
    return [user.user_group]
