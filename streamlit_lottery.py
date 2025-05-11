import streamlit as st
import random
import time
import pandas as pd
from io import StringIO

st.set_page_config(page_title="경품 추첨기", page_icon="🏱")

# 초기화
if 'step' not in st.session_state:
    st.session_state.step = 'input'
    st.session_state.available_numbers = []
    st.session_state.draw_results = {}
    st.session_state.active_draw = None
    st.session_state.draw_order = []
    st.session_state.waiting_for_audio = False

def reset():
    st.session_state.step = 'input'
    st.session_state.available_numbers = []
    st.session_state.draw_results = {}
    st.session_state.active_draw = None
    st.session_state.draw_order = []
    st.session_state.waiting_for_audio = False

# 🌟 Step 1: 입력
if st.session_state.step == 'input':
    st.title("🎈 경품 추첨기 - 설정")

    event_title = st.text_input("✅ 추첨 제목", "2025 여름학원 추첨기")
    total_people = st.number_input("참가자 수", min_value=1, value=70)
    raw_gift_input = st.text_area("🏱 선물 목록 (예: 오리 인형:3)", value="오리 인형:50")
    excluded_text = st.text_input("⛔ 제외할 번호 입력 (쉼표로 구분, 예: 7,13,29)", value="")

    if st.button("🎬 추첨 시작"):
        st.session_state.title = event_title

        # 제외 번호 처리
        excluded_numbers = []
        try:
            excluded_numbers = [int(x.strip()) for x in excluded_text.split(',') if x.strip()]
        except ValueError:
            st.error("제외 번호는 숫자만 쉼표로 입력해야 합니다.")
            st.stop()

        available = list(range(1, total_people + 1))
        available = [num for num in available if num not in excluded_numbers]
        st.session_state.available_numbers = available

        # 선물 파싱
        gifts = {}
        for line in raw_gift_input.strip().splitlines():
            if ':' in line:
                name, count = line.split(':')
                gifts[name.strip()] = int(count.strip())
        st.session_state.gifts = gifts
        st.session_state.step = 'run'
        st.session_state.excluded = excluded_numbers
        st.rerun()

# 🏱 Step 2: 추첨 화면
elif st.session_state.step == 'run':
    st.title(f"🏱 {st.session_state.title}")
    st.button("🔄 리셋", on_click=reset)

    st.markdown(f"⛔ 제외된 번호: {st.session_state.excluded}")
    st.markdown(f"🎯 추첨 대상 인원 수: {len(st.session_state.available_numbers)}명")

    search_num = st.number_input("🔍 특정 번호로 어느 선물 당첨되었는지 확인", min_value=1, max_value=999, step=1)
    found = []
    for gift, winners in st.session_state.draw_results.items():
        if search_num in winners:
            found.append(f"{gift}")

    if found:
        st.success(f"🎉 {search_num}번은 다음 선물에 당첨되었습니다: {', '.join(found)}")
    else:
        st.info(f"{search_num}번은 아직 당첨되지 않았습니다.")

    st.divider()

    if st.session_state.waiting_for_audio:
        st.audio("https://raw.githubusercontent.com/no5kio/lottery/main/asset/drum-roll-sound-effect_cut_2sec.mp3", format="audio/mp3")
        time.sleep(2)  # 2초 대기
        gift_name, winners = st.session_state.active_draw
        st.session_state.waiting_for_audio = False
        st.session_state.active_draw = None

        st.markdown(f"### 🎉 [{gift_name}] 추첨 결과")
        placeholder = st.empty()
        row = ""
        for i, w in enumerate(winners, 1):
            row += f"**{w}번**  "
            placeholder.markdown(row)
            time.sleep(0.1)

        st.markdown(f"✅ 총 {len(winners)}명 당첨")
        st.balloons()
        st.success(f"🎊 [{gift_name}] 추첨 완료!")

    else:
        for gift_name, quantity in st.session_state.gifts.items():
            if gift_name in st.session_state.draw_results:
                st.success(f"✅ [{gift_name}] 추첨 완료!")
            else:
                if st.button(f"🎯 {gift_name} ({quantity}명)", key=gift_name):
                    winners = random.sample(
                        st.session_state.available_numbers,
                        min(quantity, len(st.session_state.available_numbers))
                    )
                    for w in winners:
                        if w in st.session_state.available_numbers:
                            st.session_state.available_numbers.remove(w)
                    st.session_state.draw_results[gift_name] = winners
                    st.session_state.draw_order.append(gift_name)
                    st.session_state.active_draw = (gift_name, winners)
                    st.session_state.waiting_for_audio = True
                    st.rerun()

    # 모든 결과 추적 + 오름차순 정렬하여 표시
    if st.session_state.draw_order:
        st.markdown("---")
        st.header("📋 전체 추첨 결과")
        total_winner_count = 0

        result_data = []
        for gift_name in st.session_state.draw_order:
            winners = sorted(st.session_state.draw_results[gift_name])
            winner_str = ', '.join(f"**{num}번**" for num in winners)
            total_winner_count += len(winners)
            st.markdown(f"🏱 **{gift_name}** → {winner_str} _(총 {len(winners)}명)_")

            for w in winners:
                result_data.append({"선물명": gift_name, "번호": w})

        st.success(f"🌟 모든 선물 당첨자 수: {total_winner_count}명")

        # CSV 다운로드 버튼
        df_result = pd.DataFrame(result_data)
        csv = df_result.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 당첨 결과 CSV 다운로드",
            data=csv,
            file_name="경품추첨결과.csv",
            mime="text/csv"
        )
