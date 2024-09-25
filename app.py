from flask import Flask,request
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.vectorstores import Chroma


app = Flask(__name__)

folder_path = "db"

cached_llm = Ollama(model="llama3")

embedding = FastEmbedEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
   chunk_size=1024,
   chunk_overlap=80,
   length_function=len,
   is_separator_regex=False 
)


@app.route("/ai",methods=["POST"])
def aiPost():
    print("Post ai called")
    json_content  = request.json
    query = json_content.get("query")

    print(f"query : {query}")

    response = cached_llm.invoke("Tell me a funny joke ? ")

    print(response)

    response_answer  =  {"answer": response}

    return response_answer

@app.route("/pdf",methods=["POST"])
def pdfPost():
    file = request.files("file")
    file_name = file.filename
    save_file =  "pdf/" + file_name
    file.save(save_file)
    print(f"filename: {file_name}")

    loader = PDFPlumberLoader(save_file)
    docs = loader.load_and_split()
    print(f"docs len={len(docs)}")

    chunks = text_splitter.split_documents(docs)
    print(f"chunks len= {len(chunks)}")

    vector_store = Chroma.from_documents(
        documents=chunks,embedding=embedding,persist_directory=folder_path
    )

    vector_store.persist()

    response = {"status": "Successfully uploaded",
                "filename":file_name,
                "doc_len":len(docs),
                "chunks":len(chunks),
                }
    return response



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8200,debug=True)
    