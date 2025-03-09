from django.contrib.auth.base_user import BaseUserManager



class CustomManager(BaseUserManager):
    def create_user(self, email, password, **extrafields):
        if not email:
            raise ValueError("Email is requried")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extrafields)
        user.set_password(password)
        user.save(using=self._db)  # Ensures compatibility with multiple databases

        return user
    
    def create_superuser(self, email, password, **extrafields):
        extrafields.setdefault("is_staff", True)
        extrafields.setdefault("is_superuser", True)
        extrafields.setdefault("is_active", True)

        # remove city from superadmin
        extrafields.pop('city', None)


        return self.create_user(email, password, **extrafields)

