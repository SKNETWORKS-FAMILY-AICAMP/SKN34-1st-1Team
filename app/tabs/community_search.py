import streamlit as st

from app.db import execute_sql
from app.services import safe_load, save_dataframe
from app.sources import search_community_posts


def render() -> None:
    st.subheader("기름값을 아낄 수 있는 자동차 커뮤니티 검색")

    keyword = st.text_input("검색어", value="연비 좋은 차")

    col1, _ = st.columns([1, 4])
    with col1:
        do_search = st.button("검색/크롤링")

    if do_search:
        try:
            execute_sql("DELETE FROM community_posts")

            posts = search_community_posts(keyword)

            if posts.empty:
                st.info("수집된 검색 결과가 없습니다.")
            else:
                save_dataframe(posts, "community_posts")
                st.cache_data.clear()
                st.success(f"{len(posts):,}건을 새로 수집했습니다.")

        except Exception as exc:
            st.error(f"검색 수집에 실패했습니다: {exc}")

    posts = safe_load("community_posts")

    if posts.empty:
        st.info("검색 버튼을 눌러 공개 웹 검색 결과를 수집하세요.")
        return

    for _, row in posts.sort_values("crawled_at", ascending=False).head(30).iterrows():
        st.markdown(f"**[{row['title']}]({row['url']})**")
        st.caption(
            f"{row.get('source', '')} · "
            f"{row.get('keyword', '')} · "
            f"{row.get('crawled_at', '')}"
        )

        if row.get("snippet"):
            st.write(row["snippet"])

        st.divider()