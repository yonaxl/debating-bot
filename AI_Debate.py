from openai import OpenAI
import os
import debate
import json
import time

os.environ["OPENAI_API_KEY"] = debate.my_key
client = OpenAI()

def main():
    # set dependencies
    topic = debate.topic
    prepend = "This is a debate competition so you need to take the opposing stance of the other contestant. Use your best knowledge, facts, statistics and examples to support your stance. Your main goal is to have your stance selected as the winning argument."

    #retrieve assistant
    cont_1 = client.beta.assistants.retrieve(debate.cont_1)
    cont_2 = client.beta.assistants.retrieve(debate.cont_2)
    referee = client.beta.assistants.retrieve(debate.referee)
    max_rounds = 3

    #start new threads
    thread1 = create_thread()
    thread2 = create_thread()
    
    # Initiate the topic
    write_message(thread1, topic, query_prepend="")
    write_message(thread2, topic, query_prepend="")
    with open("debate_transcription.txt", "w") as my_file:
        my_file.write("TOPIC : \n")
        my_file.write(topic + "\n \n")

    #get user query
    for i in range(max_rounds):
        # First Contestant 
        run = client.beta.threads.runs.create(
            thread_id=thread1.id,
            assistant_id=cont_1.id
        )
        wait_on_run(run, thread1)
        # obtain the response
        response = print_reply(get_response(thread1))

        #add to txt
        with open("debate_transcription.txt", "a") as my_file:
            my_file.write("Contestant 1 : \n")
            my_file.write(response + "\n \n")

        # Second Contestant
        write_message(thread2, response, prepend)
        run = client.beta.threads.runs.create(
            thread_id=thread2.id,
            assistant_id=cont_2.id
        )
        wait_on_run(run, thread2)
        # obtain the response
        response = print_reply(get_response(thread2))
        write_message(thread1, response, prepend)

        #add to txt
        with open("debate_transcription.txt", "a") as my_file:
            my_file.write("Contestant 2 : \n")
            my_file.write(response + "\n \n")

    # Delete the two threads
    client.beta.threads.delete(thread1.id)  
    client.beta.threads.delete(thread2.id)  

def show_json(obj):
    display(json.loads(obj.model_dump_json()))

def print_intro():
    print("NW_Assistant :")
    print("""How may I assist you with today? Type "Quit" anytime to exit the chat""")

def create_thread():
    thread = client.beta.threads.create()
    return thread

def write_message(thread, query, query_prepend):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query_prepend + " : " + query,
    )

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=1)

# Pretty printing helper
def print_reply(messages):
    for m in messages:
        toReturn = m.content[0].text.value
        break
    return str(toReturn)

if __name__ == '__main__':
    main()