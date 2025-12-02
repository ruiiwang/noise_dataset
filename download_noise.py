import requests
import time
import random
import os
import re
import xml.etree.ElementTree as ET
import glob

# ### 噪声下载：
# - 网站：https://cafe.ambient-mixer.com/scottish-coffee-house
# - 点击播放，左侧点击“show mixer”，选择种类，打开文件夹直到出现音频文件。
# - 右键空白界面选择检查，网络-Fetch/XHR-预览，在左侧打开文件夹，网页：https://xml.ambient-mixer.com/get-audio?id_category=xx，xx是根据种类的编号。每个音频的格式如下：
# ```xml
# <audio_file>
# <id_audio>3924</id_audio>
# <name_audio>Auto Paper Towel Dispenser</name_audio>
# <url_audio>https://xml.ambient-mixer.com/audio/f/4/b/f4bb3ec186eaadd344b73d4d21c00f95.mp3</url_audio>
# </audio_file>
# ```
# - 复制全部到 noise_xml/{种类}.txt，运行download_noise.py，下载好的文件会保存到 noise_dataset。

# 清理文件名，移除不允许在文件名中使用的字符
def clean_filename(filename):
    # 替换不允许的字符为下划线
    return re.sub(r'[\\/*?:"<>|]', '_', filename)


# 解析XML内容
def parse_xml_content(xml_content):
    try:
        # 尝试直接解析
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"XML解析错误: {e}")
        print("尝试使用替代方法解析...")

        # 使用正则表达式直接提取所需信息
        import re
        audio_files = []

        # 匹配<audio_file>块
        pattern = r'<audio_file>.*?<id_audio>(.*?)</id_audio>.*?<name_audio>(.*?)</name_audio>.*?<url_audio>(.*?)</url_audio>.*?</audio_file>'
        matches = re.findall(pattern, xml_content, re.DOTALL)

        for match in matches:
            audio_info = {
                'id': match[0],
                'name': match[1],
                'url': match[2]
            }
            audio_files.append(audio_info)

        print(f"使用正则表达式提取到 {len(audio_files)} 个音频信息")
        return audio_files

    # 如果解析成功，使用标准方法提取
    audio_files = []
    for audio_file in root.findall('.//audio_file'):
        audio_info = {
            'id': audio_file.find('id_audio').text,
            'name': audio_file.find('name_audio').text,
            'url': audio_file.find('url_audio').text
        }
        audio_files.append(audio_info)

    return audio_files


# 下载音频文件
def download_audio(audio_info, download_dir):
    url = audio_info['url']
    # 清理文件名
    filename = clean_filename(audio_info['name'])
    file_path = os.path.join(download_dir, f"{filename}.mp3")

    # 检查文件是否已存在
    if os.path.exists(file_path):
        print(f"文件已存在，跳过: {filename}")
        return True

    try:
        print(f"正在下载: {filename}")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"下载完成: {filename}")
            return True
        else:
            print(f"下载失败: {filename}, 状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"下载出错: {filename}, 错误: {str(e)}")
        return False


# 处理单个txt文件
def process_txt_file(txt_file_path):
    # 获取txt文件名（不含扩展名）作为文件夹名
    txt_filename = os.path.splitext(os.path.basename(txt_file_path))[0]
    download_dir = os.path.join("noise_dataset", txt_filename)

    # 创建下载目录
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"创建目录: {download_dir}")

    print(f"\n开始处理文件: {txt_file_path}")

    # 读取txt文件内容
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试使用其他编码
        try:
            with open(txt_file_path, 'r', encoding='latin-1') as f:
                xml_content = f.read()
        except Exception as e:
            print(f"无法读取文件 {txt_file_path}: {str(e)}")
            return

    # 提取实际的XML部分
    xml_start = xml_content.find('<audio_files>')
    if xml_start != -1:
        # 只保留<audio_files>及之后的内容
        xml_content = xml_content[xml_start:]
        # 检查结尾标签是否存在
        if '</audio_files>' in xml_content:
            # 只保留完整的<audio_files>...</audio_files>部分
            xml_end = xml_content.find('</audio_files>') + len('</audio_files>')
            xml_content = xml_content[:xml_end]
        else:
            # 如果没有结束标签，添加一个
            xml_content = f"{xml_content}</audio_files>"
    else:
        print(f"在文件 {txt_file_path} 中找不到 <audio_files> 标签")
        return

    # 解析XML获取音频信息
    audio_files = parse_xml_content(xml_content)

    if not audio_files:
        print(f"在文件 {txt_file_path} 中未找到音频文件信息")
        return

    print(f"找到 {len(audio_files)} 个音频文件")

    # 下载每个音频文件，并在下载之间添加随机延迟
    for i, audio_info in enumerate(audio_files):
        success = download_audio(audio_info, download_dir)

        # 如果不是最后一个文件，添加随机延迟
        if i < len(audio_files) - 1 and success:
            # 随机延迟1-5秒内的任意时间（非整秒）
            delay = random.uniform(1.0, 5.0)
            print(f"等待 {delay:.2f} 秒...")
            time.sleep(delay)

    print(f"文件 {txt_file_path} 处理完成!")


def main():
    # 创建主下载目录
    if not os.path.exists("noise_dataset"):
        os.makedirs("noise_dataset")

    # 获取当前目录下所有txt文件
    txt_files = glob.glob("noise_xml/*.txt")

    if not txt_files:
        print("当前目录下未找到txt文件")
        return

    print(f"找到 {len(txt_files)} 个txt文件需要处理")

    # 处理每个txt文件
    for txt_file in txt_files:
        process_txt_file(txt_file)

    print("\n所有下载已完成!")


if __name__ == "__main__":
    main()
