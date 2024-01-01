# wiki_speedrunner
A wikipedia speedrunner.
* Requires internet connection
* Uses requests to get html of wikipedia page
* Scrapes html for wiki link using regex
* Breadth-first search
* Async multiprocessing for speed and non-blockign requests

## Usage
* Create venv and install requirements.txt
* run python3 main.py
  * Default start wiki = Toilet Paper Orientation, end wiki = Adolf Hitler
  * Use flags -s and -e followed by link to wikipedia page to set start and end wikis respectively

## Examples
* Toilet paper orientation -> Adolf Hitler

## Possible speed improvements
* Multiple sessions
* Use line profiler to find speed bottlenecks
* Branches to explore more deeply could be weighted by similarity to end wiki
  * LLM to compute similarity score? (downside: inference time = slower)
* Downloading wikipedia to avoid using slow http requests (downside: increases memory requirements)

Let me know if you end up implementing any of these improvements!
 
