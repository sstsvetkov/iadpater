# def bio(user, password, computer_name):
#     response = requests.get(
#         f"http://10.0.17.148/ReportServer/Pages/ReportViewer.aspx?%2fBiolink%2fBioTime+Manager+pwd&rs:Command=Value&Login={computer_name}",
#         auth=HttpNtlmAuth(username=user, password=password),
#     )
#     result = re.findall(
#         '<div style="width:28.09mm;min0-width: 28.09mm;">(\d+)</div>', response.text
#     )
#     if result:
#         return result[0]
#     else:
#         return None
#
#
# async def handle_bio(request):
#     text = await request.text()
#     try:
#         body = json.loads(text or "{}")
#     except json.JSONDecodeError:
#         return web.Response(status=400)
#     user = body.get("user", None)
#     password = body.get("password", None)
#     shop_num = body.get("shopNum", None)
#     if user and password and shop_num is not None:
#         text = bio(user=user, password=password, computer_name=shop_num) or "0"
#     else:
#         text = "0"
#     return web.Response(text=text)