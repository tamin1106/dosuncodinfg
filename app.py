import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(page_title='나의 데이터 웹앱', page_icon='📊', layout='wide')

st.title("나의 데이터 웹앱")
tab1, tab2 = st.tabs(["🍽️ Tips 대시보드", "🗺️ 서울 지도"])

with tab1:
    @st.cache_data
    def load_data():
        try:
            return pd.read_csv('tips.csv')
        except FileNotFoundError:
            st.error("🚨 'tips.csv' 파일이 존재하지 않습니다.")
            return pd.DataFrame()

    df = load_data()
    if not df.empty:
        df.rename(columns={'sex': '성별'}, inplace=True)

        st.sidebar.header('🔍 Filters')
        day_filter = st.sidebar.multiselect('요일 선택', options=df['day'].unique(), default=df['day'].unique())
        sex_filter = st.sidebar.multiselect('성별 선택', options=df['성별'].unique(), default=df['성별'].unique())
        smoker_filter = st.sidebar.multiselect('흡연 여부 선택', options=df['smoker'].unique(), default=df['smoker'].unique())

        filtered_df = df[
            (df['day'].isin(day_filter)) & (df['성별'].isin(sex_filter)) & (df['smoker'].isin(smoker_filter))
        ]
        with st.expander(f'📊 필터링된 데이터 (총 {filtered_df.shape[0]}개 행)'):
            st.dataframe(filtered_df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric('💰 총 결제금액 합계', round(filtered_df['total_bill'].sum(), 2))
        col2.metric('💵 팁 평균', round(filtered_df['tip'].mean(), 2))
        col3.metric('👥 평균 인원 수', round(filtered_df['size'].mean(), 2))
        col4.metric('🍽️ 총 팁 수령 합계', round(filtered_df['tip'].sum(), 2))

        st.sidebar.write('')
        st.sidebar.header('시각화 옵션')
        figure_type = st.sidebar.selectbox('시각화 형태 선택', ['px.scatter', 'px.bar', 'px.pie'])
        x_data = st.sidebar.selectbox('X축 데이터 선택', ['성별', 'smoker', 'day', 'size'])
        y_data = st.sidebar.selectbox('Y축 데이터 선택', ['total_bill', 'tip'])

        st.subheader('시각화')
        if figure_type == 'px.scatter':
            fig = px.scatter(filtered_df, x=x_data, y=y_data, color=x_data, size=y_data,
                             title=f'{x_data} vs {y_data} (산점도)')
            st.plotly_chart(fig, use_container_width=True)
        elif figure_type == 'px.bar':
            fig = px.bar(filtered_df, x=x_data, y=y_data, color=x_data,
                        title=f'{x_data} 별 {y_data} (막대 그래프)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.pie(filtered_df, names=x_data, values=y_data,
                        title=f'{x_data} 비율 (파이차트)')
            st.plotly_chart(fig, use_container_width=True)

        st.subheader('탐색적 데이터 분석')
        eda_option = st.selectbox(
            "분석 항목을 선택하세요:",
            ["결제 금액과 팁 간의 상관관계", "요일별 평균 팁", "흡연 여부에 따른 팁 차이"]
        )

        if eda_option == "결제 금액과 팁 간의 상관관계":
            fig = px.scatter(filtered_df, x='total_bill', y='tip', color='성별',
                             trendline='ols', title='결제금액 vs 팁')
            st.plotly_chart(fig, use_container_width=True)
            correlation = filtered_df['total_bill'].corr(filtered_df['tip'])
            st.info(f"결제 금액과 팁 간의 상관계수: {correlation:.2f}")
        elif eda_option == "요일별 평균 팁":
            avg_tip_by_day = filtered_df.groupby('day')['tip'].mean().reset_index()
            fig = px.bar(avg_tip_by_day, x='day', y='tip', color='day', title='요일별 평균 팁 금액')
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.box(filtered_df, x='smoker', y='tip', color='smoker',
                        title='흡연 여부에 따른 팁 분포 (Boxplot)')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("4차시에 만든 지도")
    # TODO: 업로드한 지도 파일명을 문자열로 직접 적으세요 (예: "my_wifi_map.html")
    # 주의: app.py는 코랩과 별개로 실행되는 독립된 파일이라 MAP_FILE 변수를 그대로 쓸 수 없습니다.
    with open("bike_station_map.html", "r", encoding="utf-8") as f:  # 예시: "my_wifi_map.html" — 실제 업로드한 파일명으로 교체
        map_html = f.read()
    components.html(map_html, height=600)
