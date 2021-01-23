from telegraph import Telegraph, upload


def create_telegraph_post(list_of_img, title, text):
    telegraph = Telegraph()
    telegraph.create_account(short_name='FB_test')

    links_to_img = upload.upload_file(list_of_img)
    img_links = ''
    for link in links_to_img:
        temp = f"""<img src={link}>"""
        img_links += temp

    html_content = f"""
    {img_links}
    {text}
    """
    response = telegraph.create_page(title=title, html_content=html_content)
    

    return 'https://telegra.ph/{}'.format(response['path'])

