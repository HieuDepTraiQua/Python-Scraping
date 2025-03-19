import asyncio
import json
import requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import LLMConfig
from crawl4ai.utils import optimize_html
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

async def extract_data_from_url():
    response = requests.get("https://vietnamnet.vn/")
    html_content = response.text
    dummy_html = BeautifulSoup(html_content, "html.parser")
    llm_config = LLMConfig(
        provider="gemini/gemini-1.5-pro", 
        api_token= "AIzaSyCp1BrDcVHknHa5wiNCCrj5jVocxdcp6Nc"
    )
    print("\n🚀 Generating schema for product extraction...")
    print("  This would use the LLM to analyze HTML and create an extraction schema")
    schema = JsonCssExtractionStrategy.generate_schema(
        html=dummy_html,
        llm_config = llm_config,
        query="Extract author, title, content, publish_date, image, picture, link"
    )
    print("\n✅ Generated Schema:")
    with open("crawl4ai_schema_all.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(schema))
    print("\n✅ CrawlerRunConfig:")
    css_strategy = JsonCssExtractionStrategy(schema=schema)
    async with AsyncWebCrawler(verbose=True) as crawler:
        result_extract = await run_extraction(crawler, "https://vietnamnet.vn/", css_strategy, "CSS Extraction")        
        return result_extract.extracted_content

async def get_links():
    run_config = CrawlerRunConfig(
        exclude_external_links=True,         # Remove external links from final content
        exclude_social_media_links=True,     # Remove links to known social sites
        exclude_domains=["vietnamnet.vn"], # Exclude links to these domains
        exclude_social_media_domains=["facebook.com","twitter.com"], # Extend the default list
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://vietnamnet.vn/", config=run_config
        )
        with open('crawl4ai_extract_links.json', "w", encoding="utf-8") as file:
            json.dump(result.links, file, ensure_ascii=False, indent=4) 

if __name__ == "__main__":
    asyncio.run(extract_data_from_url())
