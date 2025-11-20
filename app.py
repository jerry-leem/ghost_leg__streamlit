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

# 세션 상태 초기화
if 'ladder_generated' not in st.session_state:
    st.session_state.ladder_generated = False
if 'ladder_data' not in st.session_state:
    st.session_state.ladder_data = None
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False


class LadderGame:
    """사다리타기 게임 클래스"""

    def __init__(self, num_players: int, player_names: List[str], prizes: List[str], num_rungs: int = 15):
        """
        Args:
            num_players: 참가자 수
            player_names: 참가자 이름 리스트
            prizes: 상품 리스트
            num_rungs: 가로줄(rung) 수
        """
        self.num_players = num_players
        self.player_names = player_names
        self.prizes = prizes
        self.num_rungs = num_rungs
        self.ladder = self._generate_ladder()

    def _generate_ladder(self) -> List[List[bool]]:
        """
        사다리 가로줄을 랜덤으로 생성

        Returns:
            ladder[row][col]: row번째 높이에서 col번째와 col+1번째 세로줄 사이에 가로줄이 있는지
        """
        ladder = []

        for row in range(self.num_rungs):
            rungs = [False] * (self.num_players - 1)

            # 각 행에서 랜덤하게 가로줄 배치 (연속되지 않도록)
            positions = list(range(self.num_players - 1))
            random.shuffle(positions)

            # 30-50% 정도의 가로줄 생성
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
        시작 위치에서 사다리를 따라 내려가는 경로 추적

        Args:
            start_col: 시작 세로줄 인덱스

        Returns:
            path: (row, col) 튜플의 리스트 (경로)
            end_col: 최종 도착 세로줄 인덱스
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
        """특정 플레이어의 결과 반환"""
        _, end_col = self.trace_path(player_index)
        return self.prizes[end_col]


def draw_ladder_ascii(game: LadderGame, highlight_path: List[Tuple[int, int]] = None) -> str:
    """
    ASCII 아트로 사다리 그리기

    Args:
        game: LadderGame 인스턴스
        highlight_path: 강조할 경로 (row, col) 리스트

    Returns:
        ASCII 아트 문자열
    """
    if highlight_path is None:
        highlight_path = []

    # 경로를 set으로 변환하여 빠른 검색
    path_set = set(highlight_path)

    lines = []

    # 참가자 이름 출력 (상단)
    name_line = "  "
    for i, name in enumerate(game.player_names):
        # 각 이름을 8자로 맞춤
        name_display = name[:7].center(8)
        name_line += name_display + " "
    lines.append(name_line)

    # 시작 라인
    start_line = "  "
    for i in range(game.num_players):
        if (0, i) in path_set:
            start_line += "    ●    "
        else:
            start_line += "    |    "
    lines.append(start_line)

    # 사다리 본체
    for row in range(game.num_rungs):
        # 가로줄
        rung_line = "  "
        for col in range(game.num_players):
            if col < game.num_players - 1 and game.ladder[row][col]:
                # 가로줄이 있음
                if (row, col) in path_set or (row, col + 1) in path_set:
                    rung_line += "    ●════"
                else:
                    rung_line += "    |────"
            else:
                # 가로줄이 없음
                if (row, col) in path_set:
                    rung_line += "    ●    "
                else:
                    rung_line += "    |    "
        lines.append(rung_line)

        # 세로줄
        vert_line = "  "
        for col in range(game.num_players):
            if (row + 1, col) in path_set:
                vert_line += "    ●    "
            else:
                vert_line += "    |    "
        lines.append(vert_line)

    # 상품 출력 (하단)
    prize_line = "  "
    for i, prize in enumerate(game.prizes):
        # 각 상품을 8자로 맞춤
        prize_display = prize[:7].center(8)
        prize_line += prize_display + " "
    lines.append(prize_line)

    return "\n".join(lines)


def main():
    st.title("🪜 사다리타기 게임")
    st.markdown("---")

    # 메인 영역: 게임 설정
    if not st.session_state.ladder_generated:
        st.header("⚙️ 게임 설정")

        # 첫 번째 행: 기본 설정
        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            # 참가자 수를 셀렉트박스로 제공 (빠른 선택용)
            quick_select = st.selectbox(
                "빠른 선택",
                options=[2, 3, 4, 5, 6, 8, 10],
                index=2,  # 기본값 4
                help="일반적으로 많이 사용하는 인원수"
            )
            num_players = quick_select

        with col2:
            # 또는 직접 입력
            custom_players = st.number_input(
                "또는 직접 입력",
                min_value=2,
                max_value=100,
                value=quick_select,
                step=1,
                help="2명에서 100명까지 설정 가능"
            )
            if custom_players != quick_select:
                num_players = custom_players

        with col3:
            # 사다리 복잡도 선택
            complexity = st.select_slider(
                "사다리 복잡도",
                options=["간단", "보통", "복잡"],
                value="보통",
                help="사다리의 가로줄 개수를 결정합니다"
            )
            complexity_map = {"간단": 10, "보통": 15, "복잡": 25}
            num_rungs = complexity_map[complexity]

        st.markdown("---")

        # 두 번째 행: 참가자와 결과 입력
        st.subheader("👥 참가자 및 결과 설정")

        # 탭으로 구분
        tab1, tab2 = st.tabs(["참가자 이름 입력", "결과/상품 입력"])

        with tab1:
            st.info("💡 참가자 이름을 입력해주세요")
            player_names = []

            # 최대 4개씩 컬럼으로 배치
            num_cols = min(4, int(num_players))
            for i in range(0, int(num_players), num_cols):
                cols = st.columns(num_cols)
                for j in range(num_cols):
                    idx = i + j
                    if idx < int(num_players):
                        with cols[j]:
                            name = st.text_input(
                                f"참가자 {idx+1}",
                                value=f"참가자{idx+1}",
                                key=f"player_{idx}",
                                max_chars=10,
                                label_visibility="visible"
                            )
                            player_names.append(name)

        with tab2:
            st.info("🎁 각 결과(상품, 당첨 여부 등)를 입력해주세요")
            prizes = []

            # 최대 4개씩 컬럼으로 배치
            num_cols = min(4, int(num_players))
            for i in range(0, int(num_players), num_cols):
                cols = st.columns(num_cols)
                for j in range(num_cols):
                    idx = i + j
                    if idx < int(num_players):
                        with cols[j]:
                            prize = st.text_input(
                                f"결과 {idx+1}",
                                value=f"상품{idx+1}",
                                key=f"prize_{idx}",
                                max_chars=10,
                                label_visibility="visible"
                            )
                            prizes.append(prize)

        st.markdown("---")

        # 세 번째 행: 버튼들
        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            # 사다리 생성 버튼
            if st.button("🎲 사다리 생성", type="primary", use_container_width=True):
                game = LadderGame(int(num_players), player_names, prizes, num_rungs)
                st.session_state.ladder_data = game
                st.session_state.ladder_generated = True
                st.session_state.animation_running = False
                st.success("✅ 사다리가 생성되었습니다!")
                st.rerun()

        with col2:
            # 리셋 버튼
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.ladder_generated = False
                st.session_state.ladder_data = None
                st.session_state.animation_running = False
                st.rerun()

        st.markdown("---")

        # 게임 설명
        with st.expander("📖 게임 규칙 보기", expanded=False):
            st.markdown("""
            1. **참가자 설정**: 셀렉트박스에서 빠르게 선택하거나 직접 입력합니다 (2~100명).
            2. **복잡도 설정**: 사다리의 복잡도를 간단/보통/복잡 중에서 선택합니다.
            3. **이름 입력**: 각 참가자의 이름을 입력합니다.
            4. **결과 입력**: 각 결과(상품, 당첨 여부 등)를 입력합니다.
            5. **사다리 생성**: '사다리 생성' 버튼을 눌러 사다리를 랜덤으로 생성합니다.
            6. **결과 확인**: 참가자를 선택하면 애니메이션과 함께 결과가 표시됩니다.

            **사다리타기 규칙**:
            - 위에서 아래로 내려가면서 가로줄을 만나면 반드시 건너갑니다.
            - 가로줄이 없으면 계속 직진합니다.
            - 모든 참가자는 중복되지 않는 고유한 결과를 받습니다.
            """)
    else:
        game = st.session_state.ladder_data

        # 상단에 초기화 버튼 추가
        col1, col2 = st.columns([5, 1])
        with col1:
            st.header("🎮 사다리타기 시작!")
        with col2:
            if st.button("🔄 다시 설정", use_container_width=True):
                st.session_state.ladder_generated = False
                st.session_state.ladder_data = None
                st.session_state.animation_running = False
                st.rerun()

        st.markdown("---")

        # 참가자 선택
        st.subheader("👤 참가자 선택")

        cols = st.columns(min(game.num_players, 6))

        for i in range(game.num_players):
            with cols[i % 6]:
                if st.button(
                    f"{game.player_names[i]}",
                    key=f"select_{i}",
                    use_container_width=True,
                    type="primary" if not st.session_state.animation_running else "secondary",
                    disabled=st.session_state.animation_running
                ):
                    # 애니메이션 시작
                    st.session_state.animation_running = True

                    # 경로 추적
                    path, end_col = game.trace_path(i)
                    result = game.prizes[end_col]

                    # 결과 표시 영역
                    st.markdown("---")
                    st.subheader(f"🎯 {game.player_names[i]}님의 결과")

                    # 애니메이션 컨테이너
                    animation_container = st.empty()

                    # 단계별 애니메이션
                    for step in range(len(path) + 1):
                        current_path = path[:step]
                        ladder_display = draw_ladder_ascii(game, current_path)

                        with animation_container.container():
                            st.code(ladder_display, language=None)

                        if step < len(path):
                            time.sleep(0.15)  # 애니메이션 속도 조절

                    # 최종 결과 표시
                    st.success(f"## 🎊 결과: **{result}**")

                    st.session_state.animation_running = False

        # 사다리 표시
        if not st.session_state.animation_running:
            st.markdown("---")
            st.subheader("🪜 사다리")
            ladder_display = draw_ladder_ascii(game)
            st.code(ladder_display, language=None)

        # 결과 미리보기 (숨김 처리)
        with st.expander("🔍 결과 미리보기 (스포일러 주의!)"):
            st.warning("⚠️ 결과를 미리 보시겠습니까? 게임의 재미가 반감될 수 있습니다!")

            if st.checkbox("결과 보기"):
                results_data = []
                for i in range(game.num_players):
                    _, end_col = game.trace_path(i)
                    result = game.prizes[end_col]
                    results_data.append({
                        "참가자": game.player_names[i],
                        "결과": result
                    })

                df = pd.DataFrame(results_data)
                st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
