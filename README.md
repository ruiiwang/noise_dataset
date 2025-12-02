### 噪声下载：

- 网站：https://cafe.ambient-mixer.com/scottish-coffee-house

- 点击播放，左侧点击“show mixer”，选择种类，打开文件夹直到出现音频文件。

- 右键空白界面选择检查，网络-Fetch/XHR-预览，在左侧打开文件夹，网页：https://xml.ambient-mixer.com/get-audio?id_category=xx
- xx是根据种类的编号。每个音频的格式如下：

```xml
<audio_file>
<id_audio>3924</id_audio>
<name_audio>Auto Paper Towel Dispenser</name_audio>
<url_audio>https://xml.ambient-mixer.com/audio/f/4/b/f4bb3ec186eaadd344b73d4d21c00f95.mp3</url_audio>
</audio_file>
```

- 复制全部到 noise_xml/{种类}.txt，运行download_noise.py，下载好的文件会保存到 noise_dataset。