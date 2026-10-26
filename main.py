from src.tools.tools import web_search, scrape_url


# results = _scrape_url_func("https://www.bbc.com/technology/artificial-intelligence")
# print(results)


r = web_search.run("what is the latest research on using AI for climate chnage mitigation")
print(r)