from app.models import Book
from flask import flash, current_app
import aiohttp

ssl_conn = aiohttp.TCPConnector(ssl=False)

async def get_book_information(title: str, isbn: str, douban_id:str):
    if not isbn and not title and not douban_id:
        return None
    if isbn or douban_id:
        return await get_information_by_isbn_or_douban_id(douban_id=douban_id, isbn=isbn)
    if title:
        return await get_douban_info_page(context=title)


def convert_list_to_string(data_list: list, end: str):
    """
    :param data_list:
    :param end:
    :return:
    """
    ret_str = ""
    if len(data_list) > 0:
        for item in data_list:
            ret_str += item
            ret_str += end
        ret_str = ret_str.rstrip(end)
    return ret_str


async def get_information_by_isbn_or_douban_id(douban_id:str, isbn: str ):
    new_book = Book()
    context = f"subject/{douban_id}" if douban_id else f"isbn/{isbn}"
    book_url = f"{current_app.config['DOUBAN_TRANS_SERVER']}/{context}"
    async with aiohttp.request(method="GET", url=book_url, connector=ssl_conn) as response:
        if response.status != 200:
            flash(u"response %d" % response.status)
            return None
        json_data = await response.json()
        if not json_data["success"]:
            flash(u"fetch data not success")
            return None
        data = json_data["data"]
        new_book.title = data["title"]
        if data["subtitle"]:
            new_book.title += u"--"
            new_book.title += data["subtitle"]
        new_book.isbn = data["isbn"]
        new_book.author = convert_list_to_string(data["author"], ",")
        new_book.translator = convert_list_to_string(data["translator"], ",")
        new_book.publisher = data["publish"]
        new_book.pubdate = data["publishDate"]
        new_book.pages = data["pages"]
        new_book.price = data["price"]
        new_book.binding = data["binding"]
        new_book.summary = data["book_intro"]
        new_book.catalog = convert_list_to_string(data["catalog"], "\n")
        new_book.tags_string = convert_list_to_string(data["labels"], ",")
        new_book.image = data["cover_url"]
        new_book.douban_url = data["url"]
        if len(data["rating"]) > 0:
            new_book.douban_rating = data["rating"]["value"]
        return new_book


async def get_douban_info_page(context: str):
    search_url = f"{current_app.config['DOUBAN_TRANS_SERVER']}/search?text={context}"
    async with aiohttp.request(method="GET", url=search_url, connector=ssl_conn) as response:
        if response.status != 200:
            flash(u"response %d" % response.status)
            return None
        json_data = await response.json()
        if not json_data["success"]:
            flash(u"fetch data not success")
            return None
        if len(json_data["data"]) <= 0:
            flash(u"fetch data not success")
            return None
        for data in json_data["data"]:
            if not data.get("extra_actions", None):
                continue
            douban_id = data.get("id", "")
            if not douban_id:
                flash(u"didn't get the information page")
                return None
            return await get_information_by_isbn_or_douban_id(douban_id)
