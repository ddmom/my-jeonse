import urllib.parse
import streamlit as st
import plotly.graph_objects as go

APP_TITLE = "전세가아드"


############################################################
# 0. 네이버 부동산 검색 URL 만들기
############################################################
def build_naver_search_url(address: str):
    """주소/단지명을 넣으면 네이버 부동산 검색 페이지 URL 생성"""
    address = (address or "").strip()
    if not address:
        return None

    q = urllib.parse.quote(address)
    return f"https://new.land.naver.com/search?sk={q}"


############################################################
# 1. 전세가율 계산 + 위험도 판정
############################################################
def calc_jeonse_ratio(jeonse_deposit, sale_price):
    """전세가율 계산 (전세보증금 / 매매가 * 100)"""
    if sale_price <= 0:
        return None
    return round(jeonse_deposit / sale_price * 100, 1)


def get_risk_level(ratio):
    """전세가율에 따른 위험도와 색상 코드"""
    if ratio is None:
        return "정보 없음", "#7f8c8d"

    if ratio < 60:
        return "안전 영역", "#2ecc71"   # 초록
    elif ratio < 80:
        return "주의 영역", "#f1c40f"   # 노랑
    else:
        return "위험 영역", "#e74c3c"   # 빨강


############################################################
# 2. 도넛 그래프
############################################################
def make_donut_chart(ratio, color):
    """전세가율 도넛 차트 생성"""
    if ratio is None:
        ratio = 0

    fig = go.Figure(
        data=[
            go.Pie(
                values=[ratio, 100 - ratio],
                hole=0.7,
                marker=dict(colors=[color, "#ecf0f1"]),
                textinfo="none",
            )
        ]
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        annotations=[
            dict(
                text=f"{ratio:.1f}%",
                x=0.5,
                y=0.5,
                font=dict(size=26, color=color),
                showarrow=False,
            )
        ],
    )
    return fig


############################################################
# 3. Streamlit UI
############################################################
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🏠", layout="centered")

    st.title("🏠 전세가아드")
    st.caption("매매가·전세보증금으로 전세가율과 위험도를 확인하는 간단 계산기")

    # -----------------------------
    # 0. 주소 → 네이버 부동산 검색
    # -----------------------------
    st.markdown("### 0. 주소로 네이버 부동산 검색")

    addr = st.text_input("아파트 주소 또는 단지명")

    if st.button("네이버 부동산 검색 열기"):
        url = build_naver_search_url(addr)
        if url:
            st.success("아래 링크를 눌러 네이버 부동산에서 시세를 확인하세요.")
            st.markdown(f"[네이버 부동산에서 보기]({url})")
        else:
            st.warning("주소 또는 단지명을 입력해주세요.")

    st.markdown("---")

    # -----------------------------
    # 1. 금액 입력 (단위 텍스트 없음, 숫자만 표시)
    # -----------------------------
    st.markdown("### 1. 매매가 / 전세보증금 입력")

    sale_price = st.number_input("매매가", min_value=0, step=100)
    st.markdown(f"➡ **{sale_price:,}**")

    jeonse_deposit = st.number_input("전세보증금", min_value=0, step=100)
    st.markdown(f"➡ **{jeonse_deposit:,}**")

    # -----------------------------
    # 2. 전세가율 계산 + 결과 표시
    # -----------------------------
    if st.button("전세가율 계산하기"):
        ratio = calc_jeonse_ratio(jeonse_deposit, sale_price)
        risk, color = get_risk_level(ratio)

        st.markdown("### 2. 결과 요약")

        if ratio is None:
            st.warning("매매가를 0보다 큰 값으로 입력해주세요.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("전세가율", f"{ratio}%")
            col2.metric("매매가", f"{sale_price:,}")
            col3.metric("전세보증금", f"{jeonse_deposit:,}")

            # 위험도에 따른 배경색
            risk_bg = {
                "안전 영역": "#E8F8F2",   # 연한 초록
                "주의 영역": "#FFF4D6",   # 연한 노랑
                "위험 영역": "#FFE6E6",   # 연한 빨강
                "정보 없음": "#F0F0F0",
            }.get(risk, "#F0F0F0")

            # 위험도 강조 박스
            st.markdown(
                f"""
                <div style="
                    padding:16px;
                    border-radius:10px;
                    background-color:{risk_bg};
                    border-left:6px solid {color};
                    margin-top:10px;
                ">
                    <span style="font-size:18px; font-weight:600; color:{color};">
                        현재 상태: {risk}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # -------------------------
            # 3. 그래프
            # -------------------------
            st.markdown("### 3. 그래프")
            fig = make_donut_chart(ratio, color)
            st.plotly_chart(fig, use_container_width=True)


############################################################
# 4. 실행
############################################################
if __name__ == "__main__":
    main()
