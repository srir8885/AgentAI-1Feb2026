import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

def create_sample_documents():
    documents = [
        Document(
            page_content="""
            Milo the Mouse: Milo the mouse found a shiny button in the park. He rolled it home like a treasure. A crow said, “That’s mine!” and looked sad. Milo asked, “Want to share it as a game prize?” They played button-toss all afternoon and laughed.
            """,
            metadata={"source": "langchain_intro", "topic": "overview"},
        ),
        Document(
            page_content="""
            Luna the Little Dragon: Luna the little dragon tried to breathe fire—puff! only bubbles came out. She felt embarrassed and hid behind a rock. A dirty puppy waddled up, covered in mud. Luna bubbled him clean like a bubbly bath. Everyone cheered: “You’re a helper dragon!”
            """,
            metadata={"source": "vector_stores", "topic": "technical"},
            # Luna the Little Dragon: Luna | the litt
            # n: Luna | the little dragon tried to breathe | 
        ),
        Document(
            page_content="""
            Nia and the Brave Umbrella: Nia carried a tiny yellow umbrella on a windy day. The wind whooshed and tried to steal it away. Nia held tight and said, “Not today, Wind!” She used it to shield a ladybug from the rain. The ladybug flew off safely, and Nia smiled big.
            """,
            metadata={"source": "embeddings", "topic": "technical"},
        )
    ]
    return documents


def demo_rag():
    
    llm = ChatOpenAI(
        temperature=0,
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )

    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    )

    documents = create_sample_documents()

    for doc in documents:
        topic = doc.metadata.get("topic", "unknown")
        preview = doc.page_content.strip()[:60] + "..."

        print(topic)
        print(preview)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    splits = text_splitter.split_documents(documents)

    print(splits)

    vectorstore = FAISS.from_documents(splits, embeddings)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    return retriever, llm


def demo_rag_chain(retriever, llm):

    template = """
    Answer the question based only on the following context:

    Context:
    {context}

    Question: {question}

    Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
       return "\n\n".join(doc.page_content for doc in docs)     

    rag_chain = (
        { "context": retriever | format_docs, "question": RunnablePassthrough() }
        | prompt
        | llm
        | StrOutputParser()

    )

    result = rag_chain.invoke("who is Milo?")

    print(result)



if __name__ == "__main__":
    retriever, llm = demo_rag()
    demo_rag_chain(retriever, llm)