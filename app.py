import streamlit as st
import random
import time
import pandas as pd
from typing import List, Tuple, Dict

# 페이지 설정
st.set_page_config(
    page_title="사다리타기 게임",
    page_icon="🪜",
    layout="wide"
)

# CSS 스타일 정의
def get_ladder_css():
    """사다리 시각화를 위한 CSS 스타일 반환"""
    return """
    <style>
    /* 사다리 컨테이너 스타일 */
    .ladder-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        margin: 20px auto;
        width: 100%;
        max-width: none;
    }

    /* 참가자 이름 영역 */
    .ladder-names {
        display: flex;
        justify-content: space-around;
        width: 100%;
        margin-bottom: 30px;
    }

    .ladder-name {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        text-align: center;
        padding: 15px 20px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .ladder-name.highlight {
        background: rgba(255, 215, 0, 0.8);
        color: #000;
        transform: scale(1.1);
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.5);
    }

    /* 사다리 본체 영역 */
    .ladder-body {
        display: flex;
        justify-content: space-around;
        position: relative;
        width: 100%;
        min-height: 1000px;
    }

    /* 세로 라인 */
    .ladder-vertical {
        position: relative;
        width: 8px;
        background: linear-gradient(180deg, #fff 0%, #e0e0e0 100%);
        border-radius: 4px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    }

    .ladder-vertical.highlight {
        background: linear-gradient(180deg, #ffd700 0%, #ffed4e 100%);
        width: 12px;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.9);
        animation: pulse 0.5s ease-in-out;
    }

    /* 가로 라인 */
    .ladder-rung {
        position: absolute;
        height: 8px;
        background: linear-gradient(90deg, #fff 0%, #f0f0f0 50%, #fff 100%);
        border-radius: 4px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .ladder-rung.highlight {
        background: linear-gradient(90deg, #ffd700 0%, #ffed4e 50%, #ffd700 100%);
        height: 12px;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.9);
        animation: glow 0.5s ease-in-out;
    }

    /* 이동 포인트 (공) */
    .ladder-ball {
        position: absolute;
        width: 30px;
        height: 30px;
        background: radial-gradient(circle at 30% 30%, #ffd700, #ff6b6b);
        border-radius: 50%;
        box-shadow: 0 0 30px rgba(255, 107, 107, 0.9);
        transform: translate(-50%, -50%);
        animation: bounce 0.3s ease-in-out;
        z-index: 10;
    }

    /* 상품 영역 */
    .ladder-prizes {
        display: flex;
        justify-content: space-around;
        width: 100%;
        margin-top: 30px;
    }

    .ladder-prize {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        text-align: center;
        padding: 15px 20px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .ladder-prize.highlight {
        background: rgba(255, 107, 107, 0.8);
        color: #fff;
        transform: scale(1.2);
        box-shadow: 0 5px 20px rgba(255, 107, 107, 0.6);
        animation: tada 0.5s ease-in-out;
    }

    /* 애니메이션 정의 */
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    @keyframes glow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    @keyframes bounce {
        0%, 100% { transform: translate(-50%, -50%) scale(1); }
        50% { transform: translate(-50%, -50%) scale(1.3); }
    }

    @keyframes tada {
        0% { transform: scale(1) rotate(0deg); }
        10%, 20% { transform: scale(0.9) rotate(-3deg); }
        30%, 50%, 70%, 90% { transform: scale(1.1) rotate(3deg); }
        40%, 60%, 80% { transform: scale(1.1) rotate(-3deg); }
        100% { transform: scale(1) rotate(0deg); }
    }
    </style>
    """

# 세션 상태 초기화
if 'ladder_generated' not in st.session_state:
    st.session_state.ladder_generated = False  # 사다리 생성 여부
if 'ladder_data' not in st.session_state:
    st.session_state.ladder_data = None  # 사다리 게임 데이터
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False  # 애니메이션 실행 상태


class LadderGame:
    """사다리타기 게임 클래스 - 사다리 생성 및 경로 추적 기능 제공"""

    def __init__(self, num_players: int, player_names: List[str], prizes: List[str], num_rungs: int = 15):
        """
        사다리타기 게임 초기화

        매개변수:
            num_players: 참가자 수
            player_names: 참가자 이름 리스트
            prizes: 상품(결과) 리스트
            num_rungs: 사다리 가로줄 개수 (기본값: 15)
        """
        self.num_players = num_players
        self.player_names = player_names
        self.prizes = prizes
        self.num_rungs = num_rungs
        self.ladder = self._generate_ladder()

    def _generate_ladder(self) -> List[List[bool]]:
        """
        사다리의 가로줄을 랜덤으로 생성

        반환값:
            ladder[row][col]: row번째 높이에서 col번째와 col+1번째 세로줄 사이에
                              가로줄이 있는지 여부를 나타내는 2차원 불린 배열
        """
        ladder = []

        for row in range(self.num_rungs):
            rungs = [False] * (self.num_players - 1)

            # 각 행에서 랜덤하게 가로줄 배치 (연속된 가로줄이 생기지 않도록 함)
            positions = list(range(self.num_players - 1))
            random.shuffle(positions)

            # 전체 가능한 위치의 30-50% 정도만 가로줄 생성
            num_rungs_in_row = random.randint(
                max(1, (self.num_players - 1) // 3),
                max(2, (self.num_players - 1) // 2)
            )

            for i in range(num_rungs_in_row):
                pos = positions[i]
                # 연속된 가로줄이 없도록 확인
                can_place = True
                if pos > 0 and rungs[pos - 1]:
                    can_place = False
                if pos < len(rungs) - 1 and rungs[pos + 1]:
                    can_place = False

                if can_place:
                    rungs[pos] = True

            ladder.append(rungs)

        return ladder

    def trace_path(self, start_col: int) -> Tuple[List[Tuple[int, int]], int]:
        """
        시작 위치에서 사다리를 따라 내려가는 경로를 추적

        매개변수:
            start_col: 시작 세로줄의 인덱스 (0부터 시작)

        반환값:
            path: 경로상의 모든 위치를 나타내는 (row, col) 튜플 리스트
            end_col: 최종 도착한 세로줄의 인덱스
        """
        current_col = start_col
        path = [(0, current_col)]

        for row in range(self.num_rungs):
            # 현재 위치에서 왼쪽으로 가로줄이 있는지 확인
            if current_col > 0 and self.ladder[row][current_col - 1]:
                # 왼쪽으로 이동
                path.append((row, current_col - 1))
                current_col -= 1
            # 현재 위치에서 오른쪽으로 가로줄이 있는지 확인
            elif current_col < self.num_players - 1 and self.ladder[row][current_col]:
                # 오른쪽으로 이동
                path.append((row, current_col + 1))
                current_col += 1
            else:
                # 가로줄이 없으면 아래로만 이동
                path.append((row + 1, current_col))

        return path, current_col

    def get_result(self, player_index: int) -> str:
        """
        특정 참가자의 최종 결과(상품)를 반환

        매개변수:
            player_index: 참가자 인덱스

        반환값:
            해당 참가자가 도달한 상품(결과)
        """
        _, end_col = self.trace_path(player_index)
        return self.prizes[end_col]


def draw_ladder_html(game: LadderGame, highlight_path: List[Tuple[int, int]] = None,
                     current_position: Tuple[int, int] = None) -> str:
    """
    HTML/CSS로 사다리를 그리기 (부드러운 애니메이션 효과 포함)

    매개변수:
        game: LadderGame 인스턴스
        highlight_path: 강조 표시할 경로 [(row, col), ...] 형식의 리스트
        current_position: 현재 이동 중인 볼의 위치 (row, col)

    반환값:
        렌더링할 HTML 문자열 (CSS 스타일 포함)
    """
    if highlight_path is None:
        highlight_path = []

    # 경로를 set으로 변환하여 빠른 검색
    path_set = set(highlight_path)

    # 경로의 시작과 끝 열 찾기
    start_col = highlight_path[0][1] if highlight_path else -1
    end_col = highlight_path[-1][1] if highlight_path else -1

    html = ['<div class="ladder-container">']

    # 참가자 이름 영역
    html.append('<div class="ladder-names">')
    for i, name in enumerate(game.player_names):
        highlight_class = ' highlight' if i == start_col and highlight_path else ''
        html.append(f'<div class="ladder-name{highlight_class}">{name}</div>')
    html.append('</div>')

    # 사다리 본체 영역
    html.append('<div class="ladder-body">')

    # 각 세로 라인마다 처리
    ladder_height = 1000  # 픽셀 단위
    rung_spacing = ladder_height / (game.num_rungs + 1)

    # 세로 라인들 먼저 그리기
    for col in range(game.num_players):
        # 이 세로 라인이 경로에 포함되는지 확인
        is_in_path = any(pos[1] == col for pos in highlight_path)
        highlight_class = ' highlight' if is_in_path else ''

        html.append(f'<div class="ladder-vertical{highlight_class}"></div>')

    # 가로 라인들을 ladder-body 레벨에서 그리기
    for row in range(game.num_rungs):
        for col in range(game.num_players - 1):
            if game.ladder[row][col]:
                # 가로 라인이 있는 경우
                top_position = (row + 1) * rung_spacing

                # 이 가로 라인이 경로에 포함되는지 확인
                rung_in_path = (row, col) in path_set or (row, col + 1) in path_set
                rung_highlight = ' highlight' if rung_in_path else ''

                # 가로 라인의 위치와 너비 계산
                col_width = 100 / game.num_players
                left_percent = col * col_width + col_width / 2
                width_percent = col_width

                html.append(
                    f'<div class="ladder-rung{rung_highlight}" '
                    f'style="position: absolute; top: {top_position}px; left: {left_percent}%; width: {width_percent}%;"></div>'
                )

    # 현재 위치에 볼 표시 (애니메이션 중일 때)
    if current_position is not None:
        row, col = current_position
        # 볼의 위치 계산
        col_width = 100 / game.num_players
        left_percent = col * col_width + col_width / 2
        top_position = (row + 1) * rung_spacing if row < game.num_rungs else ladder_height

        html.append(
            f'<div class="ladder-ball" '
            f'style="left: {left_percent}%; top: {top_position}px;"></div>'
        )

    html.append('</div>')

    # 상품 영역
    html.append('<div class="ladder-prizes">')
    for i, prize in enumerate(game.prizes):
        highlight_class = ' highlight' if i == end_col and highlight_path else ''
        html.append(f'<div class="ladder-prize{highlight_class}">{prize}</div>')
    html.append('</div>')

    html.append('</div>')

    return ''.join(html)


def main():
    # CSS 스타일 적용
    st.markdown(get_ladder_css(), unsafe_allow_html=True)

    st.title("🪜 사다리타기 게임")
    st.markdown("---")

    # 메인 영역: 게임 설정
    st.header("⚙️ 게임 설정")

    # 인원 수 입력
    num_players = st.number_input(
        "참가자 수",
        min_value=2,
        max_value=100,
        value=4,
        step=1,
        help="2명에서 100명까지 설정 가능합니다."
    )

    st.markdown("---")

    # 참가자 이름 입력
    st.subheader("👥 참가자 이름")
    cols_players = st.columns(min(int(num_players), 4))
    player_names = []
    for i in range(int(num_players)):
        with cols_players[i % 4]:
            name = st.text_input(
                f"참가자 {i+1}",
                value=f"참가자{i+1}",
                key=f"player_{i}",
                max_chars=10
            )
            player_names.append(name)

    st.markdown("---")

    # 상품/결과 입력
    st.subheader("🎁 결과 (상품/당첨)")
    cols_prizes = st.columns(min(int(num_players), 4))
    prizes = []
    for i in range(int(num_players)):
        with cols_prizes[i % 4]:
            prize = st.text_input(
                f"결과 {i+1}",
                value=f"상품{i+1}",
                key=f"prize_{i}",
                max_chars=10
            )
            prizes.append(prize)

    st.markdown("---")

    # 사다리 가로줄 수 설정
    num_rungs = st.slider(
        "사다리 가로줄 수",
        min_value=10,
        max_value=30,
        value=15,
        step=1,
        help="사다리의 복잡도를 조절합니다."
    )

    st.markdown("---")

    # 버튼 영역
    button_col1, button_col2 = st.columns(2)

    with button_col1:
        # 사다리 생성 버튼
        if st.button("🎲 사다리 생성", type="primary", use_container_width=True):
            game = LadderGame(int(num_players), player_names, prizes, num_rungs)
            st.session_state.ladder_data = game
            st.session_state.ladder_generated = True
            st.session_state.animation_running = False
            st.success("✅ 사다리가 생성되었습니다!")

    with button_col2:
        # 리셋 버튼
        if st.button("🔄 초기화", use_container_width=True):
            st.session_state.ladder_generated = False
            st.session_state.ladder_data = None
            st.session_state.animation_running = False
            st.rerun()

    st.markdown("---")

    # 메인 영역
    if not st.session_state.ladder_generated:
        # 게임 설명
        st.markdown("## 📖 게임 규칙")
        st.markdown("""
        1. **참가자 설정**: 2명에서 100명까지 참가자 수를 선택합니다.
        2. **이름 입력**: 각 참가자의 이름을 입력합니다.
        3. **결과 입력**: 각 결과(상품, 당첨 여부 등)를 입력합니다.
        4. **사다리 생성**: '사다리 생성' 버튼을 눌러 사다리를 랜덤으로 생성합니다.
        5. **결과 확인**: 참가자를 선택하면 애니메이션과 함께 결과가 표시됩니다.

        **사다리타기 규칙**:
        - 위에서 아래로 내려가면서 가로줄을 만나면 반드시 건너갑니다.
        - 가로줄이 없으면 계속 직진합니다.
        - 모든 참가자는 중복되지 않는 고유한 결과를 받습니다.
        """)
    else:
        game = st.session_state.ladder_data

        # 참가자 선택 - 애니메이션 실행 중에는 숨김
        if not st.session_state.animation_running:
            st.subheader("👤 참가자 선택")

            cols = st.columns(min(int(num_players), 6))

            for i in range(int(num_players)):
                with cols[i % 6]:
                    if st.button(
                        f"{player_names[i]}",
                        key=f"select_{i}",
                        use_container_width=True,
                        type="primary"
                    ):
                        # 애니메이션 시작
                        st.session_state.animation_running = True

                        # 경로 추적
                        path, end_col = game.trace_path(i)
                        result = game.prizes[end_col]

                        # 결과 표시 영역 - 전체 화면으로 표시
                        st.markdown("---")
                        st.subheader(f"🎯 {player_names[i]}님의 결과")

                        # 애니메이션 컨테이너
                        animation_container = st.empty()

                        # 단계별 애니메이션
                        for step in range(len(path) + 1):
                            current_path = path[:step]
                            current_pos = path[step - 1] if step > 0 else None

                            # HTML 사다리 렌더링
                            ladder_html = draw_ladder_html(game, current_path, current_pos)

                            # 애니메이션 컨테이너에 직접 출력 (전체 폭 사용)
                            animation_container.markdown(ladder_html, unsafe_allow_html=True)

                            if step < len(path):
                                time.sleep(0.2)  # 애니메이션 속도 조절

                        # 최종 결과 표시
                        st.success(f"## 🎊 결과: **{result}**")

                        st.session_state.animation_running = False

        # 사다리 표시
        if not st.session_state.animation_running:
            st.markdown("---")
            st.subheader("🪜 사다리")
            ladder_html = draw_ladder_html(game)
            st.markdown(ladder_html, unsafe_allow_html=True)

        # 결과 미리보기 (숨김 처리)
        with st.expander("🔍 결과 미리보기 (스포일러 주의!)"):
            st.warning("⚠️ 결과를 미리 보시겠습니까? 게임의 재미가 반감될 수 있습니다!")

            if st.checkbox("결과 보기"):
                results_data = []
                for i in range(int(num_players)):
                    _, end_col = game.trace_path(i)
                    result = game.prizes[end_col]
                    results_data.append({
                        "참가자": player_names[i],
                        "결과": result
                    })

                df = pd.DataFrame(results_data)
                st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
