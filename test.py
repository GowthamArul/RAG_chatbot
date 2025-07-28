from chat.document_index import build_index


if __name__ == "__main__":
    retriever = build_index()
    print("Index built and loaded successfully.")