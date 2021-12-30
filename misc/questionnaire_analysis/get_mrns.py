"""This script converts bcrypt hashes of MRNs back into the original MRN.

You must supply a list of known MRNs.
"""
import csv
import queue
import threading

import bcrypt
"""
Args:
    hashed_mrns_q: Queue(bytes)
    all_mrns: list(bytes)

    result: Queue((bytes, bytes))
"""
def thread_safe_reverse_lookup(hashed_mrns_q, all_mrns, result_mrns_q):
    while not hashed_mrns_q.empty():
        hashed_mrn = hashed_mrns_q.get()
        for mrn in all_mrns:
            if bcrypt.checkpw(mrn, hashed_mrn):
                print(mrn.decode())
                result_mrns_q.put((hashed_mrn.decode(), mrn.decode()))
                break
        hashed_mrns_q.task_done()
    return True

def main():
    NUM_THREADS = 8

    all_mrns = []
    with open('/opt/spineai/files/luke_questionnaire.csv') as questionnaire:
        reader = csv.reader(questionnaire)
        headers = next(reader)
        for row in reader:
            all_mrns.append(bytes(row[7], 'utf-8'))

    hashed_mrns_q = queue.Queue()
    with open('/opt/spineai/files/Sam_MRN_Hashes_20200427.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            hashed_mrns_q.put(bytes(row[1], 'utf-8'))

    result_mrns_q = queue.Queue()
    threads = []
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=thread_safe_reverse_lookup, args=[hashed_mrns_q, all_mrns, result_mrns_q])
        thread.setDaemon(True)
        thread.start()
        threads.append(thread)

    hashed_mrns_q.join()

    with open('/opt/spineai/files/Sam_MRN_Hashes_20200427_MRNs.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for result in list(result_mrns_q.queue):
            writer.writerow(result)

if __name__ == "__main__":
    main()
