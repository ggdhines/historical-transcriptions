# historical-transcriptions

Processing printed historical documents using Optical Character Recognition (OCR) software sounds really appealing. However, there are plenty of issues. For example
*   Poor document quality
*   The OCR software being unfamiliar with the font

This is a project designed to address both of these issues. I started thinking about this problem with regards to transcribing ships' weather logs, so
the code is currently very focused towards to that. This is a starting point, and I hope that ideas in this repo can be used in many different settings.

A big goal for me is to automate this process as much as possible. For example, while there is already a way to teach Tesseract (the main opensource OCR software)
new fonts, this process is time-consuming and honestly painful. I think the automation can always be improved upon, and the current approach is definitely not perfect.
That said, if you are willing to spend some time thinking about technical things, I believe the effort is already worth it.