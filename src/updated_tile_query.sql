with unprocessed_tiles as (select tesseract_results.*
	from tesseract_results
		left join user_results
			on tesseract_results.file_prefix = user_results.file_prefix
			and tesseract_results.model = user_results.tesseract_model
			and tesseract_results.local_tile_index = user_results.local_tile_index
	where user_results.x_min is null)

select unprocessed_tiles.file_prefix,
		cvae_results.tesseract_model,
		unprocessed_tiles.local_tile_index,
		x_min,
		x_max,
		y_min,
		y_max,
		cvae_results.cvae_model,cvae_results.confidence from unprocessed_tiles
	inner join cvae_results
	on unprocessed_tiles.file_prefix = cvae_results.file_prefix
		and unprocessed_tiles.local_tile_index = cvae_results.local_tile_index
		and unprocessed_tiles.model = cvae_results.tesseract_model
	where cvae_results.cvae_model = 0
		and cvae_results.tesseract_model = 0
-- 		and cvae_results.split = 'test'
		and unprocessed_tiles.darkest_pixel < 170
		and unprocessed_tiles.area >= 2000
		and unprocessed_tiles.area <= 10000
	order by cvae_results.confidence
	limit 1