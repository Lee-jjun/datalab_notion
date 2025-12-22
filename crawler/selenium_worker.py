# import sys
# import json

# from crawler.naver_cafe_pc_selenium import get_comment_and_view_pc

# def main():
#     url = sys.argv[1]

#     title, comment, view, is_deleted = get_comment_and_view_pc(url)

#     print(json.dumps({
#         "title": title,a
#         "comment": comment,
#         "view": view,
#         "is_deleted": is_deleted,
#     }, ensure_ascii=False), flush=True)

# if __name__ == "__main__":
#     main()