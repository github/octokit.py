import uritemplate

class Users(object):
    def get_user(self, inputUser=None, **kwargs):
        if inputUser:
            return self.user(user=inputUser)
        else:
            return self.current_user

    def get_all_users(self):
        return self.user.get()
