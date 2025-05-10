import streamlit as st
import random

st.set_page_config(page_title="어린이날 경품 추첨기", page_icon="🎁")

st.title("🎉 2025 어린이날 경품 추첨기 🎉")
st.markdown("선물별로 당첨자를 랜덤으로 뽑아드립니다!")

# 참가자
all_numbers = list(range(1, 71))

# 선물 목록
gifts = {
    "카피바라 인형": 3,
    "오리 인형": 3,
    "스파이더맨 장갑": 3,
    "예수님 블록": 5,
    "젤리세트": 6,
    "기타 소소한 선물": 50,
}

if st.button("🎁 추첨 시작"):
    available_numbers = all_numbers.copy()
    results = []

    for gift, count in gifts.items():
        if count > len(available_numbers):
            st.warning(f"'{gift}' 추첨 인원이 부족합니다!")
            continue

        selected = random.sample(available_numbers, count)
        for num in selected:
            available_numbers.remove(num)

        results.append((gift, selected))

    st.subheader("📋 추첨 결과")
    for gift, winners in results:
        winner_text = ', '.join(f"{num}번" for num in winners)
        st.markdown(f"**[{gift}]** ➜ {winner_text}")

    st.success("🎊 추첨이 완료되었습니다!")
