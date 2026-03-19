import pyautogui
import math
import sys
import os
from time import sleep, strftime
from datetime import datetime

# --- ツール情報設定 ---
TOOL_NAME = "TeamsStay: Mouse & Shift"
TOOL_VERSION = "1.1.0"

# Windowsコンソールの色を有効化
if os.name == 'nt':
    os.system('')

GREEN  = '\033[32m'
YELLOW = '\033[33m'
RED    = '\033[31m'
CYAN   = '\033[36m'
BRIGHT = '\033[1m'
RESET  = '\033[0m'

pyautogui.FAILSAFE = True

def play_beep(sound_enabled, type='normal'):
    """MacとWindows両方で音が鳴るように対応"""
    if not sound_enabled: return
    
    if sys.platform == "win32":
        import winsound
        if type == 'start':
            winsound.Beep(500, 100); winsound.Beep(700, 100); winsound.Beep(900, 200)
        elif type == 'end':
            winsound.Beep(400, 600)
    elif sys.platform == "darwin":
        if type == 'start':
            os.system('afplay /System/Library/Sounds/Ping.aiff')
        elif type == 'end':
            os.system('afplay /System/Library/Sounds/Glass.aiff')

def execute_active_relay():
    """
    マウスを渦巻き状に動かし、さらにShiftキーを押す。
    """
    r = 60 # 回転半径
    (mx, my) = pyautogui.size()
    
    # 1. 準備：画面中央へ移動
    pyautogui.moveTo(round(mx/2), round(my/2 - r - r), duration=0.5)
    
    # 2. マウス移動：円を描きながら少しずつ位置をずらす「相対移動」
    
    move_steps = 40
    rotations = 3
    for t in range(move_steps):
        step = 1 / (move_steps / rotations)
        x = r * math.cos(step * t * 2 * math.pi)
        y = r * math.sin(step * t * 2 * math.pi)
        pyautogui.move(x, y, _pause=False)
    
    # 3. キー入力：Shiftキーを押下
    pyautogui.press('shift')

def print_program_overview():
    print(f"{BRIGHT}--- {TOOL_NAME} の仕組みと目的 ---{RESET}")
    print(f" 1. {BRIGHT}目的:{RESET} Microsoft Teams等のチャットツールの{BRIGHT}「離席中」判定を確実に回避{RESET}します。")
    print(f" 2. {BRIGHT}監視:{RESET} 5秒ごとにマウスをチェック。あなたが操作している間は邪魔しません。")
    print(f" 3. {BRIGHT}動作:{RESET} 指定時間操作がない場合、{BRIGHT}「マウス移動」＋「Shiftキー」{RESET}を実行。")
    print(f"    この2つの動作により、OSとアプリの両方にアクティブ状態を通知します。")
    print(f" 4. {BRIGHT}安全:{RESET} 動作中にマウスを{BRIGHT}画面の四隅{RESET}へ強く押し当てると、")
    print(f"    緊急停止（安全装置）が働き、プログラムを終了できます。")
    print(f"--------------------------------------------------\n")

def initialize():
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}{BRIGHT}   {TOOL_NAME} - v{TOOL_VERSION}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    
    print_program_overview()

    print(f"{BRIGHT}[設定 1/3]{RESET} 待機時間 (1～60分 / デフォルト: 3分)")
    val = input("   何分間操作がない場合に離席防止を作動させますか？ > ")
    wait_min = int(val) if val.isdecimal() and 1 <= int(val) <= 60 else 3
    
    print(f"\n{BRIGHT}[設定 2/3]{RESET} 自動終了時刻 (例: 18:00 / なしはEnter)")
    end_time_str = input("   業務終了時刻を入力してください > ")
    end_time = None
    if ":" in end_time_str:
        try:
            h, m = map(int, end_time_str.split(":"))
            end_time = (h, m)
        except: pass

    print(f"\n{BRIGHT}[設定 3/3]{RESET} サウンド設定")
    sound_val = input("   サウンドを有効にしますか？ (y/n) [デフォルト: y] > ").lower()
    sound_enabled = False if sound_val == 'n' else True

    if sound_enabled: play_beep(sound_enabled, 'start')
    
    print(f"\n{GREEN}{'#'*60}{RESET}")
    print(f"{GREEN}[{strftime('%H:%M:%S')}] {TOOL_NAME} 監視開始（待機: {wait_min}分）{RESET}")
    print(f"{GREEN}{'#'*60}{RESET}\n")
    
    return wait_min, end_time, sound_enabled

def move_mouse_top():
    sound_enabled = True
    try:
        wait_min, end_time, sound_enabled = initialize()
        check_interval = 5
        wait_threshold_sec = wait_min * 60
        count_sleep_sec = 0
        pos_orig = pyautogui.position()

        while True:
            # 自動終了チェック
            if end_time:
                now = datetime.now()
                if now.hour > end_time[0] or (now.hour == end_time[0] and now.minute >= end_time[1]):
                    print(f"\n{YELLOW}業務終了時刻になりました。自動終了します。お疲れ様でした！{RESET}")
                    play_beep(sound_enabled, 'end')
                    break

            sleep(check_interval)
            pos_current = pyautogui.position()
            dist = math.sqrt((pos_orig.x - pos_current.x)**2 + (pos_orig.y - pos_current.y)**2)
            
            if dist > 20:
                count_sleep_sec = 0
                print(f"[{strftime('%H:%M:%S')}] {CYAN}★ 操作を検知。タイマーをリセットしました{RESET}")
            else:
                count_sleep_sec += check_interval
                print(f"[{strftime('%H:%M:%S')}] {GREEN}静止中... {count_sleep_sec // 60:02d}:{count_sleep_sec % 60:02d} / {wait_min:02d}:00{RESET}")

            pos_orig = pos_current

            if count_sleep_sec >= wait_threshold_sec:
                print(f"[{strftime('%H:%M:%S')}] {RED}{BRIGHT}!!! 離席防止アクション実行中 !!!{RESET}")
                execute_active_relay()
                count_sleep_sec = 0
                pos_orig = pyautogui.position()

    except KeyboardInterrupt:
        print(f"\n{YELLOW}{TOOL_NAME} を終了しました。{RESET}")
        play_beep(sound_enabled, 'end')
    except pyautogui.FailSafeException:
        print(f"\n{RED}{BRIGHT}【緊急停止】安全装置が作動したため、終了しました。{RESET}")
        play_beep(sound_enabled, 'end')

if __name__ == "__main__":
    move_mouse_top()
