from django.contrib.auth.models import BaseUserManager
import random

class MyUserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, username=None, password=None,):

        if email is None and phone is None:
            raise ValueError('Users must have an email address or phone Number')
        
        # username is not mendatory for buyer(set username to provided info)
        # during changing email or phone make sure if username is created by default -
        # with the email or phone number than create option to change username also with provided info
        if username is None:
            if email is None:
                user = self.model(
                    email=email,
                    phone=phone,
                    username=phone + str(random.randrange(1, 1000)),
                )
            else:
                user = self.model(
                    email=email,
                    phone=phone,
                    username=email + str(random.randrange(1, 1000)),
                )
        else:
            user = self.model(
            email=email,
            phone=phone,
            username=username,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, phone=None, password=None,):
        user = self.create_user(
            username=username,
            email=username,
            phone=phone,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
