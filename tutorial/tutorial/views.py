import re
from docutils.core import publish_parts

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    has_permission,
    Allowed,
    )

from .models import (
    DBSession,
    Page,
    User,
    Posts,
    RootFactory,
    )
    
from sqlalchemy.orm.exc import NoResultFound

from datetime import datetime

#from security import USERS
# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(route_name='view_wiki')
def view_wiki(request):
    return HTTPFound(location = request.route_url('view_page',
                                                  pagename='FrontPage'))

@view_config(route_name='view_page', renderer='templates/view.pt')
def view_page(request):
    all_posts = []
    pagename = request.matchdict['pagename']
    page = DBSession.query(Page).filter_by(name=pagename).first()
    if page is None:
        return HTTPNotFound('No such page')
    editor = has_permission('edit',RootFactory,request)    
    def check(match):
        word = match.group(1)
        exists = DBSession.query(Page).filter_by(name=word).all()
        if exists:
            view_url = request.route_url('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.route_url('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.route_url('edit_page', pagename=pagename)
    delete_post_url = request.route_url('delete_post', pagename=pagename)
    if 'form.submitted' in request.params:
        DBSession.add(Posts(authenticated_userid(request), pagename, request.params['message'], datetime.now()))
    for post in DBSession.query(Posts).filter_by(page_name=pagename):
        all_posts.append(post)
    
    return dict(page=page,  content=content, all_posts=all_posts, edit_url=edit_url, delete_post_url=delete_post_url, editor = editor,
                logged_in=authenticated_userid(request))

@view_config(route_name='add_page', renderer='templates/edit.pt',
             permission='edit')
def add_page(request):
    name = request.matchdict['pagename']
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(name, body)
        DBSession.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=name))
    save_url = request.route_url('add_page', pagename=name)
    page = Page('', '')
    return dict(page=page, save_url=save_url,
                logged_in=authenticated_userid(request))

@view_config(route_name='edit_page', renderer='templates/edit.pt',
             permission='edit')
def edit_page(request):
    name = request.matchdict['pagename']
    page = DBSession.query(Page).filter_by(name=name).one()
    if 'form.submitted' in request.params:
        page.data = request.params['body']
        DBSession.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=name))
    return dict(
        page=page,
        save_url = request.route_url('edit_page', pagename=name),
        logged_in=authenticated_userid(request),
        )

@view_config(route_name='delete_post',permission='edit')
def delete_post(request):
    pagename = request.matchdict['pagename']
    if 'form.post' in request.params:
        user_name = request.params['user_name']
        post_time = request.params['post_time']
        DBSession.query(Posts).filter_by(user_name=user_name).filter_by(page_name=pagename).filter_by(time=post_time).delete()
        return HTTPFound(location = request.route_url('view_page',pagename=pagename))
 
    
    
@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        try:
            user = DBSession.query(User).filter_by(user_name=login).one()
        except NoResultFound, e:
            print e
            return dict(
        message = 'Wrong username or password! Please check it again.',
        url = request.application_url + '/login',
        came_from = came_from,
        login = '',
        password = '',
        )
        #if USERS.get(login) == password:
        if user.password == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('view_wiki'),
                     headers = headers)
   
    
