import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

class ArticleScraper(scrapy.Spider):
    name = "article_and_recital_scraper"

    # Initialise with the range of articles and recitals to scrape from the EU AI Act
    def __init__(self, article_start=1, article_end=113, recital_start=1, recital_end=180, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article_start = article_start
        self.article_end = article_end
        self.recital_start = recital_start
        self.recital_end = recital_end
        self.article_base_url = "https://artificialintelligenceact.eu/article/"
        self.recital_base_url = "https://artificialintelligenceact.eu/recital/"
        self.articles = []
        self.recitals = []

    # Define and initialise the Scrapy request object
    def start_requests(self):
        # Scrape articles 1 to 113
        for article_id in range(self.article_start, self.article_end + 1):
            url = f"{self.article_base_url}{article_id}/"
            print(f"URL for Article #{article_id}: {url}")
            yield scrapy.Request(url, callback=self.parse_article)
        # Scrape recitals 1 to 180
        for recital_id in range(self.recital_start, self.recital_end + 1):
            url = f"{self.recital_base_url}{recital_id}/"
            print(f"URL for Recital #{recital_id}: {url}")
            yield scrapy.Request(url, callback=self.parse_recital)

    # Clean up content retrieved from the article url's
    def parse_article(self, response):
        article_id = response.url.split("/")[-2]
        title = response.xpath("//h1/text()").get(default=f"Article {article_id}")
        content = "\n".join(response.xpath("//p//text() | //h4//text()").getall()).strip()
        self.articles.append({"Type": "Article", "ID": article_id, "Title": title, "Content": content})

    # Clean up content retrieved from the recital url's
    def parse_recital(self, response):
        recital_id = response.url.split("/")[-2]
        title = response.xpath("//h1/text()").get(default=f"Recital {recital_id}")
        content = "\n".join(response.xpath("//p//text()").getall()).strip()
        self.recitals.append({"Type": "Recital", "ID": recital_id, "Title": title, "Content": content})

    # Convert both lists to Dataframe and concatenate
    def closed(self, reason):   # Keep 'reason' parameter for logging and debugging
        df_articles = pd.DataFrame(self.articles)
        df_recitals = pd.DataFrame(self.recitals)
        df_combined = pd.concat(objs=[df_articles, df_recitals], ignore_index=True)
        df_combined.to_csv(path_or_buf="./data/articles_and_recitals.csv", index=False)

# Define the run function and save Scrapy Crawler output to .csv file
def run_scraper():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "articles_and_recitals.csv": {"format": "csv"},
        },
    })

    process.crawl(ArticleScraper, article_start=1, article_end=113, recital_start=1, recital_end=180)
    process.start()

    print("Scraping of EU AI Act completed! Saved to articles_and_recitals.csv \n")

# Load scraped data into a DataFrame
def load_articles_and_recitals_to_dataframe():
    try:
        dataframe = pd.read_csv("./data/articles_and_recitals.csv")

        print("Successfully loaded articles_and_recitals.csv file! \n")

        return dataframe

    except FileNotFoundError:
        print("The articles_and_recitals.csv was not found. Running the scraper now \n"
              ".................................................................... \n")

        # Run web scraper which saves output to .csv
        run_scraper()

        # Load .csv to DataFrame
        dataframe = pd.read_csv("./data/articles_and_recitals.csv")

        print("The .csv was saved to location /data/articles_and_recitals.csv")

        return dataframe