-- hardcoding several values in this query for now
select tesseract_results.file_prefix,cvae_results.tesseract_model , cvae_results.cvae_model,tesseract_results.local_tile_index,x_min,x_max,y_min,y_max from tesseract_results
	inner join cvae_results
		on tesseract_results.file_prefix = cvae_results.file_prefix
		and tesseract_results.local_tile_index = cvae_results.local_tile_index
		and tesseract_results.model = cvae_results.tesseract_model
	where cvae_results.cvae_model = 0
		and cvae_results.tesseract_model = 0
		and cvae_results.split = 'test'
		and tesseract_results.darkest_pixel < 170
		and tesseract_results.area >= 2000
		and tesseract_results.area <= 10000
	order by cvae_results.confidence
	limit 1