local_up:
	docker compose up -d
	docker compose run backend python manage.py migrate
	docker compose run backend python manage.py shell -c "from recipes.models import DBUser; DBUser.objects.filter(username='admin').exists() or DBUser.objects.create_superuser('admin','admin@example.com','password123')"

load_csv:
	docker compose run backend python manage.py csv_loader