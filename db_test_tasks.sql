-- С какими актёрами работал режиссер Jørgen Lerdam?
WITH director_films AS (
	SELECT fw.id as film_uuid
	FROM person p
	JOIN person_film_work pfw on p.id == pfw.person_id
	JOIN film_work fw on pfw.film_work_id == fw.id 
	WHERE p.full_name like '%Jørgen Lerdam%'
)
SELECT p.full_name 
FROM person p 
JOIN person_film_work pfw on p.id == pfw.person_id
JOIN film_work fw on pfw.film_work_id == fw.id
JOIN director_films df on fw.id == df.film_uuid 
WHERE pfw."role" == 'actor';


-- Кто из сценаристов принял участие в большинстве фильмов?
SELECT p.full_name, pfw."role", COUNT(*)
FROM person p
JOIN person_film_work pfw on p.id == pfw.person_id 
WHERE pfw."role" == 'writer'
GROUP BY pfw.person_id
ORDER BY COUNT(*) DESC
LIMIT 1;

-- Кто из актёров снялся в большинстве фильмов?
SELECT p.full_name, pfw."role", COUNT(*)
FROM person p
JOIN person_film_work pfw on p.id == pfw.person_id 
WHERE pfw."role" == 'actor'
GROUP BY pfw.person_id
ORDER BY COUNT(*) DESC
LIMIT 1;