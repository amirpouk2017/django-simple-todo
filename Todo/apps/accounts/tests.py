from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthAPITest(APITestCase):
    def setUp(self):
        self.username = "admin"
        self.password = "Admin123456"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
        )

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------

    def test_register_success(self):
        response = self.client.post(
            "/api/signup/",
            {
                "username": "user2",
                "password": "Password123",
                "password2": "Password123",
                "email": "user2@test.com",
                "first_name": "User",
                "last_name": "Two",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="user2").exists())

    def test_register_duplicate_username(self):
        response = self.client.post(
            "/api/signup/",
            {
                "username": self.username,
                "password": "Password123",
                "password2": "Password123",
                "email": "new@test.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        response = self.client.post(
            "/api/signup/",
            {
                "username": "user3",
                "password": "Password123",
                "password2": "Password999",
                "email": "user3@test.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email(self):
        response = self.client.post(
            "/api/signup/",
            {
                "username": "user3",
                "password": "Password123",
                "password2": "Password123",
                "email": "new@test.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def test_login_success(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh_token", response.cookies)

    def test_login_wrong_password(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": "wrong",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_username(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": "unknown",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------
    # Me
    # ------------------------------------------------------------------

    def test_me_success(self):
        login = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        access = login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get("/api/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.username)

    def test_me_without_token(self):
        response = self.client.get("/api/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def test_refresh_success(self):
        login = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        refresh = login.cookies["refresh_token"].value
        print(refresh)

        self.client.cookies["refresh_token"] = refresh

        response = self.client.post("/api/refresh/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh_token", response.cookies)

    def test_refresh_without_cookie(self):
        response = self.client.post("/api/refresh/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_invalid_cookie(self):
        self.client.cookies["refresh_token"] = "invalid"

        response = self.client.post("/api/refresh/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def test_logout_success(self):
        login = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        access = login.data["access"]
        refresh = login.cookies["refresh_token"].value

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        self.client.cookies["refresh_token"] = refresh

        response = self.client.post("/api/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_without_access_token(self):
        response = self.client.post("/api/logout/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_refresh_cookie(self):
        login = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        access = login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post("/api/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_token_revoked_after_logout(self):
        login = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        access = login.data["access"]
        refresh = login.cookies["refresh_token"].value

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        self.client.cookies["refresh_token"] = refresh

        self.client.post("/api/logout/")

        response = self.client.get("/api/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
