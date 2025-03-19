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
        api_token= "token_gemeini"
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



async def main():
    init_html = """
    <html>
    <body>
<div class="group-horizontal-item">
            <!-- related item -->
                    <div class="vnn-mb-[20px] vnn-grid vnn-grid-cols-2 vnn-gap-[15px] vnn-font-arial lg:vnn-font-notosans-regular">
                        <a class="vnn-relative vnn-mb-[8px] vnn-block vnn-h-0 vnn-pb-[66%]" href="/sau-khi-sua-doi-hien-phap-se-xem-xet-bo-cap-huyen-sap-nhap-tinh-2381465.html">
                            <img class="vnn-absolute vnn-top-0 vnn-left-0 vnn-right-0 vnn-bottom-0 vnn-h-full vnn-w-full" src="https://static-images.vnncdn.net/vps_images_publish/000001/000003/2025/3/17/sau-khi-sua-doi-hien-phap-se-xem-xet-bo-cap-huyen-sap-nhap-tinh-62747.jpg?width=0&amp;s=w2HkmIaqRhqEEnixX9kRWg" alt="Sau khi sửa đổi Hiến pháp sẽ xem xét bỏ cấp huyện, sáp nhập tỉnh">
                        </a>
                        <div class="group-content">
                            <h4 class="vnn-mb-[7px] vnn-font-bold vnn-text-[#3e3e3e] lg:vnn-font-notosans-bold lg:vnn-font-normal">
                                <a href="/sau-khi-sua-doi-hien-phap-se-xem-xet-bo-cap-huyen-sap-nhap-tinh-2381465.html" title="Sau khi sửa đổi Hiến pháp sẽ xem xét bỏ cấp huyện, sáp nhập tỉnh">
                                    Sau khi sửa đổi Hiến pháp sẽ xem xét bỏ cấp huyện, sáp nhập tỉnh
                                </a>
                            </h4>
                            <span class="vnn-mb-[8px] vnn-hidden vnn-text-[12px] vnn-text-[#868686] lg:vnn-block">17/03/2025</span>
                            <span class="vnn-hidden vnn-text-[15px] vnn-text-[#5d5d5d] lg:vnn-line-clamp-3">
                                Chủ tịch Quốc hội Trần Thanh Mẫn cho biết, cuộc cách mạng tinh gọn bộ máy đang bước vào giai đoạn thứ hai, chuẩn bị tiến hành sắp xếp bộ máy cấp xã; sau khi sửa đổi Hiến pháp sẽ xem xét việc bỏ cấp huyện, sắp xếp sáp nhập đơn vị hành chính cấp tỉnh.
                            </span>
                        </div>
                    </div>
                    <div class="vnn-mb-[20px] vnn-grid vnn-grid-cols-2 vnn-gap-[15px] vnn-font-arial lg:vnn-font-notosans-regular">
                        <a class="vnn-relative vnn-mb-[8px] vnn-block vnn-h-0 vnn-pb-[66%]" href="/quoc-hoi-hop-som-quyet-nhieu-van-de-lien-quan-sap-nhap-tinh-bo-cap-huyen-2380803.html">
                            <img class="vnn-absolute vnn-top-0 vnn-left-0 vnn-right-0 vnn-bottom-0 vnn-h-full vnn-w-full" src="https://static-images.vnncdn.net/vps_images_publish/000001/000003/2025/3/14/quoc-hoi-hop-som-quyet-nhieu-van-de-lien-quan-sap-nhap-tinh-bo-cap-huyen-102551.jpg?width=0&amp;s=8klg4hcE5wcJtDlUnBFzhw" alt="Quốc hội họp sớm, quyết nhiều vấn đề liên quan sáp nhập tỉnh, bỏ cấp huyện">
                        </a>
                        <div class="group-content">
                            <h4 class="vnn-mb-[7px] vnn-font-bold vnn-text-[#3e3e3e] lg:vnn-font-notosans-bold lg:vnn-font-normal">
                                <a href="/quoc-hoi-hop-som-quyet-nhieu-van-de-lien-quan-sap-nhap-tinh-bo-cap-huyen-2380803.html" title="Quốc hội họp sớm, quyết nhiều vấn đề liên quan sáp nhập tỉnh, bỏ cấp huyện">
                                    Quốc hội họp sớm, quyết nhiều vấn đề liên quan sáp nhập tỉnh, bỏ cấp huyện
                                </a>
                            </h4>
                            <span class="vnn-mb-[8px] vnn-hidden vnn-text-[12px] vnn-text-[#868686] lg:vnn-block">14/03/2025</span>
                            <span class="vnn-hidden vnn-text-[15px] vnn-text-[#5d5d5d] lg:vnn-line-clamp-3">
                                Kỳ họp lần thứ 9 tới của Quốc hội sẽ khai mạc sớm, từ đầu tháng 5, trong đó quyết nhiều vấn đề liên quan sáp nhập tỉnh, bỏ cấp huyện.
                            </span>
                        </div>
                    </div>
            <!-- end related -->
            
        </div>
    </body>
  </html>
    """

    result_main = await extract_data_from_html(init_html, 'main')
    with open('crawl4ai_extract_main.json', "w", encoding="utf-8") as file:
        file.write(result_main)
    base_url = "https://vietnamnet.vn"
    link_list = [base_url + item["link"] for item in json.loads(result_main)]
    print(link_list)

    merge_child = []
    for child_link in link_list:
        child_html = await get_html(child_link, 'content-detail')
        result_child = await extract_data_from_html(child_html, 'child')
        print(type(result_child))
        result_child_dic = json.loads(result_child)
        merge_child = merge_child + result_child_dic
        print(child_link,'========================\n',result_child,'========================\n')
    # print(merge_child)
    print(type(merge_child))
    with open('crawl4ai_extract.md', "w", encoding="utf-8") as file:
        json.dump(merge_child, file, ensure_ascii=False, indent=4)
asyncio.run(main())

