#!/usr/bin/env python3
import time
import os
import json
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from parse_bookmarks import parse_bookmarks, save_bookmarks

class BookmarkHandler(FileSystemEventHandler):
    def __init__(self, bookmark_file, output_json, output_js):
        self.bookmark_file = bookmark_file
        self.output_json = output_json
        self.output_js = output_js
        self.last_modified = 0
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.bookmark_file):
            # 防止重复处理
            current_time = time.time()
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time
            
            print(f"\n检测到书签文件变化: {event.src_path}")
            try:
                # 解析书签文件
                bookmarks = parse_bookmarks(event.src_path)
                
                # 保存为JSON
                save_bookmarks(bookmarks, self.output_json)
                print(f"已更新 {self.output_json}")
                
                # 转换为JavaScript文件
                js_content = f"const bookmarksData = {json.dumps(bookmarks, ensure_ascii=False, indent=2)};"
                with open(self.output_js, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                print(f"已更新 {self.output_js}")
                
            except Exception as e:
                print(f"更新失败: {str(e)}")

def watch_bookmarks(bookmark_file, output_json, output_js):
    # 确保文件存在
    if not os.path.exists(bookmark_file):
        print(f"错误: 找不到书签文件 {bookmark_file}")
        return
    
    # 创建事件处理器
    event_handler = BookmarkHandler(bookmark_file, output_json, output_js)
    
    # 创建观察者，使用轮询方式
    observer = PollingObserver(timeout=1)  # 每秒检查一次
    observer.schedule(event_handler, os.path.dirname(bookmark_file), recursive=False)
    observer.start()
    
    print(f"\n开始监控书签文件: {bookmark_file}")
    print("等待文件变化...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n停止监控")
    
    observer.join()

if __name__ == "__main__":
    # 配置文件路径
    BOOKMARK_FILE = "../data/bookmarks_2025_3_28.html"  # 原始书签文件
    OUTPUT_JSON = "../data/bookmarks.json"  # JSON输出
    OUTPUT_JS = "../web/bookmarks.js"  # JavaScript输出
    
    watch_bookmarks(BOOKMARK_FILE, OUTPUT_JSON, OUTPUT_JS) 