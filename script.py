from multiprocessing import Pool
import requests
import os
import re

class Parser:
    course_base = "https://course.bazanova-art.ru/course/learn/"
    session = None

    def __init__(self):
        self.session = self.create_session()

    def create_session(self):
        cookies_string = """sj_lang=ru; ai_user=5Yp8g|2021-05-05T10:12:35.823Z; tj=CD44547BBEA6D3BC76D503A1975FD36AA58AF30DAEF3E12CC42AA17B5B57F0BA936987FB530303225A4FEFF4DDD59D7220F59C7AF9A64AEBC29502D8EAE212B4DBA9225C97B17ECF031ED8A7DA9A15437287B1A2257533DD7A4057C794D20139123116D4C65C52B34085392ED3AB75E2FCF4619A80EF247C7CEF3C2821C2CA107DB88EA99875A47D17B98DEB67AF3FD2; ai_session=HWys4|1620231718800|1620233380895.26"""
        cookies = {k.split('=')[0]: k.split('=')[1] for k in cookies_string.split(';')}
        session = requests.Session()
        for k, v in cookies.items():
            session.cookies.set(k, v)
        return session

    def download_video(self, article_path):
        page = self.session.get(self.course_base + article_path)
        with open('page.html', 'w+') as f:
            f.write(page.text)
        if 'iframe' in page.text:
            title = re.search('<h1 class="name">([^<]*)<\/h1>', page.text).groups()[0].strip()
            cdn_root_m3u8_url = page.text.split("<iframe src=\"")[1].split('"')[0]
            page_root_m3u8 = self.session.get(cdn_root_m3u8_url)
            url_root_m3u8 = page_root_m3u8.text.split('url: \'')[1].split("'")[0]
            root_m3u8 = self.session.get(url_root_m3u8)
            video_id = url_root_m3u8.split('/video/')[1].split('/')[0]
            track_names = list(filter(lambda x: not x.startswith("#") and x, root_m3u8.text.splitlines()))
            cdn_base = "https://cdn-eu.accelonline.io/jjCmI4EwwUu6qgUCeEYffw/video/"
            cdn_video_base = f"{cdn_base}{video_id}/hls/"
            if 'videos' not in os.listdir():
                os.mkdir('videos')
            os.system(f"""
                ffmpeg \\
                -i "{cdn_video_base}{track_names[4]}" \\
                -i "{cdn_video_base}{track_names[0]}" \\
                -c:v copy -c:a aac "videos/{title}.mp4"
            """)

    def download_course(self, course_id):
        page = self.session.get(self.course_base + f"{course_id}")
        article_ids = list(k for k in re.findall(r"/course/gotostep/\d+\/\d+", page.text))
        with Pool(len(article_ids)) as p:
            p.map(self.download_video, article_ids)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("id", help="Id of course", type=int)
    args = parser.parse_args()
    parser = Parser()
    parser.download_course(args.id)
