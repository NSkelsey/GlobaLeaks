import time
from cyclone.util import ObjectDict as OD

from twisted.internet.defer import inlineCallbacks
from globaleaks.tests import helpers
from globaleaks import settings
from globaleaks.handlers import authentication
from globaleaks.rest import errors

class TestAuthentication(helpers.TestHandler):
    _handler = authentication.AuthenticationHandler

    def login(self, role='admin', user_id=None):
        if not user_id:
            if role == 'admin':
                user_id = 'admin'
            elif role == 'wb':
                user_id = self.dummySubmission['submission_gus']
            elif role == 'receiver':
                user_id = self.dummyReceiver['receiver_gus']
        session = OD(timestamp=time.time(),id='spam',
                role=role, user_id=user_id)
        settings.sessions[session.id] = session
        return session.id

    @inlineCallbacks
    def test_successful_admin_login(self):
        handler = self.request({
           'username': 'admin',
           'password': 'globaleaks',
           'role': 'admin'
        })
        success = yield handler.post()
        self.assertTrue('session_id' in self.responses[0])

    @inlineCallbacks
    def test_successful_receiver_login(self):
        handler = self.request({
           'username': self.dummyReceiver['username'],
           'password': self.dummyReceiver['password'],
           'role': 'receiver'
        })
        success = yield handler.post()
        self.assertTrue('session_id' in self.responses[0])

    @inlineCallbacks
    def test_successful_whistleblower_login(self):
        handler = self.request({
           'username': '',
           'password': self.dummyWBTip,
           'role': 'wb'
        })
        success = yield handler.post()
        self.assertTrue('session_id' in self.responses[0])

    @inlineCallbacks
    def test_successful_admin_logout(self):
        handler = self.request()
        handler.request.headers['X-Session'] = self.login('admin')

        success = yield handler.delete()
        self.assertTrue(handler.current_user is None)

    @inlineCallbacks
    def test_successful_receiver_logout(self):
        handler = self.request()
        handler.request.headers['X-Session'] = self.login('receiver')

        success = yield handler.delete()
        self.assertTrue(handler.current_user is None)

    @inlineCallbacks
    def test_successful_whistleblower_logout(self):
        handler = self.request()
        handler.request.headers['X-Session'] = self.login('wb')

        success = yield handler.delete()
        self.assertTrue(handler.current_user is None)


    def test_invalid_admin_login_wrong_password(self):
        handler = self.request({
           'username': 'admin',
           'password': 'INVALIDPASSWORD',
           'role': 'admin'
        })
        d = handler.post()
        self.assertFailure(d, errors.InvalidAuthRequest)
        return d

    def test_invalid_receiver_login_wrong_password(self):
        handler = self.request({
           'username': 'receiver',
           'password': 'INVALIDPASSWORD',
           'role': 'receiver'
        })
        d = handler.post()
        self.assertFailure(d, errors.InvalidAuthRequest)
        return d

    def test_invalid_whistleblower_login_wrong_receipt(self):
        handler = self.request({
           'username': '',
           'password': 'INVALIDPASSWORD',
           'role': 'wb'
        })
        d = handler.post()
        self.assertFailure(d, errors.InvalidAuthRequest)
        return d

    def test_invalid_input_format_missing_role(self):
        handler = self.request({
           'username': '',
           'password': '',
        })
        d = handler.post()
        self.assertFailure(d, errors.InvalidInputFormat)
        return d

    def test_invalid_input_format_wrong_role(self):
        handler = self.request({
           'username': 'ratzinger',
           'password': '',
           'role': 'pope'
        })
        d = handler.post()
        self.assertFailure(d, errors.InvalidInputFormat)
        return d

