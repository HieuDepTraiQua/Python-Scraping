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

async def get_html(url, class_name): 
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    elements = soup.find_all(class_=class_name)
    return str(elements[0])

async def run_extraction(crawler: AsyncWebCrawler, url: str, strategy, name: str):
    """Helper function to run extraction with proper configuration"""
    try:
        # Configure the crawler run settings
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=strategy,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()  # For fit_markdown support
            ),
        )

        # Run the crawler
        result = await crawler.arun(url=url, config=config)

        if result.success:
            # print(f"\n=== {name} Results ===")
            # print(f"Extracted Content: {result.extracted_content}")
            # print(f"Raw Markdown Length: {len(result.markdown.raw_markdown)}")
            # print(
            #     f"Citations Markdown Length: {len(result.markdown.markdown_with_citations)}"
            # )
            return result
        else:
            print(f"Error in {name}: Crawl failed")

    except Exception as e:
        print(f"Error in {name}: {str(e)}")


async def extract_data_from_html(init_html, key):
    # 1. Minimal dummy HTML with some repeating rows

    dummy_html = optimize_html(init_html, threshold=100)
    # 2. Define the JSON schema (XPath version)
   
    raw_url = f"raw://{init_html}"

    print("\n📊 Setting up LLMConfig...")
    # Create LLM configuration
    llm_config = LLMConfig(
        provider="gemini/gemini-1.5-pro", 
        api_token= "AIzaSyBP_Duk1iOD5EG7Otpa39B1mC_adN0wBHQ"
    )
    print("\n🚀 Generating schema for product extraction...")
    print("  This would use the LLM to analyze HTML and create an extraction schema")
    schema = JsonCssExtractionStrategy.generate_schema(
        html=dummy_html,
        llm_config = llm_config,
        query="Extract author, title, content, publish_date, image, picture, link"
    )
    print("\n✅ Generated Schema:")
    with open("crawl4ai_schema.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(schema))
    print("\n✅ CrawlerRunConfig:")
    css_strategy = JsonCssExtractionStrategy(schema=schema)
    async with AsyncWebCrawler(verbose=True) as crawler:
        result_extract = await run_extraction(crawler, raw_url, css_strategy, "CSS Extraction")        
        return result_extract.extracted_content
        # for img in images:
        #     print("Image URL:", img["src"], "Alt:", img.get("alt"))



def read_json_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

async def crawl4ai_data_by_html(url, content):
    init_html = f"<html><body>{content}</body></html>"

    result_main = await extract_data_from_html(init_html, 'main')
    with open('crawl4ai_extract_main.json', "w", encoding="utf-8") as file:
        file.write(result_main)

    data_json = json.loads(result_main)

    # data_json = read_json_file_content("crawl4ai_extract_main.json")
    data_fields = [key for key in data_json[0]]
    result_json = {
            "column": list(data_fields),
            "data": data_json
        }
    print("odiodidoi", result_json)
    
    return result_json
    # base_url = "https://vietnamnet.vn"
    # link_list = [base_url + item["link"] for item in json.loads(result_main)]
    # print(link_list)

    # merge_child = []
    # for child_link in link_list:
    #     child_html = await get_html(child_link, 'content-detail')
    #     result_child = await extract_data_from_html(child_html, 'child')
    #     print(type(result_child))
    #     result_child_dic = json.loads(result_child)
    #     merge_child = merge_child + result_child_dic
    #     print(child_link,'========================\n',result_child,'========================\n')
    # # print(merge_child)
    # print(type(merge_child))
    # with open('crawl4ai_extract.md', "w", encoding="utf-8") as file:
    #     json.dump(merge_child, file, ensure_ascii=False, indent=4)

# asyncio.run(crawl4ai_data_by_html())