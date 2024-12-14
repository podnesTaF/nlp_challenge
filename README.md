# 💬 Chatbot template

A simple Streamlit app that shows how to build a chatbot using OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   pip install -r requirements.txt
   ```

2. Run the app

   ```
   streamlit run streamlit_app.py
   ```

3. Add stt tts
4. Add PDF RAG for "Doc summarizer"
5. a Quiz (Exam) agent
6. Extra: Adding (short-term) memory to your chat conversation, so you can reference earlier
   topics from the same chat-session. You can further extend this with other types of
   memory, like long term (to really personalize the response based on previous
   interactions), entity, or even contextual memory

flow is the following:

1. We are embedding and storing files to chromadb after upload.

1. When we making a prompt the following happens:

- Retrieve the most relevant docs
- RAG search the relevant content
- summarize the content and write response
