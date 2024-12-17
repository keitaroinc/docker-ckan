start:
	docker compose build
	docker compose up -d 

prune:
	docker compose down 
	docker volume rm compose_ckan_data
	docker volume rm compose_solr_data
	docker volume rm compose_pg_data