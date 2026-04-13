import mss
import mss.tools
import time
import os
from pynput import mouse, keyboard

# 저장될 폴더 설정
SAVE_FOLDER = "screenshots"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def main():
    print("=== 🖥️ 듀얼 모니터 지정 영역 캡처 프로그램 ===\n")
    
    # ---------------------------------------------------------
    # 1. 모니터 감지 및 선택 메뉴
    # ---------------------------------------------------------
    with mss.mss() as sct:
        monitors = sct.monitors
        print("[연결된 모니터 목록]")
        # monitors[0]은 가상 통합 모니터이므로 1번부터 출력
        for i in range(1, len(monitors)):
            m = monitors[i]
            print(f"모니터 {i} 👉 해상도: {m['width']}x{m['height']} (시작 좌표: {m['left']}, {m['top']})")
            
    try:
        monitor_idx = int(input("\n🎯 캡처를 진행할 모니터 번호를 입력하세요 (예: 1 또는 2): "))
        if monitor_idx < 1 or monitor_idx >= len(monitors):
            print("❌ 오류: 유효하지 않은 모니터 번호입니다. 프로그램을 종료합니다.")
            return
    except ValueError:
        print("❌ 오류: 숫자를 입력하셔야 합니다.")
        return

    print(f"\n✅ [준비 완료] 모니터 {monitor_idx}번이 선택되었습니다.")

    # ---------------------------------------------------------
    # 2. 마우스 클릭으로 캡처 영역 지정
    # ---------------------------------------------------------
    click_coords = []
    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            click_coords.append((int(x), int(y)))
            if len(click_coords) == 1:
                print(f"   ✔️ 1/2 시작점 지정: {click_coords[0]}")
            elif len(click_coords) == 2:
                print(f"   ✔️ 2/2 종료점 지정: {click_coords[1]}")
                return False # 두 번 클릭하면 마우스 감지 종료

    print("👉 캡처할 영역의 '좌측 상단'과 '우측 하단'을 마우스로 한 번씩 클릭하세요.")
    with mouse.Listener(on_click=on_click) as m_listener:
        m_listener.join()
        
    x1, y1 = click_coords[0]
    x2, y2 = click_coords[1]
    
    # 클릭 순서가 뒤바뀌어도 올바른 사각형 영역을 잡도록 계산
    capture_area = {
        "top": min(y1, y2), 
        "left": min(x1, x2), 
        "width": abs(x2 - x1), 
        "height": abs(y2 - y1)
    }
    print(f"✅ 영역 설정 완료: 가로 {capture_area['width']}px, 세로 {capture_area['height']}px")

    # ---------------------------------------------------------
    # 3. 메인 캡처 루프 (안전하고 가벼운 pynput Events 방식)
    # ---------------------------------------------------------
    page = 1
    print("\n=================================================")
    print(" ⌨️  [오른쪽 방향키] : 지정한 영역 캡처 및 저장")
    print(" ⌨️  [ESC 키]        : 프로그램 종료")
    print("=================================================\n")
    
    with mss.mss() as sct:
        # 키보드 입력이 있을 때만 루프가 반응함 (CPU 최적화)
        with keyboard.Events() as events:
            for event in events:
                # 키를 '누를 때(Press)'만 작동 (뗄 때는 무시)
                if isinstance(event, keyboard.Events.Press):
                    
                    # 오른쪽 방향키 처리
                    if event.key == keyboard.Key.right:
                        # 파일명에 모니터 번호와 페이지 번호 포함
                        filename = f"monitor{monitor_idx}_page_{page}.png"
                        filepath = os.path.join(SAVE_FOLDER, filename)
                        
                        # 캡처 및 저장
                        sct_img = sct.grab(capture_area)
                        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filepath)
                        
                        print(f"📸 {page}페이지 캡처 완료! -> {filename}")
                        page += 1
                        
                    # ESC 처리 (프로그램 안전 종료)
                    elif event.key == keyboard.Key.esc:
                        print("\n🛑 종료 키(ESC)가 입력되었습니다. 프로그램을 안전하게 종료합니다.")
                        break

if __name__ == "__main__":
    main()