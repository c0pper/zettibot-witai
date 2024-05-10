from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import json



# load the document and split it into chunks
with open("intents.json", "r", encoding="utf8") as j:
    intents = json.loads(j.read())["intents"]

# Initialize the OpenAI embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
persist_directory = "vectorstore"
collection_name="zetti"

# Load the Chroma database from disk
chroma_db = Chroma(persist_directory=persist_directory, 
                   embedding_function=embeddings,
                   collection_name=collection_name)

collection = chroma_db.get()


if len(collection['ids']) == 0:
    documents = []
    for i in intents:
        tag = i["tag"]
        for r in i["responses"]:
            d = Document(page_content=r["it"], metadata={
                "intent": tag,
                "nap": r["nap"]
            })
            
            documents.append(d)
    # Create a new Chroma database from the documents
    chroma_db = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings, 
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    # Save the Chroma database to disk
    chroma_db.persist()

# query = "Brother fai i bucchini"

# print('Similarity search:')
# result = chroma_db.similarity_search(query, filter={"intent": "incazzo"})
# print([x.metadata["nap"] for x in result])

# # print('Similarity search with score:')
# result = chroma_db.similarity_search(query)
# print([x.metadata["nap"] for x in result])

# print("done")


# # create the open-source embedding function
# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# # load it into Chroma
# db = Chroma.from_documents(docs, embedding_function)

# # query it
# query = "What did the president say about Ketanji Brown Jackson"
# docs = db.similarity_search(query)

# # print results
# print(docs[0].page_content)