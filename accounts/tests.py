from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.test import TestCase
from django.urls import reverse

from accounts.models import Connection
from tweets.models import Tweet

User = get_user_model()


class TestSignupView(TestCase, UserCreationForm):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassrd2354",
            "password2": "testpassrd2354",
        }
        response = self.client.post(self.url, valid_data, follow=True)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, status_code=302)
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])

    def test_failure_post_with_duplicated_user(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "testpassword")
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "testmail",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "test",
            "password2": "test",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn(
            "このパスワードは短すぎます。最低 8 文字以上必要です。",
            form.errors["password2"],
        )

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testusernopass",
            "password2": "testusernopass",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "1604236888",
            "password2": "1604236888",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassward",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testuser")
        self.login = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        response = self.client.post(self.login, {"username": "testuser", "password": "testuser"})
        self.assertRedirects(response, reverse("tweets:home"), status_code=302, target_status_code=200)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        invalid_data = {"username": "testkun", "password": "testuser"}
        response = self.client.post(self.login, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn(
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
            form.errors["__all__"],
        )

    def test_failure_post_with_empty_password(self):
        invalid_data = {"username": "testuser", "password": ""}
        response = self.client.post(self.login, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):

    def setUp(self):
        self.logout = reverse("accounts:logout")

    def test_success_post(self):
        response = self.client.post(self.logout)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("welcome:welcome"),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testesuser",
        )
        self.user2 = User.objects.create(username="testesuser2")
        self.user.set_password("testpassword")
        self.user.set_password("testpassword2")
        self.user.save()
        self.user2.save()
        self.tweet = Tweet.objects.create(user=self.user, title="test_title", content="test_content")
        self.tweet2 = Tweet.objects.create(user=self.user2, title="test_title2", content="test_content2")
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user.username})

    def test_success_get(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["n_follower"], Connection.objects.filter(follower=self.user).count())
        self.assertEqual(response.context["n_following"], Connection.objects.filter(following=self.user).count())
        self.assertEqual(response.context["tweets_list"][0], Tweet.objects.get(user=self.user))
        self.assertTemplateUsed(response, "tweets/profile.html")


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


class TestFollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.user2 = User.objects.create(username="testuser2", password="testpassword2")
        self.url = reverse("accounts:follow", kwargs={"username": self.user2.username})
        self.wrongurl = reverse("accounts:follow", kwargs={"username": "IamUFO"})
        self.selfurl = reverse("accounts:follow", kwargs={"username": self.user.username})

    def test_success_post(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tweets:home"), status_code=302, target_status_code=200)
        self.assertTrue(Connection.objects.filter(follower=self.user, following=self.user2).exists())

    def test_failure_post_with_not_exist_user(self):
        self.client.force_login(self.user)
        response = self.client.post(self.wrongurl)
        self.assertFalse(Connection.objects.filter(follower=self.user).exists())
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_self(self):
        self.client.force_login(self.user)
        response = self.client.post(self.selfurl)
        self.assertFalse(Connection.objects.filter(follower=self.user, following=self.user).exists())
        self.assertEqual(response.status_code, 400)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.user2 = User.objects.create(username="testuser2", password="testpassword2")
        self.user3 = User.objects.create(username="testuser3", password="testpassword3")
        self.connection = Connection.objects.create(follower=self.user, following=self.user2)
        self.url = reverse("accounts:unfollow", kwargs={"username": self.user2.username})
        self.wrongurl = reverse("accounts:unfollow", kwargs={"username": "IamUFO"})
        self.selfurl = reverse("accounts:unfollow", kwargs={"username": self.user.username})

    def test_success_post(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tweets:home"), status_code=302, target_status_code=200)
        self.assertFalse(Connection.objects.filter(follower=self.user, following=self.user2).exists())

    def test_failure_post_with_self(self):
        self.client.force_login(self.user)
        response = self.client.post(self.wrongurl)
        self.assertTrue(Connection.objects.filter(follower=self.user, following=self.user2).exists())
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_incorrect_user(self):
        self.client.force_login(self.user)
        response = self.client.post(self.selfurl)
        self.assertTrue(Connection.objects.filter(follower=self.user, following=self.user2).exists())
        self.assertEqual(response.status_code, 400)


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.user2 = User.objects.create(username="testuser2", password="testpassword2")
        self.url = reverse("accounts:following_list", kwargs={"username": self.user2.username})

    def test_success_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.user2 = User.objects.create(username="testuser2", password="testpassword2")
        self.url = reverse("accounts:following_list", kwargs={"username": self.user2.username})

    def test_success_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
