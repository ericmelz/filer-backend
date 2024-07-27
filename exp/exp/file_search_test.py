from openai import AssistantEventHandler, OpenAI
import os


class EventHandler(AssistantEventHandler):
    def __init__(self, client):
        super().__init__()
        self.client = client

    # def on_text_created(self, text) -> None:
    #     print(f"\nassistant > ", end="", flush=True)

    # def on_tool_call_created(self, tool_call):
    #     print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f" [{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations) + '\n')


def test1():
    """
    See https://platform.openai.com/docs/assistants/tools/file-search
    :return:
    """
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    assistant = client.beta.assistants.create(
        name="Bank Statement Assistant",
        instructions="You are an AI assistant helping a user understand their bank statement.",
        model="gpt-4o",
        tools=[{"type": "file_search"}]
    )

    # Create a vector store for the bank statements
    vector_store = client.beta.vector_stores.create(name="Bank Statements")

    # Ready the files for upload to OpenAI
    # file_paths = ["/Users/ericmelz/Desktop/2024_01_31.pdf",
    #               "/Users/ericmelz/Desktop/2024_02_29.pdf",
    #               "/Users/ericmelz/Desktop/Invoice_INVJBA4729211.pdf",
    #               "/Users/ericmelz/Desktop/tree.txt"]

    ROOT_DIR = '/Users/ericmelz/Desktop/For Filing/SynologyDrive/'
    all_files = os.listdir(ROOT_DIR)
    file_paths = [os.path.join(ROOT_DIR, file) for file in all_files if file.endswith('.pdf')]

    file_streams = [open(path, "rb") for path in file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    # You can print the status and the file counts of the batch to see the result of this operation.
    # print(f'{file_batch.status=}')

    # Register the Vector store with the assistant
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    # Upload the user provided file to OpenAI
    # message_file = client.files.create(
    #     file=open("/Users/ericmelz/Desktop/2024_02_29.pdf", "rb"), purpose="assistants"
    # )

    threads = []

    query1 = "What was my qualification balance on February 29, 2024?"
    query2 = "What was my qualification balance on January 31, 2024?"
    # query3 = ("tree.txt contains a list of directories and files. Please suggest a folder to move "
    #           "the file 2024_02_29.pdf to.")
    # query4 = ("tree.txt contains a list of directories and files. Please suggest a folder to move "
    #           "the file Invoice_INVJBA4729211.pdf to.")
    # query5 = ("tree.txt contains a list of directories and files. Please suggest the most appropriate folder "
    #           "for the file 2024_02_29.pdf.")

    # queries = [query3, query4, query5]

    queries = [(f'tree.txt contains a list of directories and files. Please suggest the most appropriate f'
                f'folder for the file {file}') for file in file_paths]

    for query in queries:
        print(f'{query=}')

        # Create a thread and attach the file to the message
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                    # # Attach the new file to the message.
                    # "attachments": [
                    #     {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                    # ],
                }
            ]
        )

        # Just in case we need to access the thread later
        threads.append(thread)

        # The thread now has a vector store with that file in its tool resources.
        # print(f'{thread.tool_resources.file_search=}')

        # Use EventHandler class to create the Run
        # and stream the response.
        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                instructions="Please address the user as Eric Melz. The user has a premium account.",
                event_handler=EventHandler(client),
        ) as stream:
            stream.until_done()


if __name__ == '__main__':
    test1()
