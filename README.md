# SkyrimStringToJson
convert Skyrim game string (XML file from xTranslator) to json.

将从xTranslator提取的汉化XML文件转换为JSON

由于官方繁中的质量有很大提升空间，玩家使用的游戏汉化可能是：ANK汉化、大学汉化、汤镬汉化等等，还有很多玩家社区维护的汉化。

不同的译文让玩家们难以交流，甚至连游戏攻略都不互通：地点和人物用词不同。

## 1. 使用 xTranslator 从游戏中导出 String

在xTranslator中，先加载Esp/Esm文件，再加载.strings作为翻译，可以导出带有详细的翻译文本，如：

```xml
<String List="0" sID="00EE7A">
  <EDID>Book3ValuableLustyArgonianMaidVol01</EDID>
  <REC>BOOK:FULL</REC>
  <Source>The Lusty Argonian Maid, v1</Source>
  <Dest>元气满满的亚龙人女仆，卷一</Dest>
</String>
```

这样的XML文件不容易处理，如果转换为JSON/WikiTable，就方便处理了。


## 2. 修改配置

修改config.json

如对于从多个汉化导出的XML文件夹

```json
{
    "xml_folders": {
        "Official": "C:/Skyrim_Trans/Official/xml",
        "ANK": "C:/Skyrim_Trans/ANK/xml",
        "Reconquista": "C:/Skyrim_Trans/Reconquista/xml",
        "Unofficial": "C:/Skyrim_Trans/Unofficial/xml"
    },
    "output": "C:/Skyrim_Trans/Export"
}
```

## 3. 运行程序获得 JSON

（本程序依赖库 xmltodict，可以使用命令`pip install xmltodict`安装）

运行`python main.py`，可以在输出目录获得相应json文件

形如：

```json
{
  "Dawnguard_0003E0": {
    "DLC": "Dawnguard",
    "@List": "0",
    "@sID": "0003E0",
    "EDID": "DLC1ElderScrollDragon",
    "EN": "Elder Scroll (Dragon)",
    "ANK": "上古卷轴（龙）",
    "Official": "上古卷軸（龍）",
    "Reconquista": "上古卷轴（龙）",
    "Unofficial": "上古卷轴（龙类）"
  },
  ...
}
```

这样更容易解析的格式方便进行后续处理。

