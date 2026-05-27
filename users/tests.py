import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from projects.models import Project


User = get_user_model()


class MediaRootMixin:
    @classmethod
    def setUpClass(cls):
        cls._temp_media = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._temp_media)
        cls._override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override.disable()
        shutil.rmtree(cls._temp_media, ignore_errors=True)


class UserFlowTests(MediaRootMixin, TestCase):
    def test_registration_redirects_to_login_and_creates_avatar(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "name": "Иван",
                "surname": "Сидоров",
                "email": "ivan@example.com",
                "phone": "89990000001",
                "password": "StrongPass123",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        user = User.objects.get(email="ivan@example.com")
        self.assertTrue(bool(user.avatar))
        self.assertEqual(user.phone, "+79990000001")

    def test_registration_requires_phone(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "name": "Иван",
                "surname": "Сидоров",
                "email": "ivan2@example.com",
                "phone": "",
                "password": "StrongPass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Обязательное поле")

    def test_registration_shows_error_for_invalid_phone(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "name": "Иван",
                "surname": "Сидоров",
                "email": "ivan3@example.com",
                "phone": "12345",
                "password": "StrongPass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.",
        )

    def test_login_works_with_email(self):
        password = "StrongPass123"
        user = User.objects.create_user(
            email="anna@example.com",
            password=password,
            name="Анна",
            surname="Иванова",
            phone="+79990000010",
        )

        response = self.client.post(
            reverse("users:login"),
            data={"email": user.email, "password": password},
        )

        self.assertRedirects(response, reverse("projects:list"))

    def test_profile_form_normalizes_phone(self):
        user = User.objects.create_user(
            email="anna@example.com",
            password="StrongPass123",
            name="Анна",
            surname="Иванова",
            phone="+79990000011",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:edit-profile"),
            data={
                "name": "Анна",
                "surname": "Иванова",
                "about": "Backend developer",
                "phone": "89990000000",
                "github_url": "https://github.com/anna-example",
            },
        )

        self.assertRedirects(
            response,
            reverse("users:detail", kwargs={"user_id": user.id}),
        )
        user.refresh_from_db()
        self.assertEqual(user.phone, "+79990000000")

    def test_profile_form_rejects_non_github_url(self):
        user = User.objects.create_user(
            email="anna@example.com",
            password="StrongPass123",
            name="Анна",
            surname="Иванова",
            phone="+79990000012",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:edit-profile"),
            data={
                "name": "Анна",
                "surname": "Иванова",
                "about": "Backend developer",
                "phone": "+79990000000",
                "github_url": "https://gitlab.com/anna-example",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Укажите ссылку на GitHub.")

    def test_profile_form_requires_phone(self):
        user = User.objects.create_user(
            email="anna@example.com",
            password="StrongPass123",
            name="Анна",
            surname="Иванова",
            phone="+79990000013",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:edit-profile"),
            data={
                "name": "Анна",
                "surname": "Иванова",
                "about": "Backend developer",
                "phone": "",
                "github_url": "https://github.com/anna-example",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Обязательное поле")

    def test_profile_form_shows_error_for_invalid_phone(self):
        user = User.objects.create_user(
            email="anna@example.com",
            password="StrongPass123",
            name="Анна",
            surname="Иванова",
            phone="+79990000017",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:edit-profile"),
            data={
                "name": "Анна",
                "surname": "Иванова",
                "about": "Backend developer",
                "phone": "12345",
                "github_url": "https://github.com/anna-example",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.",
        )

    def test_user_list_filter_participants_of_my_projects(self):
        owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123",
            name="Олег",
            surname="Орлов",
            phone="+79990000014",
        )
        participant = User.objects.create_user(
            email="member@example.com",
            password="StrongPass123",
            name="Мила",
            surname="Миронова",
            phone="+79990000015",
        )
        project = Project.objects.create(
            name="Team Finder",
            description="Проект",
            owner=owner,
        )
        project.participants.add(participant)
        self.client.force_login(owner)

        response = self.client.get(
            reverse("users:list"),
            data={"filter": "participants-of-my-projects"},
        )

        self.assertContains(response, "Мила Миронова")
        page_ids = [
            participant.id
            for participant in response.context["page_obj"].object_list
        ]
        self.assertEqual(page_ids, [participant.id])

    def test_change_password_updates_credentials(self):
        user = User.objects.create_user(
            email="anna@example.com",
            password="StrongPass123",
            name="Анна",
            surname="Иванова",
            phone="+79990000016",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("users:change-password"),
            data={
                "old_password": "StrongPass123",
                "new_password1": "NewStrongPass123",
                "new_password2": "NewStrongPass123",
            },
        )

        self.assertRedirects(
            response,
            reverse("users:detail", kwargs={"user_id": user.id}),
        )
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewStrongPass123"))

    def test_user_str_returns_full_name(self):
        user = User.objects.create_user(
            email="anna@example.com",
            password="StrongPass123",
            name="Анна",
            surname="Иванова",
            phone="+79990000018",
        )

        self.assertEqual(str(user), "Анна Иванова")

    def test_seed_demo_data_command_creates_users_and_projects(self):
        call_command("seed_demo_data")

        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Project.objects.count(), 3)
