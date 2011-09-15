from django.contrib.auth.models import User

def create_users():
  for i in range(0, 1000):
    # create group one and group two.
    username = "user%d-%d" % (i / 500, i % 500)
    user = User.objects.create_user(username, username + "@test.com", password="testuser")
    profile = user.get_profile()
    profile.setup_complete = True
    profile.setup_profile = True
    profile.save()
    
def remove_users():
  for i in range(0, 1000):
    username = "user%d-%d" % (i / 500, i % 500)
    user = User.objects.get(username=username)
    user.delete()