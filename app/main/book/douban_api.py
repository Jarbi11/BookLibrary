from app import db
from app.models import Book
from flask import flash, current_app
import aiohttp
import asyncio

ssl_conn = aiohttp.TCPConnector(verify_ssl=False)
loop = asyncio.get_event_loop()


async def get_book_information(title: str, isbns: str, douban_ids: str):
    new_books = []
    if not isbns and not title and not douban_ids:
        return new_books
    if title:
        new_book = await get_douban_info_page(context=title)
        if not new_book:
            flash(u"书籍 %s 添加失败" % title, "danger")
            return
        db.session.add(new_book)
        db.session.commit()
        flash(u'书籍 %s 已添加至图书馆!' % new_book.title, 'success')
        new_books.append(new_book)
    if douban_ids:
        for douban_id in douban_ids.replace(" ", "").split(","):
            new_book = await get_information_by_isbn_or_douban_id(context=f"subject/{douban_id}")
            if not new_book:
                flash(u"书籍 %s 添加失败" % douban_id, "danger")
            else:
                db.session.add(new_book)
                db.session.commit()
                flash(u'书籍 %s 已添加至图书馆!' % new_book.title, 'success')
                new_books.append(new_book)
        return new_books
    if isbns:
        for isbn in isbns.replace(" ", "").split(","):
            new_book = await get_information_by_isbn_or_douban_id(context=f"isbn/{isbn}")
            if not new_book:
                flash(u"书籍 %s 添加失败" % isbn, "danger")
            else:
                db.session.add(new_book)
                db.session.commit()
                flash(u'书籍 %s 已添加至图书馆!' % new_book.title, 'success')
                new_books.append(new_book)
        return new_books


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


async def get_information_by_isbn_or_douban_id(context: str):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as er:
        print(er.args[0], "create a new EventLoop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    new_book = Book()
    book_url = f"{current_app.config['DOUBAN_TRANS_SERVER']}/{context}"
    async with aiohttp.request(method="GET", url=book_url, connector=aiohttp.TCPConnector(verify_ssl=False),
                               loop=loop) as response:
        if response.status != 200:
            flash(u"response %d" % response.status, "danger")
            return None
        json_data = await response.json()
        if not json_data["success"]:
            flash(u"fetch data not success", "danger")
            return None
        data = json_data["data"]
        new_book.title = data["title"]
        if data["subtitle"]:
            new_book.title += u"--"
            new_book.title += data["subtitle"]
        new_book.isbn = data["isbn"]
        new_book.author = convert_list_to_string(data["author"], ",")
        new_book.translator = convert_list_to_string(data["translator"], ",")
        new_book.publisher = convert_list_to_string(data["publish"], ",")
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
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as er:
        print(er.args[0], "create a new EventLoop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    search_url = f"{current_app.config['DOUBAN_TRANS_SERVER']}/search?text={context}"
    async with aiohttp.request(method="GET", url=search_url, connector=aiohttp.TCPConnector(verify_ssl=False),
                               loop=loop) as response:
        if response.status != 200:
            flash(u"response %d" % response.status, "danger")
            return None
        json_data = await response.json()
        if not json_data["success"]:
            flash(u"fetch data not success", "danger")
            return None
        if len(json_data["data"]) <= 0:
            flash(u"fetch data not success", "danger")
            return None
        for data in json_data["data"]:
            if not data.get("extra_actions", None):
                continue
            douban_id = data.get("id", "")
            if not douban_id:
                flash(u"didn't get the information page")
                return None
            return await get_information_by_isbn_or_douban_id(context=f"subject/{douban_id}")
