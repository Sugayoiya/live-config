#!/usr/bin/env python3
"""将 M3U/M3U8 直播源转换为 TVBox JSON 配置格式"""

import json
import re
import sys
import urllib.request


def convert_m3u(content):
    lines = content.splitlines()
    groups = {}
    current_name = ""
    current_group = "默认"

    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            gm = re.search(r'group-title="([^"]*)"', line)
            if gm:
                current_group = gm.group(1)
            else:
                current_group = "默认"
            comma_idx = line.rfind(',')
            if comma_idx != -1:
                current_name = line[comma_idx+1:].strip()
        elif line.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')) and current_name:
            if current_group not in groups:
                groups[current_group] = {}
            if current_name not in groups[current_group]:
                groups[current_group][current_name] = []
            groups[current_group][current_name].append(line)

    channels = []
    for group_name, chans in groups.items():
        for chan_name, urls in chans.items():
            channels.append({
                "name": chan_name,
                "urls": urls,
                "group": group_name
            })

    config = {
        "lives": [
            {
                "name": "直播",
                "channels": channels
            }
        ]
    }
    return config, len(groups), len(channels)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 convert_m3u.py <M3U文件或URL> [输出文件名]")
        print("示例:")
        print("  python3 convert_m3u.py source.m3u live.json")
        print("  python3 convert_m3u.py https://example.com/iptv.m3u output.json")
        sys.exit(1)

    source = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.json"

    if source.startswith(('http://', 'https://')):
        print(f"正在下载: {source}")
        req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode('utf-8')
    else:
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()

    config, group_count, channel_count = convert_m3u(content)
    output = json.dumps(config, ensure_ascii=False, indent=2)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"转换完成: {group_count} 个分组, {channel_count} 个频道")
    print(f"输出文件: {output_file}")


if __name__ == "__main__":
    main()
