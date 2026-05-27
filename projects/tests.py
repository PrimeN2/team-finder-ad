import shutil
import tempfile

from django.contrib.auth import get_user_model
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


class ProjectFlowTests(MediaRootMixin, TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123",
            name="Олег",
            surname="Орлов",
            phone="+79990000020",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="StrongPass123",
            name="Мила",
            surname="Миронова",
            phone="+79990000021",
        )
        self.project = Project.objects.create(
            name="Новый проект",
            description="Описание",
            owner=self.owner,
            status=Project.STATUS_OPEN,
        )

    def test_root_redirects_to_project_list(self):
        response = self.client.get("/")

        self.assertRedirects(response, reverse("projects:list"))

    def test_project_list_uses_pagination(self):
        for index in range(13):
            Project.objects.create(
                name=f"Проект {index}",
                description="Описание",
                owner=self.owner,
            )

        response = self.client.get(reverse("projects:list"))

        self.assertEqual(len(response.context["page_obj"].object_list), 12)
        self.assertTrue(response.context["page_obj"].has_next())

    def test_create_project_requires_login(self):
        response = self.client.get(reverse("projects:create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_create_project_succeeds_for_authenticated_user(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("projects:create"),
            data={
                "name": "Сервис команд",
                "description": "Ищем backend-разработчика",
                "github_url": "https://github.com/owner-example/project",
                "status": Project.STATUS_OPEN,
            },
        )

        created_project = Project.objects.get(name="Сервис команд")
        self.assertRedirects(
            response,
            reverse("projects:detail", kwargs={"project_id": created_project.id}),
        )

    def test_edit_project_available_only_for_owner(self):
        self.client.force_login(self.member)

        response = self.client.get(
            reverse("projects:edit", kwargs={"project_id": self.project.id}),
        )

        self.assertEqual(response.status_code, 404)

    def test_toggle_favorite_adds_project(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse(
                "projects:toggle-favorite",
                kwargs={"project_id": self.project.id},
            )
        )

        self.assertEqual(response.json(), {"status": "ok", "favorited": True})
        self.assertTrue(self.member.favorites.filter(id=self.project.id).exists())

    def test_toggle_participate_adds_member(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse(
                "projects:toggle-participate",
                kwargs={"project_id": self.project.id},
            )
        )

        self.assertEqual(response.json(), {"status": "ok", "participant": True})
        self.assertTrue(
            self.project.participants.filter(id=self.member.id).exists(),
        )

    def test_complete_project_closes_project(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse(
                "projects:complete",
                kwargs={"project_id": self.project.id},
            )
        )

        self.assertEqual(
            response.json(),
            {"status": "ok", "project_status": "closed"},
        )
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_favorites_page_requires_login(self):
        response = self.client.get(reverse("projects:favorites"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_project_str_returns_name(self):
        self.assertEqual(str(self.project), self.project.name)
