
# import trafilatura
# import json
# from bs4 import BeautifulSoup
# import json
# from goose3 import Goose
# from readability import Document
# import requests
# from llama_cpp import Llama


# def function_test():
#     url = "https://vietnamnet.vn/xac-minh-vu-tai-xe-taxi-g7-bi-danh-nhap-vien-2377990.html"
#     downloaded = trafilatura.fetch_url(url)
#     result = trafilatura.extract(downloaded, output_format='json', include_comments=False, include_tables=False)
#     print(json.dumps(result, indent=2, ensure_ascii=False))
    
# def test2 ():
#     html = read_file_content("div_content.txt")
#     soup = BeautifulSoup(html, 'html.parser')

#     # Tạo dictionary để chứa kết quả
#     result = {"articles": []}

#     important_tags = ["h1", "h2", "h3", "p", "img", "a"]
#     ignored_tags = ["script", "style", "meta", "link", "iframe"]

#     for element in soup.find_all():
#         tag_name = element.name

#         # Bỏ qua các thẻ không quan trọng
#         if tag_name in ignored_tags:
#             continue

#         # Lấy nội dung quan trọng
#         text = element.get_text(strip=True) if tag_name != "img" else ""

#         # Lấy thuộc tính của thẻ (src, href, data-srcset)
#         attributes = element.attrs
#         if tag_name == "img":
#             attributes["src"] = element.get("src", "")
#             attributes["data-srcset"] = element.get("data-srcset", "")
#         elif tag_name == "a":
#             attributes["href"] = element.get("href", "")

#         # Chỉ lưu các thẻ quan trọng
#         if tag_name in important_tags or attributes:
#             result["articles"].append({"tag": tag_name, "text": text, "attributes": attributes})

#     # Xuất JSON
#     output_filename = "output.json"
#     with open(output_filename, "w", encoding="utf-8") as json_file:
#         json.dump(result, json_file, ensure_ascii=False, indent=4)

#     print(f"Dữ liệu đã được ghi vào {output_filename}")
    
    
# def extract_with_traf():
#     html = read_file_content("div_content.txt")
#     # Trích xuất dữ liệu quan trọng bằng AI
#     result = trafilatura.extract(html, output_format='json', include_comments=False, include_tables=False)
#     print(result)
#     # output_filename = "output_with_traf.json"
#     # with open(output_filename, "w", encoding="utf-8") as json_file:
#     #     json.dump(result, json_file, ensure_ascii=False, indent=4)

# def extract_with_goose():
#     html = read_file_content("div_content.txt")
#     g = Goose()
#     article = g.extract("https://vietnamnet.vn/kien-truc-gay-tranh-cai-cua-toa-nha-ham-ca-map-ben-ho-guom-2377993.html#vnn_source=thoisu&vnn_medium=listtin1")
#     json = {
#         "title": article.title,
#         "content": article.cleaned_text,
#         "image": article.top_image
#     }
#     print(json)
    
# def extract_with_readability():
#     html = read_file_content("div_content.txt")
#     response = requests.get('https://vietnamnet.vn/man-the-hien-suc-manh-moi-la-cua-canh-sat-o-pho-di-bo-ho-guom-2378951.html')
#     doc = Document(html)
#     json_data = {
#         "title": doc.title(),
#         "content_summary": doc.summary(),
#         "clean_html": doc.get_clean_html(),
#         "shortTile": doc.short_title()
#     }
    
#     output_filename = "output_with_readability.json"
#     with open(output_filename, "w", encoding="utf-8") as json_file:
#         json.dump(json_data, json_file, ensure_ascii=False, indent=4)

#     # In ra thông báo
#     print(f"Dữ liệu đã được ghi vào {output_filename}")
    
    
# def extract_with_local_ai_mistral():
#     html = read_file_content("div_content.txt")
#     soup = BeautifulSoup(html, "html.parser")
#     llm = Llama(model_path="models\mistral-7b-instruct-v0.1.Q4_K_M.gguf",
#                 n_ctx=2048, n_threads=12
#     )
#     # Lấy toàn bộ nội dung HTML (đã làm sạch)
#     cleaned_html = soup.prettify()
    
#     # Gọi mô hình
#     output = llm(f"Bạn là một AI giúp phân tích HTML và trích xuất dữ liệu quan trọng. Đây là nội dung HTML:\n{cleaned_html}\nHãy trả về Json gồm các nội dung quan trọng trong đoạn HTML trên, tôi chỉ cần kết quả json, không cần giải thích và cấu trúc của những giá trị trả về luôn cố định và được định nghĩa như sau value là giá trị của nội dung tìm được và selector là className dẫn tới thẻ đó hoặc một giá trị CSS slector nào đó dùng để định nghĩa thẻ ")
#     print(output)
    
#     # Xuất JSON
#     output_filename = "output_with_gpt.json"
#     with open(output_filename, "w", encoding="utf-8") as json_file:
#         json.dump(output, json_file, ensure_ascii=False, indent=4)
#     print("Đã lưu kết quả vào file output_with_gpt.json")

# def extract_with_parse_html():
#     html = read_file_content("div_content.txt")
#     soup = BeautifulSoup(html, "html.parser")
#     # Lấy toàn bộ nội dung HTML (đã làm sạch)
#     cleaned_html = soup.prettify()
#     html_text = cleaned_html.replace("\n", "<br>")
    
#     # Xuất .txt
#     output_filename = "test_text.txt"
#     with open(output_filename, "w", encoding="utf-8") as file:
#         json.dump(html_text, file, ensure_ascii=False, indent=4)
#     print("Đã lưu kết quả vào file test_text.txt")