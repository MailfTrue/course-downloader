from multiprocessing import Pool
import requests
import os
import re

class Parser:
    course_base = "https://course.bazanova-art.ru/course/learn/"
    session = None

    def __init__(self, email, password):
        self.session = self.create_session(email, password)

    def create_session(self, email, password):
        session = requests.Session()
        for k, v in cookies.items():
            session.cookies.set(k, v)
        session.post(self.course_base + '/login', data={'email': email, 'password': password})
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
    parser.add_argument("email", help="Id of course", type=str)
    parser.add_argument("password", help="Id of course", type=str)
    args = parser.parse_args()
    parser = Parser(args.email, args.password)
    parser.download_course(args.id)
