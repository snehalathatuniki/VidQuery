import os
from apikey import apikey

import streamlit as st
from langchain import OpenAI 
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma 
#from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import YoutubeLoader

os.environ["OPENAI_API_KEY"] = apikey 

def clear_history():
    if 'history' in st.session_state:
        del st.session_state['history']

st.title('Chat with Youtube')
youtube_url = st.text_input('Input your Youtube URL')

if youtube_url:
    with st.spinner('Reading, chunking and embedding file...'):
        
        loader = YoutubeLoader.from_youtube_url(youtube_url)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        #\n\n, \n, ' '

        chunks = text_splitter.split_documents(documents)    

        embeddings = OpenAIEmbeddings()

        vector_store = Chroma.from_documents(chunks, embeddings)

        #llm = OpenAI(temperature=0)
        llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=1)

        retriever=vector_store.as_retriever()

        #chain = RetrievalQA.from_chain_type(llm, retriever=retriever )
        crc = ConversationalRetrievalChain.from_llm(llm,retriever)
        st.session_state.crc = crc
        st.success('File uploaded, chunked and embedded successfully')

question = st.text_input('Input your question')

if question:
    if 'crc' in st.session_state:
        crc = st.session_state.crc
        if 'history' not in st.session_state:
            st.session_state['history'] = []

        response = crc.run({'question':question,'chat_history':st.session_state['history']})

        st.session_state['history'].append((question,response))
        st.write(response)

        #st.write(st.session_state['history'])
        for prompts in st.session_state['history']:
            st.write("Question: " + prompts[0])
            st.write("Answer: " + prompts[1])    
