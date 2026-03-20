import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate


def create_knowledge_base():
    loader = DirectoryLoader("data/manuals/", glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(texts)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print(embeddings)
    vectorstore = FAISS.from_documents(texts, embeddings)
    return vectorstore


def ask_digital_twin(question, vectorstore):
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

    prompt = ChatPromptTemplate.from_template(
        """
    Answer the user's question based ONLY on the following context:
    <context>
    {context}
    </context>
    
    Question: {input}
    """
    )

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectorstore.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke({"input": question})
    return response["answer"]


knowledge_base = create_knowledge_base()

q1 = input("User: ")
answer = ask_digital_twin(q1, knowledge_base)
print(answer)
