import streamlit as st
from rapidfuzz import fuzz

st.title("K-Read Coach Test")
st.write("If you see this in the browser, your setup is working!")

# Test your comparison logic
score = fuzz.ratio("안녕하세요", "안녕")
st.write(f"Test similarity score: {score}%")