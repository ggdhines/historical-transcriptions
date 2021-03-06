WITH USER_CHARACTER_COUNT AS
	(SELECT CHARACTER,
			COUNT(*) AS USER_COUNT
		FROM USER_RESULTS
		GROUP BY CHARACTER),
	CHARACTERS_NOT_YET_FOUND AS
	(SELECT TESSERACT_RESULTS.*
		FROM TESSERACT_RESULTS
		LEFT JOIN USER_CHARACTER_COUNT ON TESSERACT_RESULTS.CHARACTER = USER_CHARACTER_COUNT.CHARACTER
		WHERE (USER_CHARACTER_COUNT.USER_COUNT IS NULL)
			OR (USER_CHARACTER_COUNT.USER_COUNT < 2)),
	UNPROCESSED_TILES AS
	(SELECT CHARACTERS_NOT_YET_FOUND.*
		FROM CHARACTERS_NOT_YET_FOUND
		LEFT JOIN USER_RESULTS ON CHARACTERS_NOT_YET_FOUND.FILE_PREFIX = USER_RESULTS.FILE_PREFIX
		AND CHARACTERS_NOT_YET_FOUND.MODEL = USER_RESULTS.TESSERACT_MODEL
		AND CHARACTERS_NOT_YET_FOUND.LOCAL_TILE_INDEX = USER_RESULTS.LOCAL_TILE_INDEX
		WHERE USER_RESULTS.X_MIN IS NULL)
SELECT UNPROCESSED_TILES.FILE_PREFIX,
	SIMPLE_RESULTS.TESSERACT_MODEL,
	UNPROCESSED_TILES.LOCAL_TILE_INDEX,
	X_MIN,
	X_MAX,
	Y_MIN,
	Y_MAX,
	SIMPLE_RESULTS.GLYPH_CONFIDENCE,
	SIMPLE_RESULTS.TESSERACT_CONFIDENCE,
	UNPROCESSED_TILES.CHARACTER
FROM UNPROCESSED_TILES
INNER JOIN SIMPLE_RESULTS ON UNPROCESSED_TILES.FILE_PREFIX = SIMPLE_RESULTS.FILE_PREFIX
AND UNPROCESSED_TILES.LOCAL_TILE_INDEX = SIMPLE_RESULTS.LOCAL_TILE_INDEX
AND UNPROCESSED_TILES.MODEL = SIMPLE_RESULTS.TESSERACT_MODEL
WHERE UNPROCESSED_TILES.MODEL = 0
	AND UNPROCESSED_TILES.DARKEST_PIXEL < 170
	AND UNPROCESSED_TILES.AREA >= 2000
	AND UNPROCESSED_TILES.AREA <= 10000
ORDER BY SIMPLE_RESULTS.TESSERACT_CONFIDENCE,
	SIMPLE_RESULTS.GLYPH_CONFIDENCE
LIMIT 1

