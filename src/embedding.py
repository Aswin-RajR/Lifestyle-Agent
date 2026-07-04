from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader(
    "../data",
    glob="**/*.md",
    loader_cls=TextLoader,
)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(docs)

vectorstore = FAISS.from_documents(texts, embeddings)
vectorstore.save_local("vectorstores/my_faiss_index")