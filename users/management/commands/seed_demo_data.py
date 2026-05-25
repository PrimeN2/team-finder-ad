from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Создает тестовых пользователей и проекты для ручной проверки."

    def handle(self, *args, **options):
        demo_users = [
            {
                "email": "anna@example.com",
                "password": "TeamFinder123",
                "name": "Анна",
                "surname": "Иванова",
                "phone": "+79990000001",
                "about": "Python backend developer",
                "github_url": "https://github.com/anna-example",
            },
            {
                "email": "boris@example.com",
                "password": "TeamFinder123",
                "name": "Борис",
                "surname": "Петров",
                "phone": "+79990000002",
                "about": "UI/UX designer",
                "github_url": "https://github.com/boris-example",
            },
            {
                "email": "maria@example.com",
                "password": "TeamFinder123",
                "name": "Мария",
                "surname": "Соколова",
                "phone": "+79990000003",
                "about": "Frontend engineer",
                "github_url": "https://github.com/maria-example",
            },
        ]
        created_users = []
        for payload in demo_users:
            defaults = {
                "name": payload["name"],
                "surname": payload["surname"],
                "phone": payload["phone"],
                "about": payload["about"],
                "github_url": payload["github_url"],
            }
            user, created = User.objects.get_or_create(
                email=payload["email"],
                defaults=defaults,
            )
            if created:
                user.set_password(payload["password"])
                user.ensure_avatar()
                user.save()
            created_users.append(user)
            action = "создан" if created else "уже существует"
            self.stdout.write(f"Пользователь {user.email} {action}.")

        project_specs = [
            (
                created_users[0],
                "Сервис поиска команды",
                "Платформа для поиска специалистов в pet-проекты.",
                "https://github.com/anna-example/teamfinder",
            ),
            (
                created_users[1],
                "Дизайн-система для стартапа",
                "Набор UI-компонентов и гайдов для команды продукта.",
                "https://github.com/boris-example/design-system",
            ),
            (
                created_users[2],
                "Трекер привычек",
                "Веб-приложение для командных челленджей и привычек.",
                "https://github.com/maria-example/habit-tracker",
            ),
        ]

        projects = []
        for owner, name, description, github_url in project_specs:
            project, created = Project.objects.get_or_create(
                owner=owner,
                name=name,
                defaults={
                    "description": description,
                    "github_url": github_url,
                    "status": Project.STATUS_OPEN,
                },
            )
            projects.append(project)
            action = "создан" if created else "уже существует"
            self.stdout.write(f"Проект '{project.name}' {action}.")

        projects[0].participants.add(created_users[1], created_users[2])
        projects[1].participants.add(created_users[0])
        created_users[0].favorites.add(projects[1], projects[2])
        created_users[1].favorites.add(projects[0])
        created_users[2].favorites.add(projects[0], projects[1])

        self.stdout.write(self.style.SUCCESS("Тестовые данные готовы."))
