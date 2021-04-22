with character_count as (
select character,count(*) from user_results
	group by character
),
distinct_characters as (
select distinct character from tesseract_results
),
characters_to_ask_about as (
	select distinct_characters.character,character_count.count from distinct_characters
	left join character_count on distinct_characters.character = character_count.character
	where (character_count.count is null) or (character_count.count < 10)
),
unprocessed_tiles as (select tesseract_results.*
	from tesseract_results
		left join user_results
			on tesseract_results.file_prefix = user_results.file_prefix
			and tesseract_results.model = user_results.tesseract_model
			and tesseract_results.local_tile_index = user_results.local_tile_index
	where user_results.x_min is null),
tiles_to_ask_about as (select unprocessed_tiles.* from unprocessed_tiles
					  inner join characters_to_ask_about on
					  unprocessed_tiles.character = characters_to_ask_about.character)

select tiles_to_ask_about.file_prefix,
		simple_results.tesseract_model,
		tiles_to_ask_about.local_tile_index,
		x_min,
		x_max,
		y_min,
		y_max,
		simple_results.glyph_confidence,
		simple_results.tesseract_confidence,
		tiles_to_ask_about.character
		from tiles_to_ask_about
	inner join simple_results
	on tiles_to_ask_about.file_prefix = simple_results.file_prefix
		and tiles_to_ask_about.local_tile_index = simple_results.local_tile_index
		and tiles_to_ask_about.model = simple_results.tesseract_model
	where tiles_to_ask_about.model = 0
		and tiles_to_ask_about.darkest_pixel < 170
		and tiles_to_ask_about.area >= 2000
		and tiles_to_ask_about.area <= 10000
	order by simple_results.tesseract_confidence,simple_results.glyph_confidence
	limit 1
